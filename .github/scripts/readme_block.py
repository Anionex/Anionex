"""Rewrite the region between a pair of <!-- MARKER-START/END --> comments in README.md."""

import re


def replace(marker, body, path="README.md"):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # A lambda, not a replacement string: bodies are URLs and would otherwise
    # have their backslash/group syntax interpreted by re.sub.
    updated = re.sub(
        rf"<!-- {marker}-START -->.*?<!-- {marker}-END -->",
        lambda _: f"<!-- {marker}-START -->\n{body}\n<!-- {marker}-END -->",
        content,
        flags=re.DOTALL,
    )
    if updated == content:
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True
