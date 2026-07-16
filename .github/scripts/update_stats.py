"""Refresh the stats/rank badges in README.md between the <!-- STATS --> markers."""

import json
import os
import re
import urllib.request

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount }
    }
  }
}
"""


def fetch(url, headers=None, data=None):
    req = urllib.request.Request(url, headers=headers or {}, data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_stats():
    stars, cursor = 0, None
    while True:
        body = json.dumps({"query": QUERY, "variables": {"login": USER, "cursor": cursor}})
        payload = json.loads(fetch(
            "https://api.github.com/graphql",
            headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
            data=body.encode("utf-8"),
        ))
        if "errors" in payload:
            raise RuntimeError(payload["errors"])
        user = payload["data"]["user"]
        repos = user["repositories"]
        stars += sum(n["stargazerCount"] for n in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            return stars, user["followers"]["totalCount"], repos["totalCount"]
        cursor = repos["pageInfo"]["endCursor"]


def fetch_rank():
    """Global star rank from gitstar-ranking. Returns None so a failed scrape keeps the old value."""
    try:
        html = fetch(f"https://gitstar-ranking.com/{USER}", headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        print(f"rank scrape failed: {e}")
        return None
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", html))
    m = re.search(r"Rank (\d+)", text)
    return m.group(1) if m else None


def fmt(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def replace_block(content, marker, body):
    return re.sub(
        rf"<!-- {marker}-START -->.*?<!-- {marker}-END -->",
        f"<!-- {marker}-START -->\n{body}\n<!-- {marker}-END -->",
        content,
        flags=re.DOTALL,
    )


stars, followers, repos = fetch_stats()
rank = fetch_rank()
print(f"stars={stars} followers={followers} repos={repos} rank={rank or 'scrape failed'}")

with open("README.md", encoding="utf-8") as f:
    content = f.read()

if rank is None:
    m = re.search(r"Global%20Star%20Rank-%23([0-9]+)-", content)
    rank = m.group(1) if m else None

if rank:
    content = replace_block(
        content,
        "RANK",
        f"[![Global Star Rank](https://img.shields.io/badge/Global%20Star%20Rank-%23{rank}-2F81F7?style=flat&logo=github&logoColor=white)](https://gitstar-ranking.com/{USER})",
    )

content = replace_block(
    content,
    "STATS",
    "\n".join([
        f"[![Total Stars](https://img.shields.io/badge/Total%20Stars-{fmt(stars)}-D29922?style=flat&logo=github&logoColor=white)](https://github.com/{USER})",
        f"[![Followers](https://img.shields.io/badge/Followers-{fmt(followers)}-238636?style=flat&logo=github&logoColor=white)](https://github.com/{USER}?tab=followers)",
        f"[![Public Repos](https://img.shields.io/badge/Public%20Repos-{repos}-57606A?style=flat&logo=github&logoColor=white)](https://github.com/{USER}?tab=repositories)",
    ]),
)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)
