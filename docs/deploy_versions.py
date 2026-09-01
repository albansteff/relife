"""Deploy the retained set of versioned docs via mike, run from a tag push.

Deploys any retained tag (see ``select_versions.py``) that isn't already
published, retires deployed versions that fell out of the retention window,
and keeps "latest" (the continuously-deployed ``main`` branch build) as the
site's default landing version.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from select_versions import has_zensical_config, list_version_tags, select_versions

CONFIG = "docs/zensical.toml"


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def deployed_versions() -> set[str]:
    result = subprocess.run(
        ["mike", "list", "-F", CONFIG, "-j"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()  # no gh-pages branch yet (first-ever deploy)
    return {entry["version"] for entry in json.loads(result.stdout or "[]")}


def deploy_tag(tag: str) -> None:
    worktree = Path(".worktrees") / tag
    run("git", "worktree", "add", "--detach", str(worktree), tag)
    try:
        run(
            "mike",
            "deploy",
            tag,
            "--push",
            "-F",
            str(worktree / "docs" / "zensical.toml"),
        )
    finally:
        run("git", "worktree", "remove", "--force", str(worktree))


def main() -> None:
    retained = {
        tag for tag in select_versions(list_version_tags()) if has_zensical_config(tag)
    }
    deployed = deployed_versions()

    for tag in sorted(retained - deployed):
        deploy_tag(tag)

    stale = deployed - retained - {"latest"}
    if stale:
        run("mike", "delete", *sorted(stale), "--push", "-F", CONFIG)

    run("mike", "set-default", "latest", "--push", "-F", CONFIG, "--allow-undefined")


if __name__ == "__main__":
    main()
