import re
import sys
from pathlib import Path

COMMIT_MESSAGE_PATTERN = re.compile(
    r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
    r"(\([a-z0-9._-]+\))?(!)?: .+"
)


def main() -> int:
    commit_msg_path = Path(sys.argv[1])
    subject = commit_msg_path.read_text(encoding="utf-8").splitlines()[0].strip()

    if COMMIT_MESSAGE_PATTERN.match(subject):
        return 0

    print(
        "Commit message must follow Conventional Commits, for example:\n"
        "  feat(auth): add Spotify login\n"
        "  fix: refresh expired Spotify token\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
