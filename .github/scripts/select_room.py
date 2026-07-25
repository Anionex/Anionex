"""Select a checked-in room preset for the current Beijing time."""

import datetime as dt
import os

PRESETS = {
    "morning": "assets/room/morning.webp",
    "evening": "assets/room/evening.webp",
}


def current_slot():
    """Use the morning preset before 16:00 Beijing time, evening otherwise."""
    hour = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=8)).hour
    if 5 <= hour < 16:
        return "morning"
    return "evening"


slot = os.environ.get("SLOT") or current_slot()
if slot not in PRESETS:
    raise SystemExit(f"unknown slot: {slot}")

if not os.path.isfile(PRESETS[slot]):
    raise SystemExit(f"missing preset: {PRESETS[slot]}")

print(f"slot={slot} preset={PRESETS[slot]}")

if out := os.environ.get("GITHUB_OUTPUT"):
    with open(out, "a", encoding="utf-8") as f:
        f.write(f"slot={slot}\n")
