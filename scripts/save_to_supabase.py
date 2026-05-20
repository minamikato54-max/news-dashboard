"""articles_processed.json を Supabase の articles テーブルに保存する。"""

import json
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

INPUT_FILE = Path(__file__).parent.parent / "articles_processed.json"


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL / SUPABASE_KEY が設定されていません。")
    return create_client(url, key)


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} が見つかりません。", file=sys.stderr)
        sys.exit(1)

    articles = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    client = get_client()

    seen_urls: set[str] = set()
    rows = []
    for a in articles:
        url = a["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)
        rows.append({
            "date": today,
            "category": a["category"],
            "title": a["title"],
            "url": url,
            "summary": a.get("summary", ""),
            "terms": a.get("terms", []),
            "quiz": a.get("quiz"),
            "importance": a.get("importance", 1),
            "background": a.get("background", ""),
            "related_ids": [],
        })

    saved = 0
    for row in rows:
        try:
            client.table("articles").upsert(row, on_conflict="url,date").execute()
            saved += 1
        except Exception as e:
            print(f"[WARN] 保存スキップ ({row['url']}): {e}", file=sys.stderr)
    print(f"Supabase に {saved} 件保存完了（日付: {today}）")


if __name__ == "__main__":
    main()
