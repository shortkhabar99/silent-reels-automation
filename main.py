
import json
import feedparser
from datetime import datetime, timezone

FEEDS = {
    "नेपाल समाचार": "https://www.onlinekhabar.com/feed",
    "सेतोपाटी": "https://www.setopati.com/feed",
    "रातोपाटी": "https://www.ratopati.com/feed",
    "उज्यालो": "https://ujyaaloonline.com/rss"
}

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
                    "published": item.get("published", "")
                })
                seen_links.add(link)

            if len(news) >= 30:
                break

    except Exception as error:
        print(category, error)

with open("news.json", "w", encoding="utf-8") as file:
    json.dump(news, file, ensure_ascii=False, indent=2)

print("नेपाली समाचार संकलन:", len(news))
print("Updated:", datetime.now(timezone.utc).isoformat())

if len(news) < 10:
    raise ValueError("१० वटा समाचार उपलब्ध भएनन्। RSS स्रोत जाँच गर्नुहोस्।")
