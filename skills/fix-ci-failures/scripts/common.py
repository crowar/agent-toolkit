"""Shared helpers: .env bootstrap and HTTP access. Stdlib only."""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

PREFIX = "CIFIX_"
KEYS = [PREFIX + k for k in ("GITLAB_URL", "GITLAB_TOKEN", "SONAR_URL", "SONAR_TOKEN")]
HEADER = "# --- fix-ci-failures (не коммитить .env!) ---"
HINTS = {
    PREFIX + "GITLAB_URL": "# GitLab, например https://gitlab.example.com",
    PREFIX + "GITLAB_TOKEN": "# токен GitLab, scope api (чтение MR + ответы/resolve review threads)",
    PREFIX + "SONAR_URL": "# SonarQube, например https://sq.example.com",
    PREFIX + "SONAR_TOKEN": "# токен SonarQube (user/project analysis token)",
}


def repo_root():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return os.getcwd()


def ensure_gitignored(root):
    path = os.path.join(root, ".gitignore")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = []
    if ".env" not in [l.strip() for l in lines]:
        with open(path, "a", encoding="utf-8") as f:
            f.write(("\n" if lines and lines[-1] else "") + ".env\n")


def parse_env(path):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip("'\"")
    return env


def load_env(required=()):
    """Read config from os.environ and .env (environ wins). The .env is created or
    extended with missing CIFIX_* keys only when required values are unavailable.
    Exit(2) if required keys are empty."""
    root = repo_root()
    path = os.path.join(root, ".env")
    existed = os.path.exists(path)
    file_env = parse_env(path) if existed else {}
    env = {k: os.environ.get(k) or file_env.get(k, "") for k in KEYS}
    missing = [k for k in required if not env[k]]
    absent = [k for k in KEYS if k not in file_env]
    if absent and (missing or existed):
        with open(path, "a+", encoding="utf-8") as f:
            f.seek(0)
            content = f.read()
            if content and not content.endswith("\n"):
                f.write("\n")
            if content:
                f.write("\n")
            f.write(HEADER + "\n")
            for k in absent:
                f.write(f"{HINTS[k]}\n{k}=\n")
        if not existed:
            os.chmod(path, 0o600)
        ensure_gitignored(root)
        print(f"{'Обновлён' if existed else 'Создан'} {path}: добавлены {', '.join(absent)}.")
    if missing:
        print(f"Заполните в {path} (или задайте переменные окружения): {', '.join(missing)}")
        sys.exit(2)
    for k in (PREFIX + "GITLAB_URL", PREFIX + "SONAR_URL"):
        env[k] = env[k].rstrip("/")
    return {k[len(PREFIX):]: v for k, v in env.items()}


class ApiError(Exception):
    def __init__(self, status, url, reason):
        super().__init__(f"HTTP {status} for {url}: {reason}" if status else f"Network error for {url}: {reason}")
        self.status = status


def run(main):
    """Run a script entry point, turning ApiError into a clean exit."""
    try:
        main()
    except ApiError as e:
        sys.exit(str(e))


def http_request(url, headers, method="GET", body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    request_headers = dict(headers)
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    safe = url.split("?")[0]
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", "replace").strip()
        reason = f"{e.reason}: {err_body}" if err_body else e.reason
        raise ApiError(e.code, safe, reason) from None
    except urllib.error.URLError as e:
        raise ApiError(0, safe, e.reason) from None
    if not data:
        return None
    return data.decode("utf-8", "replace") if raw else json.loads(data)


def http_get(url, headers, raw=False):
    return http_request(url, headers, raw=raw)


def gitlab_request(env, path, method="GET", params=None, body=None):
    q = "?" + urllib.parse.urlencode(params) if params else ""
    return http_request(
        f"{env['GITLAB_URL']}/api/v4{path}{q}",
        {"PRIVATE-TOKEN": env["GITLAB_TOKEN"]},
        method=method,
        body=body,
    )


def gitlab_get(env, path, params=None, raw=False):
    q = "?" + urllib.parse.urlencode(params) if params else ""
    return http_get(
        f"{env['GITLAB_URL']}/api/v4{path}{q}", {"PRIVATE-TOKEN": env["GITLAB_TOKEN"]}, raw
    )


def sonar_get(env, path, params=None):
    q = "?" + urllib.parse.urlencode(params, doseq=True) if params else ""
    auth = base64.b64encode(f"{env['SONAR_TOKEN']}:".encode()).decode()
    return http_get(f"{env['SONAR_URL']}{path}{q}", {"Authorization": f"Basic {auth}"})
