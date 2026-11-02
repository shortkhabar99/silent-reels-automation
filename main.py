
import json
import feedparser
import requests
import re

from html.parser import HTMLParser
from datetime import datetime, timezone

FEEDS = {
    "नेपाल समाचार": "https://www.onlinekhabar.com/feed",
    "सेतोपाटी": "https://www.setopati.com/feed",
    "रातोपाटी": "https://www.ratopati.com/feed",
    "उज्यालो": "https://ujyaaloonline.com/rss"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}


# Find image inside article HTML
class ImageFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image = ""

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return

        data = dict(attrs)

        key = (
            data.get("property", "")
            or data.get("name", "")
        ).lower()

        if key in ["og:image", "twitter:image"]:
            self.image = data.get("content", "")
            

def get_article_image(link):
    if not link:
        return ""

    try:
        response = requests.get(
            link,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()

        finder = ImageFinder()
        finder.feed(response.text)

        return finder.image

    except Exception as error:
        print("Article image error:", error)
        return ""


def get_feed_image(item):
    # RSS media content
    for media in item.get("media_content", []):
        url = media.get("url", "")
        if url:
            return url

    # RSS thumbnail
    for media in item.get("media_thumbnail", []):
        url = media.get("url", "")
        if url:
            return url

    # RSS enclosure
    for enclosure in item.get("enclosures", []):
        url = enclosure.get("href") or enclosure.get("url", "")
        if url:
            return url

    # Image inside RSS summary
    html = item.get("summary", "") + item.get("description", "")
    match = re.search(
        r'<img[^>]+src=["\']([^"\']+)',
        html,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return ""


news = []
seen_links = set()

# COLLECT NEWS
for category, url in FEEDS.items():
    try:
        feed = feedparser.parse(url)

        for item in feed.entries:
            title = item.get("title", "").strip()
            link = item.get("link", "").strip()

            if title and link and link not in seen_links:
                news.append({
                    "category": category,
                    "title": title,
                    "link": link,
                    "image": get_feed_image(item),
                    "published": item.get("published", "")
                })

                seen_links.add(link)

            if len(news) >= 30:
                break

    except Exception as error:
        print("Feed error:", category, error)


# FIND ARTICLE PHOTOS FOR FIRST 10 NEWS
for item in news[:10]:
    if not item["image"]:
        print("Searching article photo:", item["title"])
        item["image"] = get_article_image(item["link"])

# SAVE NEWS
with open("news.json", "w", encoding="utf-8") as file:
    json.dump(news, file, ensure_ascii=False, indent=2)

photo_count = sum(
    1 for item in news[:10] if item.get("image")
)

print("News collected:", len(news))
print("Photos found for first 10 news:", photo_count)
print("Updated:", datetime.now(timezone.utc).isoformat())

if len(news) < 10:
    raise ValueError("At least 10 news items are required")
