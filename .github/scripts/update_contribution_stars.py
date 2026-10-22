"""Refresh contribution star counts and sort projects by stars, highest first."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import re
import urllib.request

import readme_block

README = Path(__file__).resolve().parents[2] / "README.md"
BLOCK = re.compile(r"<!-- CONTRIBUTIONS-START -->\n(.*?)\n<!-- CONTRIBUTIONS-END -->", re.S)
PROJECT = re.compile(
    r"^(\* \[[^\]]+\]\(https://github\.com/([^/\s]+/[^/)\s]+)/?\))"
    r"(?: \(([\d.]+)(k?)⭐\))?( — .+)?$"
)


def format_stars(count):
    if type(count) is not int or count < 0:
        raise ValueError("invalid stargazers_count")
    if count < 1000:
        return str(count)
    return f"{count / 1000:.1f}".rstrip("0").rstrip(".") + "k"


def update_project(line):
    match = PROJECT.fullmatch(line)
    if not match:
        return -1, line
    link, repo, previous, unit, description = match.groups()
    previous_count = float(previous) * (1000 if unit else 1) if previous else -1
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Anionex-profile"}
    if token := os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    try:
        request = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            count = json.load(response)["stargazers_count"]
            stars = format_stars(count)
    except Exception as error:
        print(f"{repo}: keeping existing count ({type(error).__name__})")
        return previous_count, line
    print(f"{repo}: {stars} stars")
    return count, f"{link} ({stars}⭐){description or ''}"


def main():
    content = README.read_text(encoding="utf-8")
    match = BLOCK.search(content)
    if not match:
        raise SystemExit("Missing CONTRIBUTIONS markers in README.md")
    with ThreadPoolExecutor(max_workers=5) as pool:
        projects = list(pool.map(update_project, match.group(1).splitlines()))
    projects.sort(key=lambda project: project[0], reverse=True)
    body = "\n".join(line for _, line in projects)
    readme_block.replace("CONTRIBUTIONS", body, path=README)


if __name__ == "__main__":
    main()
