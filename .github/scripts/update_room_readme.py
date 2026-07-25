"""Point the README's room banner at the selected checked-in preset."""

import os

import readme_block

REPO = os.environ.get("GITHUB_REPOSITORY", "Anionex/Anionex")
slot = os.environ["SLOT"]
if slot not in {"morning", "evening"}:
    raise SystemExit(f"unknown slot: {slot}")

url = f"https://raw.githubusercontent.com/{REPO}/main/assets/room/{slot}.webp"
readme_block.replace("ROOM", f'<img src="{url}" width="100%" alt="{slot}" />')
print(f"README -> {slot}")
