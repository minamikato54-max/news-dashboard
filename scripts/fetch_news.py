"""RSSフィードから各カテゴリ4記事を取得し articles_raw.json に保存する。"""

import json
import sys
from pathlib import Path

import feedparser

RSS_SOURCES: dict[str, list[str]] = {
    "経済": [
        "https://www3.nhk.or.jp/rss/news/cat4.xml",
        "https://news.google.com/rss/search?q=%E7%B5%8C%E6%B8%88&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "国内": [
        "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "https://www3.nhk.or.jp/rss/news/cat5.xml",
    ],
    "海外": [
        "https://www3.nhk.or.jp/rss/news/cat6.xml",
        "https://feeds.bbci.co.uk/japanese/rss.xml",
        "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96+%E5%9B%BD%E9%9A%9B+%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&hl=ja&gl=JP&ceid=JP:ja",
    ],
    "AI事情": [
        "https://news.google.com/rss/search?q=AI+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD&hl=ja&gl=JP&ceid=JP:ja",
        "https://news.google.com/rss/search?q=%E7%94%9F%E6%88%90AI+%E6%9C%80%E6%96%B0&hl=ja&gl=JP&ceid=JP:ja",
    ],
}
ARTICLES_PER_CATEGORY = 4
OUTPUT_FILE = Path(__file__).parent.parent / "articles_raw.json"


def fetch_category(category: str, urls: list[str], seen_urls: set[str]) -> list[dict]:
    articles: list[dict] = []
    for url in urls:
        if len(articles) >= ARTICLES_PER_CATEGORY:
            break
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if len(articles) >= ARTICLES_PER_CATEGORY:
                    break
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or not link or link in seen_urls:
                    continue
                seen_urls.add(link)
                articles.append({"category": category, "title": title, "url": link})
        except Exception as e:
            print(f"[WARN] {category} RSS({url}) 取得失敗: {e}", file=sys.stderr)
    return articles


def main() -> None:
    all_articles = []
    seen_urls: set[str] = set()
    for category, urls in RSS_SOURCES.items():
        try:
            articles = fetch_category(category, urls, seen_urls)
            print(f"{category}: {len(articles)}件取得")
            all_articles.extend(articles)
        except Exception as e:
            print(f"[ERROR] {category} 取得失敗: {e}", file=sys.stderr)

    if not all_articles:
        print("[ERROR] 記事を1件も取得できませんでした", file=sys.stderr)
        sys.exit(1)

    OUTPUT_FILE.write_text(json.dumps(all_articles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"合計 {len(all_articles)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
