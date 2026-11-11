#!/usr/bin/env python3
"""List unresolved GitLab MR review threads, or reply and resolve one after fixing it.

Usage:
  review_comments.py --mr IID
  review_comments.py --mr IID --reply DISCUSSION_ID --message "Исправлено: ... Проверки: ..."
"""
import argparse
import urllib.parse

from common import gitlab_request, load_env, run
from gitlab_mr import project_path


def discussions(env, project, iid):
    page = 1
    result = []
    while True:
        batch = gitlab_request(
            env,
            f"/projects/{project}/merge_requests/{iid}/discussions",
            params={"per_page": 100, "page": page},
        )
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mr", type=int, required=True, help="GitLab merge request IID")
    parser.add_argument("--reply", metavar="DISCUSSION_ID", help="reply to and resolve this discussion")
    parser.add_argument("--message", help="reply text describing the fix and verification")
    args = parser.parse_args()
    if bool(args.reply) != bool(args.message):
        parser.error("--reply and --message must be supplied together")

    env = load_env(["CIFIX_GITLAB_URL", "CIFIX_GITLAB_TOKEN"])
    project = urllib.parse.quote(project_path(env), safe="")
    threads = discussions(env, project, args.mr)
    unresolved = [
        d
        for d in threads
        if any(n.get("resolvable") and not n.get("resolved") for n in d.get("notes", []))
    ]

    if not args.reply:
        if not unresolved:
            print(f"У MR !{args.mr} нет незакрытых review threads.")
            return
        for d in unresolved:
            notes = d.get("notes", [])
            first = next((n for n in notes if not n.get("system")), notes[0] if notes else {})
            position = first.get("position") or {}
            location = position.get("new_path") or position.get("old_path") or "общий комментарий"
            line = position.get("new_line") or position.get("old_line")
            print(f"DISCUSSION_ID={d['id']} | {location}{':' + str(line) if line else ''}")
            for note in notes:
                if not note.get("system"):
                    author = (note.get("author") or {}).get("username", "unknown")
                    print(f"  @{author}: {note.get('body', '').strip()}")
        return

    target = next((d for d in unresolved if d.get("id") == args.reply), None)
    if target is None:
        raise SystemExit(f"Незакрытый discussion {args.reply!r} не найден для MR !{args.mr}.")
    if target.get("individual_note"):
        raise SystemExit("Нельзя закрыть individual note через discussion API.")

    gitlab_request(
        env,
        f"/projects/{project}/merge_requests/{args.mr}/discussions/{urllib.parse.quote(args.reply, safe='')}/notes",
        method="POST",
        body={"body": args.message},
    )
    gitlab_request(
        env,
        f"/projects/{project}/merge_requests/{args.mr}/discussions/{urllib.parse.quote(args.reply, safe='')}",
        method="PUT",
        params={"resolved": "true"},
    )
    print(f"Ответ добавлен, discussion {args.reply} закрыт в MR !{args.mr}.")


if __name__ == "__main__":
    run(main)
