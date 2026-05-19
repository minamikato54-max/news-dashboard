"""RSSフィードから各カテゴリ4記事を取得し articles_raw.json に保存する。"""

import json
import sys
from pathlib import Path

import feedparser

RSS_SOURCES = {
    "経済": "https://www3.nhk.or.jp/rss/news/cat4.xml",
    "国内": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "海外": "https://www3.nhk.or.jp/rss/news/cat6.xml",
    "AI事情": "https://news.google.com/rss/search?q=AI+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD&hl=ja&gl=JP&ceid=JP:ja",
}
ARTICLES_PER_CATEGORY = 4
OUTPUT_FILE = Path(__file__).parent.parent / "articles_raw.json"


def fetch_category(category: str, url: str) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:ARTICLES_PER_CATEGORY]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue
        articles.append({"category": category, "title": title, "url": link})
    return articles


def main() -> None:
    all_articles = []
    for category, url in RSS_SOURCES.items():
        try:
            articles = fetch_category(category, url)
            print(f"{category}: {len(articles)}件取得")
            all_articles.extend(articles)
        except Exception as e:
            print(f"[ERROR] {category} RSS取得失敗: {e}", file=sys.stderr)

    if not all_articles:
        print("[ERROR] 記事を1件も取得できませんでした", file=sys.stderr)
        sys.exit(1)

    OUTPUT_FILE.write_text(json.dumps(all_articles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"合計 {len(all_articles)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
