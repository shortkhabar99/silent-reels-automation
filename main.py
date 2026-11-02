
import json
import feedparser
import re
from datetime import datetime, timezone

FEEDS = {
    "नेपाल समाचार": "https://www.onlinekhabar.com/feed",
    "सेतोपाटी": "https://www.setopati.com/feed",
    "रातोपाटी": "https://www.ratopati.com/feed",
    "उज्यालो": "https://ujyaaloonline.com/rss"
}

def get_image(item):
    # RSS media content
    for media in item.get("media_content", []):
        url = media.get("url", "")
        if url:
            return url

    # RSS thumbnails
    for media in item.get("media_thumbnail", []):
        url = media.get("url", "")
        if url:
            return url

    # RSS enclosure
    for enclosure in item.get("enclosures", []):
        url = enclosure.get("href") or enclosure.get("url", "")
        if url:
            return url

    # Image links
    for link in item.get("links", []):
        url = link.get("href", "")
        if "image" in link.get("type", "") and url:
            return url

    # Image inside article summary
    html = item.get("summary", "") + item.get("description", "")
    match = re.search(r'<img[^>]+src=["\']([^"\']+)', html)

    if match:
        return match.group(1)

    return ""

news = []
seen_links = set()

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
                    "image": get_image(item),
                    "published": item.get("published", "")
                })

                seen_links.add(link)

            if len(news) >= 30:
                break

    except Exception as error:
        print(category, error)

with open("news.json", "w", encoding="utf-8") as file:
    json.dump(news, file, ensure_ascii=False, indent=2)

print("समाचार संकलन:", len(news))
print("फोटो लिंक भएका समाचार:", sum(1 for item in news if item["image"]))
print("Updated:", datetime.now(timezone.utc).isoformat())

if len(news) < 10:
    raise ValueError("१० वटा समाचार उपलब्ध भएनन्।")
