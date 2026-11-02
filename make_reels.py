
import json
import os
import textwrap
import subprocess
import glob
import requests
import imageio_ffmpeg

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
english_font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

headline_font = ImageFont.truetype(nepali_font, 58)
category_font = ImageFont.truetype(nepali_font, 42)
english_big = ImageFont.truetype(english_font, 42)
english_small = ImageFont.truetype(english_font, 32)

# CHECK MUSIC
if not os.path.exists("news_music.mp3"):
    raise FileNotFoundError("news_music.mp3 not found")

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")


# DOWNLOAD NEWS PHOTO
def download_photo(url):
    if not url:
        return None

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()

        photo = Image.open(BytesIO(response.content))
        photo = photo.convert("RGB")

        photo = ImageOps.fit(
            photo,
            (950, 600),
            method=Image.Resampling.LANCZOS
        )

        return photo

    except Exception as error:
        print("Photo unavailable:", error)
        return None


# CREATE 10 REELS
for index, item in enumerate(news[:10], start=1):

    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    # HEADER
    draw.rectangle((0, 0, WIDTH, 210), fill="#c90020")

    draw.text(
        (65, 65),
        "SHORT KHABAR",
        font=english_big,
        fill="white"
    )

    # CATEGORY
    draw.text(
        (65, 300),
        item.get("category", "समाचार"),
        font=category_font,
        fill="#ffcc33"
    )

    # HEADLINE
    headline = item.get("title", "ताजा समाचार")
    lines = textwrap.wrap(headline, width=25)

    y = 420

    for line in lines[:4]:
        draw.text(
            (65, y),
            line,
            font=headline_font,
            fill="white"
        )
        y += 95

    # NEWS PHOTO
    photo = download_photo(item.get("image", ""))

    if photo:
        image.paste(photo, (65, 900))
        print("Photo added:", item.get("title", ""))
    else:
        draw.rounded_rectangle(
            (65, 900, 1015, 1500),
            radius=25,
            fill="#263449"
        )

        draw.text(
            (300, 1150),
            "PHOTO NOT AVAILABLE",
            font=english_small,
            fill="white"
        )

        print("No photo:", item.get("title", ""))

    # FOOTER
    draw.rectangle(
        (0, 1650, WIDTH, 1920),
        fill="#c90020"
    )

    draw.text(
        (65, 1730),
        "FOLLOW FOR MORE UPDATES",
        font=english_small,
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
        font=english_small,
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

    # ADD BACKGROUND MUSIC
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

    print("Music Photo Reel created:", filename)

print("SUCCESS: 10 Photo Music Reels created!")
