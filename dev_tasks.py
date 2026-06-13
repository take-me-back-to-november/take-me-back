import subprocess


def format() -> None:
    raise SystemExit(subprocess.run(["ruff", "format", "src"]).returncode)


def lint() -> None:
    raise SystemExit(subprocess.run(["ruff", "check", "src"]).returncode)
