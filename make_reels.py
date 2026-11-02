
import json
import os
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio
import numpy as np

WIDTH, HEIGHT = 1080, 1920
FPS = 15
DURATION = 6

os.makedirs("reels", exist_ok=True)

with open("news.json", encoding="utf-8") as f:
    news = json.load(f)

if len(news) < 10:
    raise ValueError("At least 10 news items are required")

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = ImageFont.truetype(font_path, 62)
small = ImageFont.truetype(font_path, 42)

timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

for index, item in enumerate(news[:10], start=1):
    image = Image.new("RGB", (WIDTH, HEIGHT), "#101827")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 210), fill="#c90020")
    draw.text((65, 65), "SHORT KHABAR", font=small, fill="white")

    draw.text((65, 330), item["category"].upper(),
              font=small, fill="#ffcc33")

    headline = item["title"]
    lines = textwrap.wrap(headline, width=22)

    y = 550
    for line in lines[:9]:
        draw.text((65, y), line, font=font, fill="white")
        y += 105

    draw.rectangle((0, 1650, WIDTH, 1920), fill="#c90020")
    draw.text((65, 1730), "FOLLOW FOR MORE UPDATES",
              font=small, fill="white")
    draw.text((65, 1820), "SHORT KHABAR",
              font=small, fill="white")

    frame = np.array(image)
    filename = f"reels/news_{timestamp}_{index:02d}.mp4"

    with imageio.get_writer(
        filename, fps=FPS, codec="libx264",
        macro_block_size=1
    ) as writer:
        for _ in range(FPS * DURATION):
            writer.append_data(frame)

    print("Silent Reel created:", filename)

print("SUCCESS: 10 Silent Reels created!")
