"""Generate the pixel-art room scene for the current time of day (Seedream / Volcengine Ark).

Slot is picked from Beijing time unless SLOT is set. Writes room.png in the CWD.
"""

import base64
import datetime as dt
import json
import os
import urllib.request

API = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
MODEL = "doubao-seedream-4-5-251128"
AVATAR = "https://avatars.githubusercontent.com/u/123177548?v=4"

# 房间本身在三个时段完全一致，只有光线和氛围变化。
SCENE = (
    "16:9像素风格画。一间温暖的卧室从天花板往下斜拍的图片，右边是透光的窗户。"
    "卧室主人是程序员坐在电脑屏幕前，形象如参考图所示，穿蓝色带兜帽卫衣，黑色长裤，"
    "看着屏幕，侧身面对画面。桌上有苹果显示器和macbook。房间里有咖啡机，midi琴键等，"
    "桌搭十分精致；墙角有一把长号。"
)

LIGHTING = {
    "morning": (
        "窗外的蓝天和树木清晰可见，阳光明媚。清晨的阳光斜射进房间，在地板上投下明亮的光斑。"
        "整体色调明亮温暖，透露出有序和积极的氛围。"
    ),
    "evening": (
        "窗外是橙金色的晚霞，树木被夕阳染成暖色。低角度的夕阳射入房间，在墙上拉出长长的橙色光影。"
        "整体色调温暖偏金，透露出松弛而专注的氛围。"
    ),
    "night": (
        "窗外是深蓝色的夜空，点点星光，远处有零星灯火。房间里只有显示器的冷蓝光和桌上一盏暖黄台灯，"
        "光影对比强烈。整体色调深邃安静，透露出沉浸和专注的氛围。"
    ),
}


def current_slot():
    """早晨 / 傍晚 / 晚上 by Beijing time — the boundaries the cron fires around."""
    hour = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=8)).hour
    if 5 <= hour < 16:
        return "morning"
    if 16 <= hour < 20:
        return "evening"
    return "night"


slot = os.environ.get("SLOT") or current_slot()
if slot not in LIGHTING:
    raise SystemExit(f"unknown slot: {slot}")

with urllib.request.urlopen(AVATAR, timeout=30) as r:
    avatar = base64.b64encode(r.read()).decode()

body = {
    "model": MODEL,
    "prompt": SCENE + LIGHTING[slot],
    "image": f"data:image/png;base64,{avatar}",
    # Ark rejects anything under 3,686,400 px; 2560x1440 is the smallest 16:9 that clears it.
    "size": "2560x1440",
    "response_format": "url",
    "watermark": False,
}

req = urllib.request.Request(
    API,
    data=json.dumps(body).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['DOUBAO_API_KEY']}",
        "Content-Type": "application/json",
    },
)
with urllib.request.urlopen(req, timeout=300) as r:
    payload = json.loads(r.read())

urllib.request.urlretrieve(payload["data"][0]["url"], "room.png")
print(f"slot={slot} bytes={os.path.getsize('room.png')} usage={payload.get('usage')}")

if out := os.environ.get("GITHUB_OUTPUT"):
    with open(out, "a") as f:
        f.write(f"slot={slot}\n")

# Downscaling is deliberately skipped: LANCZOS smears the flat pixel-art palette and
# actually triples the PNG (705KB -> 2MB). The native 2560x1440 is the smaller file.
