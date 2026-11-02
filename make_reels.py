
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

# VIDEO SETTINGS
WIDTH = 1080
HEIGHT = 1920
FPS = 15
DURATION = 6

os.makedirs("reels", exist_ok=True)

# LOAD NEWS
with open("news.json", encoding="utf-8") as f:
    news = json.load(f)

if len(news) < 10:
    raise ValueError("At least 10 news items are required")

# FIND NEPALI FONT
font_files = (
    glob.glob("/usr/share/fonts/truetype/noto/*Devanagari*Bold*.ttf")
    + glob.glob("/usr/share/fonts/truetype/noto/*devanagari*bold*.ttf")
)

if not font_files:
    raise FileNotFoundError("Nepali font not found")

nepali_font = font_files[0]

# ENGLISH FONT
english_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# LOAD FONTS
headline_font = ImageFont.truetype(nepali_font, 62)
category_font = ImageFont.truetype(nepali_font, 42)
english_font_big = ImageFont.truetype(english_font, 42)
english_font_small = ImageFont.truetype(english_font, 34)

# CHECK MUSIC
if not os.path.exists("news_music.mp3"):
    raise FileNotFoundError("news_music.mp3 not found")

# FFMPEG
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

# CREATE REELS
for index, item in enumerate(news[:10], start=1):

    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    # HEADER
    draw.rectangle((0, 0, WIDTH, 210), fill="#c90020")
    draw.text(
        (65, 65),
        "SHORT KHABAR",
        font=english_font_big,
        fill="white"
    )

    # CATEGORY
    draw.text(
        (65, 330),
        item["category"],
        font=category_font,
        fill="#ffcc33"
    )

    # HEADLINE
    headline = item["title"]
    lines = textwrap.wrap(headline, width=22)

    y = 550

    for line in lines[:9]:
        draw.text(
            (65, y),
            line,
            font=headline_font,
            fill="white"
        )
        y += 105

    # FOOTER
    draw.rectangle((0, 1650, WIDTH, 1920), fill="#c90020")

    draw.text(
        (65, 1730),
        "FOLLOW FOR MORE UPDATES",
        font=english_font_small,
        fill="white"
    )

    # INSTAGRAM USERNAME
    draw.rounded_rectangle(
        (65, 1795, 650, 1890),
        radius=25,
        fill="#E1306C"
    )

    draw.text(
        (90, 1815),
        "@khabar.short",
        font=english_font_small,
        fill="white"
    )

    # VIDEO FRAME
    frame = np.array(image)

    filename = f"reels/news_{timestamp}_{index:02d}.mp4"
    temp_file = filename.replace(".mp4", "_silent.mp4")

    # CREATE VIDEO
    with imageio.get_writer(
        temp_file,
        fps=FPS,
        codec="libx264",
        macro_block_size=1
    ) as writer:

        for _ in range(FPS * DURATION):
            writer.append_data(frame)

    # ADD MUSIC
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

    # DELETE TEMP FILE
    os.remove(temp_file)

    print("Reel created:", filename)

print("SUCCESS: 10 Nepali Music Reels created!")
