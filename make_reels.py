
import json
import os
import glob
import textwrap
import subprocess
import requests
import imageio_ffmpeg
import nepali_datetime
import numpy as np
import imageio.v2 as imageio

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

WIDTH = 1080
HEIGHT = 1920
FPS = 15
DURATION = 6

os.makedirs("reels", exist_ok=True)

with open("news.json", "r", encoding="utf-8") as f:
    news = json.load(f)

if not isinstance(news, list) or len(news) == 0:
    raise ValueError("news.json मा समाचार छैन।")

font_paths = [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
]

font_path = next((p for p in font_paths if os.path.exists(p)), None)

if not font_path:
    raise FileNotFoundError("Nepali font भेटिएन।")

title_font = ImageFont.truetype(font_path, 64)
small_font = ImageFont.truetype(font_path, 38)
brand_font = ImageFont.truetype(font_path, 42)

if not os.path.exists("news_music.mp3"):
    raise FileNotFoundError("news_music.mp3 भेटिएन।")

today = nepali_datetime.date.today()
nepali_date = today.strftime("%Y-%m-%d")

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

for index, item in enumerate(news[:10], start=1):
    print(f"Creating reel {index}/10")

    title = str(item.get("title", "आजको मुख्य समाचार"))
    description = str(item.get("description", ""))
    photo_url = item.get("image") or item.get("image_url") or item.get("photo")

    img = Image.new("RGB", (WIDTH, HEIGHT), (12, 20, 38))
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, WIDTH, 180), fill=(180, 0, 0))
    draw.text((55, 55), "SHORT KHABAR", font=brand_font, fill="white")

    photo = None
    if photo_url:
        try:
            response = requests.get(photo_url, timeout=20)
            response.raise_for_status()
            photo = Image.open(BytesIO(response.content)).convert("RGB")
            photo.thumbnail((980, 760))
        except Exception as e:
            print("Photo download failed:", e)

    if photo:
        x = (WIDTH - photo.width) // 2
        img.paste(photo, (x, 220))
        y = 1030
    else:
        y = 350

    draw = ImageDraw.Draw(img)

    def draw_wrapped(text, font, y_pos, max_chars, color):
        lines = textwrap.wrap(text, width=max_chars)
        for line in lines[:5]:
            draw.text((60, y_pos), line, font=font, fill=color)
            y_pos += font.size + 22
        return y_pos

    y = draw_wrapped(title, title_font, y, 23, "white")
    y += 25
    draw_wrapped(description, small_font, y, 38, (220, 220, 220))

    draw.rectangle((0, 1740, WIDTH, HEIGHT), fill=(180, 0, 0))
    draw.text((55, 1780), f"नेपाली मिति: {nepali_date}", font=small_font, fill="white")
    draw.text((55, 1840), "@khabar.short", font=brand_font, fill="white")

    image_path = f"/tmp/news_{index:02d}.png"
    video_path = f"reels/news_{index:02d}.mp4"

    img.save(image_path)

    subprocess.run([
        ffmpeg,
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", "news_music.mp3",
        "-t", str(DURATION),
        "-r", str(FPS),
        "-vf", f"scale={WIDTH}:{HEIGHT},format=yuv420p",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        "-movflags", "+faststart",
        video_path
    ], check=True)

    os.remove(image_path)

print("SUCCESS: Reels created:", len(glob.glob("reels/*.mp4")))
