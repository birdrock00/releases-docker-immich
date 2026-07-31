#!/usr/bin/env python3
"""Reapplies this fork's README notice on top of whatever upstream ships.

Run after every upstream merge (see .github/workflows/sync-upstream.yaml).
Unlike the rest of this repo, README.md is an upstream-owned file that this
fork also edits (to add the notice below), so a merge can genuinely conflict
here if imagegenius ever touches the same lines. This script re-derives the
notice from scratch each run rather than relying on the merge to preserve it,
so the notice survives even a resolved conflict.
"""
import re
import sys

README_PATH = "README.md"
FORK = "birdrock00/releases-docker-immich"
UPSTREAM = "imagegenius/docker-immich"
IMMICH_UPSTREAM = "immich-app/immich"
RELEASE_NOTES_ISSUE = "https://github.com/imagegenius/docker-immich/issues/712"

FORK_NOTICE = f"""<!-- FORK-NOTICE:START -->
> **This is [{FORK}](https://github.com/{FORK})**, a fork of [{UPSTREAM}](https://github.com/{UPSTREAM}).
> A GitHub Action ([sync-upstream.yaml](.github/workflows/sync-upstream.yaml)) merges every upstream commit into this fork every 2 weeks, so the build pipeline and image contents track imagegenius's own release exactly.
> Separately, this fork guarantees GitHub Releases stay populated: imagegenius stopped publishing release notes on GitHub (only rolling image tags since 2026-05-18), and a request to link the upstream Immich changelog when bumping versions was raised in [{UPSTREAM}#712]({RELEASE_NOTES_ISSUE}) and closed without being addressed. So [immich-release-notes.yaml](.github/workflows/immich-release-notes.yaml) fires after every successful build and publishes a matching GitHub Release here -- with the real upstream [{IMMICH_UPSTREAM}](https://github.com/{IMMICH_UPSTREAM}) release notes for that pinned Immich version -- so `ghcr.io/birdrock00/immich` always has an accurate changelog, unlike the upstream repo it forks from.
<!-- FORK-NOTICE:END -->
"""


# The image itself is still published as `immich` (upstream's own naming,
# unrelated to this repo's name) but under this fork's owner, not
# imagegenius's -- so pull/image-tag examples should point at the image
# this fork actually publishes, not the upstream one.
IMAGE_REF = re.compile(r"ghcr\.io/imagegenius/immich\b")


def strip_existing_notice(text: str) -> str:
    return re.sub(
        r"<!-- FORK-NOTICE:START -->.*?<!-- FORK-NOTICE:END -->\n*",
        "",
        text,
        flags=re.DOTALL,
    )


def main() -> int:
    with open(README_PATH, encoding="utf-8") as f:
        text = f.read()

    text = strip_existing_notice(text)
    text = IMAGE_REF.sub("ghcr.io/birdrock00/immich", text)

    # Insert right after the first line (upstream's title line), or at the
    # top if the README was restructured so there's no clear first line.
    first_newline = text.find("\n")
    if first_newline == -1:
        text = FORK_NOTICE + "\n" + text
    else:
        insert_at = first_newline + 1
        rest = text[insert_at:].lstrip("\n")
        text = text[:insert_at] + "\n" + FORK_NOTICE + "\n" + rest

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
