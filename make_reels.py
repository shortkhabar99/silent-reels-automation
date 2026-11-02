
import json
import os
import textwrap
import subprocess
import glob
import imageio_ffmpeg

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
import numpy as np

WIDTH = 1080
HEIGHT = 1920
FPS = 15
DURATION = 6

os.makedirs("reels", exist_ok=True)

with open("news.json", encoding="utf-8") as f:
    news = json.load(f)

if len(news) < 10:
    raise ValueError("At least 10 news items are required")

# Find Nepali Noto font
font_files = glob.glob(
    "/usr/share/fonts/truetype/noto/*Devanagari*Bold*.ttf"
)

if not font_files:
    raise FileNotFoundError(
        "Nepali Noto font not found. Check fonts-noto-core installation."
    )

font_path = font_files[0]

font = ImageFont.truetype(font_path, 62)
small = ImageFont.truetype(font_path, 42)

if not os.path.exists("news_music.mp3"):
    raise FileNotFoundError("news_music.mp3 not found")

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

for index, item in enumerate(news[:10], start=1):

    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 210), fill="#c90020")
    draw.text((65, 65), "SHORT KHABAR", font=small, fill="white")

    draw.text(
        (65, 330),
        item["category"],
        font=small,
        fill="#ffcc33"
    )

    headline = item["title"]
    lines = textwrap.wrap(headline, width=22)

    y = 550
    for line in lines[:9]:
        draw.text(
            (65, y),
            line,
            font=font,
            fill="white"
        )
        y += 105

    draw.rectangle((0, 1650, WIDTH, 1920), fill="#c90020")

    draw.text(
        (65, 1730),
        "FOLLOW FOR MORE UPDATES",
        font=small,
        fill="white"
    )

    draw.rounded_rectangle(
        (65, 1795, 650, 1890),
        radius=25,
        fill="#E1306C"
    )

    draw.text(
        (90, 1815),
        "@khabar.short",
        font=small,
        fill="white"
    )

    frame = np.array(image)

    filename = f"reels/news_{timestamp}_{index:02d}.mp4"
    temp_file = filename.replace(".mp4", "_silent.mp4")

    with imageio.get_writer(
        temp_file,
        fps=FPS,
        codec="libx264",
        macro_block_size=1
    ) as writer:

        for _ in range(FPS * DURATION):
            writer.append_data(frame)

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i", temp_file,
            "-stream_loop", "-1",
            "-i", "news_music.mp3",
            "-t", str(DURATION),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            filename
        ],
        check=True
    )

    os.remove(temp_file)

    print("Nepali Music Reel created:", filename)

print("SUCCESS: 10 Nepali Music Reels created!")
