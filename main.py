#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The World in One Day -- runner for make.fun news-image-20261121.

The entry is the editorial poster ``entry.png`` shipped beside this file:
a single image summing up the world news of Saturday 21 November 2026.
This program is the deterministic runner. It loads the poster, rejects it
unless it is a PNG inside the 1 MiB / 1024 px limits, writes the exact
same bytes to ``entry.png`` in the grader's output directory, and checks
the copy with a SHA-256 comparison before printing a fixed log of the
stories the poster carries. Standard library only; no network, no clock,
no randomness, so two runs write identical bytes and print identical text.
"""

import hashlib
import os
import struct
import sys

SLUG = "news-image-20261121"
DAY = "2026-11-21"
POSTER_FILE = "entry.png"
PNG_HEADER = b"\x89PNG\r\n\x1a\n"
LIMIT_BYTES = 1048576
LIMIT_SIDE = 1024

# The stories on the poster, in the order they appear on the page.
HEADLINES = [
    ("Poland", "Two Russian missiles and a suspected drone come down on Polish soil"),
    ("The Hague", "World Court rules Myanmar committed genocide against the Rohingya"),
    ("Wall Street", "US shares fall about 3.7%; the S&P 500 enters correction"),
    ("Odisha", "Cyclone Akvan weakens after crossing the Odisha coast"),
    ("Brussels", "UK and EU sign post-Brexit deals on trade, carbon and youth mobility"),
]


def read_validated_poster():
    """Load the poster bytes, exiting non-zero if they fail any check."""
    folder = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(folder, POSTER_FILE)
    try:
        with open(path, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        print("cannot read poster: %s" % exc, file=sys.stderr)
        sys.exit(1)
    if not blob.startswith(PNG_HEADER):
        print("poster is not a PNG file", file=sys.stderr)
        sys.exit(1)
    if len(blob) > LIMIT_BYTES:
        print("poster over 1 MiB: %d bytes" % len(blob), file=sys.stderr)
        sys.exit(1)
    width, height = struct.unpack(">II", blob[16:24])
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        print("poster over 1024 px: %dx%d" % (width, height), file=sys.stderr)
        sys.exit(1)
    return blob


def target_path():
    """Where the grader wants the image: $MAKEFUN_OUTPUT_DIR, else /output."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, POSTER_FILE)


def run():
    blob = read_validated_poster()
    dest = target_path()
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "wb") as handle:
        handle.write(blob)
    with open(dest, "rb") as handle:
        copied = handle.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(blob).hexdigest():
        print("output copy differs from poster: %s" % dest, file=sys.stderr)
        sys.exit(1)
    print("The World in One Day -- %s" % DAY)
    for city, line in HEADLINES:
        print("%s: %s" % (city, line))
    print("wrote %s (%d bytes, sha256 %s)" % (dest, len(blob), hashlib.sha256(blob).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(run())
