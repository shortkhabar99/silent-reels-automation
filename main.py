
import json
import feedparser
from datetime import datetime, timezone

FEEDS = {
    "World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Nepal News": "https://english.onlinekhabar.com/feed",
    "Cricket": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "Trending": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
}

news = []

for category, url in FEEDS.items():
    try:
        feed = feedparser.parse(url)

        for item in feed.entries[:2]:
            news.append({
                "category": category,
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "published": item.get("published", "")
            })

    except Exception as error:
        print(category, error)

with open("news.json", "w", encoding="utf-8") as file:
    json.dump(news, file, ensure_ascii=False, indent=2)

print("News collected:", len(news))
print("Updated:", datetime.now(timezone.utc).isoformat())
