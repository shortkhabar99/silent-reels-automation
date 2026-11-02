import json
import os
import textwrap
import subprocess
import imageio_ffmpeg

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
import numpy as np

# Video settings
WIDTH = 1080
HEIGHT = 1920
FPS = 15
DURATION = 6

# Create reels folder
os.makedirs("reels", exist_ok=True)

# Load news
with open("news.json", encoding="utf-8") as f:
    news = json.load(f)

if len(news) < 10:
    raise ValueError("At least 10 news items are required")

# Check music file
if not os.path.exists("news_music.mp3"):
    raise FileNotFoundError("news_music.mp3 not found")

# Fonts
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 62)
small = ImageFont.truetype(font_path, 42)

# Timestamp
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

# FFmpeg
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

# Create 10 reels
for index, item in enumerate(news[:10], start=1):

    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    # Header
    draw.rectangle((0, 0, WIDTH, 210), fill="#c90020")
    draw.text(
        (65, 65),
        "SHORT KHABAR",
        font=small,
        fill="white"
    )

    # Category
    draw.text(
        (65, 330),
        item["category"].upper(),
        font=small,
        fill="#ffcc33"
    )

    # Headline
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

    # Footer
    draw.rectangle(
        (0, 1650, WIDTH, 1920),
        fill="#c90020"
    )

    draw.text(
        (65, 1730),
        "FOLLOW FOR MORE UPDATES",
        font=small,
        fill="white"
    )

    # Instagram username
    draw.rounded_rectangle(
        (65, 1795, 650, 1890),
        radius=25,
        fill="#E1306C"
    )

    draw.text(
        (90, 1815),
        "◎ @khabar.short",
        font=small,
        fill="white"
    )

    # Convert image to frame
    frame = np.array(image)

    filename = f"reels/news_{timestamp}_{index:02d}.mp4"
    temp_file = filename.replace(".mp4", "_silent.mp4")

    # Create silent video
    with imageio.get_writer(
        temp_file,
        fps=FPS,
        codec="libx264",
        macro_block_size=1
    ) as writer:

        for _ in range(FPS * DURATION):
            writer.append_data(frame)

    # Add background music
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

    # Delete temporary video
    os.remove(temp_file)

    print("Music Reel created:", filename)

print("SUCCESS: 10 Music Reels created!")
