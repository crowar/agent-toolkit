#!/usr/bin/env python3
"""Print SonarQube quality gate failures, issues and hotspots for a scan URL.

Usage: sonar_issues.py "https://sonar/dashboard?id=KEY&pullRequest=154"
       (also supports &branch=NAME; without either - the main branch)
"""
import sys
import urllib.parse

from common import ApiError, load_env, run, sonar_get


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    u = urllib.parse.urlparse(sys.argv[1])
    q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
    if "id" not in q:
        sys.exit("В ссылке нет параметра id=")
    env = load_env(["CIFIX_SONAR_URL", "CIFIX_SONAR_TOKEN"])
    cfg = urllib.parse.urlparse(env["SONAR_URL"])
    if (u.hostname or "").lower() != (cfg.hostname or "").lower() or (u.port or 0) != (cfg.port or 0):
        print(f"WARN: хост ссылки ({u.netloc}) отличается от SONAR_URL; токен отправляется на SONAR_URL")
    scope = {k: q[k] for k in ("pullRequest", "branch") if k in q}
    key = q["id"]

    gate = sonar_get(env, "/api/qualitygates/project_status", {"projectKey": key, **scope})
    ps = gate["projectStatus"]
    print(f"QUALITY GATE: {ps['status']}")
    for c in ps.get("conditions", []):
        if c["status"] != "OK":
            print(f"  ✗ {c['metricKey']}: actual={c.get('actualValue')} {c.get('comparator')} "
                  f"threshold={c.get('errorThreshold')}")

    page, total = 1, 0
    while True:
        r = sonar_get(env, "/api/issues/search", {
            "componentKeys": key, **scope, "resolved": "false", "ps": 500, "p": page,
            **({} if "pullRequest" in scope else {"inNewCodePeriod": "true"}),
        })
        if page == 1:
            print(f"\nISSUES: {r['paging']['total']}")
        for i in r["issues"]:
            comp = i["component"].split(":", 1)[-1]
            print(f"[{i['severity']}/{i['type']}] {comp}:{i.get('line', '?')} "
                  f"{i['rule']} — {i['message']}")
        total += len(r["issues"])
        if total >= r["paging"]["total"] or not r["issues"]:
            break
        page += 1

    try:
        h = sonar_get(env, "/api/hotspots/search", {"projectKey": key, **scope, "status": "TO_REVIEW", "ps": 500})
        print(f"\nSECURITY HOTSPOTS (to review): {h['paging']['total']}")
        for x in h["hotspots"]:
            print(f"[{x['vulnerabilityProbability']}] {x['component'].split(':', 1)[-1]}:"
                  f"{x.get('line', '?')} {x['ruleKey']} — {x['message']}")
    except ApiError as e:
        print("hotspots недоступны:", e)

    # Coverage / duplication on new code (gate failures are often these).
    m = sonar_get(env, "/api/measures/component", {
        "component": key, **scope,
        "metricKeys": "new_coverage,new_duplicated_lines_density,new_uncovered_lines,new_lines_to_cover",
    })
    print("\nNEW-CODE METRICS:", {x["metric"]: (x.get("period") or x).get("value") for x in m["component"]["measures"]})
    print("Покрытие по файлам: /api/measures/component_tree (metricKeys=new_uncovered_lines) при необходимости.")


if __name__ == "__main__":
    run(main)
