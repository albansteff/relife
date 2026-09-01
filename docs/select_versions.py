"""Select which git tags should have published documentation versions.

Keeps the latest patch release of the last ``N_VERSIONS`` minor-version
families. Tags predate the Zensical migration and never had a
``docs/zensical.toml`` are skipped, since there is no way to build their docs
with the current toolchain without misrepresenting their content with
present-day pages.
"""

from __future__ import annotations

import re
import subprocess

N_VERSIONS = 3
TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def list_version_tags() -> list[str]:
    output = subprocess.run(
        ["git", "tag", "--list", "v*"], capture_output=True, text=True, check=True
    ).stdout
    return [tag for tag in output.splitlines() if TAG_RE.match(tag)]


def has_zensical_config(tag: str) -> bool:
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{tag}:docs/zensical.toml"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def select_versions(tags: list[str], n_versions: int = N_VERSIONS) -> list[str]:
    by_minor: dict[tuple[int, int], tuple[int, str]] = {}
    for tag in tags:
        major, minor, patch = (int(x) for x in TAG_RE.match(tag).groups())
        key = (major, minor)
        if key not in by_minor or patch > by_minor[key][0]:
            by_minor[key] = (patch, tag)
    families = sorted(by_minor)[-n_versions:]
    return [by_minor[key][1] for key in families]


if __name__ == "__main__":
    for tag in select_versions(list_version_tags()):
        if has_zensical_config(tag):
            print(tag)
