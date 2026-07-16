"""Point the README's room banner at the freshly pushed image."""

import os

import readme_block

REPO = os.environ.get("GITHUB_REPOSITORY", "Anionex/Anionex")
slot = os.environ["SLOT"]
# GitHub's camo proxy caches by URL, so a stable URL would keep serving the old
# scene forever. The changing ?v= is what actually makes the refresh visible.
version = os.environ["VERSION"]

url = f"https://raw.githubusercontent.com/{REPO}/profile-assets/room.png?v={version}"
readme_block.replace("ROOM", f'<img src="{url}" width="100%" alt="{slot}" />')
print(f"README -> {slot} ({version})")
