"""Refresh the global star rank badge in README.md between the <!-- RANK --> markers."""

import os
import re
import urllib.request

import readme_block

USER = os.environ["GH_USER"]


def fetch_rank():
    """Global star rank from gitstar-ranking, or None if it can't be read."""
    try:
        req = urllib.request.Request(
            f"https://gitstar-ranking.com/{USER}", headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"rank scrape failed: {e}")
        return None
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", html))
    m = re.search(r"Rank (\d+)", text)
    return m.group(1) if m else None


rank = fetch_rank()
if not rank:
    print("leaving the existing badge alone")
    raise SystemExit(0)

print(f"rank={rank}")
badge = (
    f"[![Global Star Rank](https://img.shields.io/badge/Global%20Star%20Rank-%23{rank}"
    f"-2F81F7?style=flat&logo=github&logoColor=white)](https://gitstar-ranking.com/{USER})"
)

readme_block.replace("RANK", badge)
