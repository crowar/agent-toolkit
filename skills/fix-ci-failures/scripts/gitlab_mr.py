#!/usr/bin/env python3
"""Find the GitLab MR for the current (or given) branch and print failed CI jobs.

Usage: gitlab_mr.py [--branch NAME] [--tail 150] [--mr IID]
"""
import argparse
import re
import subprocess
import urllib.parse

from common import gitlab_get, load_env, run

SONAR_RE = re.compile(r"https?://\S+/dashboard\?\S*?id=\S+")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]|\r")
ERR_RE = re.compile(
    r"(ERROR|FAIL|FAILED|Exception|error:|AssertionError|BUILD FAILURE|"
    r"QUALITY GATE|Tests run:.*(Failures|Errors): [1-9])",
)


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def project_path(env):
    """Derive 'group/sub/project' from origin (https, ssh://, scp-like), minus GITLAB_URL's path prefix."""
    url = git("remote", "get-url", "origin")
    base = urllib.parse.urlparse(env["GITLAB_URL"])
    host = (base.hostname or "").lower()
    m = re.match(r"^(?:[^@/\s]+@)?([^:/\s]+):(?!\d+/)(.+)$", url)  # scp-like
    if m and "://" not in url:
        rhost, path = m.group(1), m.group(2)
    else:
        u = urllib.parse.urlparse(url)
        rhost, path = u.hostname or "", u.path
    if rhost.lower() != host:
        raise SystemExit(f"origin ({url}) не соответствует CIFIX_GITLAB_URL ({env['GITLAB_URL']})")
    path = "/" + path.strip("/")
    prefix = base.path.rstrip("/")
    if prefix and path.startswith(prefix + "/"):
        path = path[len(prefix):]
    path = re.sub(r"\.git$", "", path.strip("/"))
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch")
    ap.add_argument("--mr", type=int)
    ap.add_argument("--tail", type=int, default=150, help="trace lines kept per job")
    a = ap.parse_args()
    env = load_env(["CIFIX_GITLAB_URL", "CIFIX_GITLAB_TOKEN"])
    pid = urllib.parse.quote(project_path(env), safe="")
    branch = a.branch or git("rev-parse", "--abbrev-ref", "HEAD")

    if a.mr:
        mr = gitlab_get(env, f"/projects/{pid}/merge_requests/{a.mr}")
    else:
        mrs = gitlab_get(
            env,
            f"/projects/{pid}/merge_requests",
            {"source_branch": branch, "order_by": "updated_at", "per_page": 5},
        )
        mrs.sort(key=lambda m: m["state"] != "opened")
        if not mrs:
            raise SystemExit(f"MR для ветки '{branch}' не найден. Запушена ли ветка / создан ли MR?")
        mr = mrs[0]
    print(f"MR !{mr['iid']} [{mr['state']}] {mr['title']}\n{mr['web_url']}")

    pipe = mr.get("head_pipeline") or mr.get("pipeline")
    if not pipe:
        pls = gitlab_get(env, f"/projects/{pid}/merge_requests/{mr['iid']}/pipelines")
        pipe = pls[0] if pls else None
    if not pipe:
        raise SystemExit("У MR нет пайплайнов")
    print(f"Pipeline #{pipe['id']} status={pipe['status']} {pipe['web_url']}\n")

    jobs = gitlab_get(env, f"/projects/{pid}/pipelines/{pipe['id']}/jobs", {"per_page": 100})
    failed = [j for j in jobs if j["status"] == "failed"]
    if not failed:
        print("Упавших jobs нет:", {j["name"]: j["status"] for j in jobs})
        return
    sonar_urls = set()
    for j in failed:
        trace = ANSI_RE.sub("", gitlab_get(env, f"/projects/{pid}/jobs/{j['id']}/trace", raw=True))
        lines = trace.splitlines()
        sonar_urls.update(u.rstrip(".,)") for u in SONAR_RE.findall(trace))
        print(f"=== FAILED job: {j['name']} (stage {j['stage']}, #{j['id']}) {j['web_url']}")
        hits = [l for l in lines if ERR_RE.search(l)][:40]
        print("--- ключевые строки:")
        print("\n".join(hits) or "(нет)")
        print(f"--- последние {a.tail} строк:")
        print("\n".join(lines[-a.tail:] if a.tail > 0 else []), "\n")
    if sonar_urls:
        print("SONAR_LINKS:", *sorted(sonar_urls), sep="\n  ")
        print("Далее: python sonar_issues.py <ссылка>")


if __name__ == "__main__":
    run(main)
