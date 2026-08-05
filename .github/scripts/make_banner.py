"""Crop the full room scene into a wide 5:1 hero banner.

The full art stays the canonical source in assets/room/{slot}.webp; the
derived {slot}-banner.webp is what the profile actually shows, so the
intro text sits above the fold. The crop starts ~32% down the frame,
which keeps the skylight, desk, person and monitors while skipping the
bed at the bottom.
"""

import argparse
import os

from PIL import Image

RATIO = 5          # width : height of the banner
BAND_OFFSET = 0.32  # start the crop this far down the full frame

PRESETS = ["morning", "evening"]


def make_banner(slot: str) -> str:
    src = f"assets/room/{slot}.webp"
    dst = f"assets/room/{slot}-banner.webp"
    if not os.path.isfile(src):
        raise SystemExit(f"missing source: {src}")
    with Image.open(src) as img:
        width, height = img.size
        banner_h = round(width / RATIO)
        y1 = min(round(height * BAND_OFFSET), height - banner_h)
        img.crop((0, y1, width, y1 + banner_h)).save(dst, "webp", quality=85, method=6)
    return dst


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--both", action="store_true", help="regenerate both presets")
    parser.add_argument("slots", nargs="*", choices=PRESETS)
    args = parser.parse_args()
    slots = PRESETS if args.both else args.slots
    if not slots:
        parser.error("pass a slot (morning|evening) or --both")
    for slot in slots:
        print(f"banner {slot} -> {make_banner(slot)}")


if __name__ == "__main__":
    main()
