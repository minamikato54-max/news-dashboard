"""articles_processed.json を data/articles/YYYY-MM-DD.json に保存する。"""

import json
import sys
from datetime import date
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "articles_processed.json"
DATA_DIR = Path(__file__).parent.parent / "data" / "articles"

CATEGORY_PREFIX = {
    "経済": "eco",
    "AI事情": "ai",
    "国内": "dom",
    "海外": "int",
}


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} が見つかりません。", file=sys.stderr)
        sys.exit(1)

    articles = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    today = date.today().isoformat()
    today_compact = today.replace("-", "")

    seen_urls: set[str] = set()
    rows = []
    cat_counters: dict[str, int] = {}

    for a in articles:
        url = a["url"]
        if url in seen_urls:
            continue
        seen_urls.add(url)

        cat = a.get("category", "other")
        prefix = CATEGORY_PREFIX.get(cat, "art")
        cat_counters[prefix] = cat_counters.get(prefix, 0) + 1
        idx = cat_counters[prefix]

        rows.append({
            "id": f"{prefix}-{today_compact}-{idx:02d}",
            "date": today,
            "category": cat,
            "title": a["title"],
            "url": url,
            "summary": a.get("summary", ""),
            "terms": a.get("terms", []),
            "quiz": a.get("quiz"),
            "importance": a.get("importance", 1),
            "background": a.get("background", ""),
            "related_ids": [],
        })

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output = DATA_DIR / f"{today}.json"
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"data/articles/{today}.json に {len(rows)} 件保存完了")


if __name__ == "__main__":
    main()
