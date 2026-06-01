"""data/articles/ から記事を取得して index.html / archive.html を生成する。"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data" / "articles"
ARCHIVE_DAYS = 30
ARTICLES_PER_CATEGORY = 4


def fetch_today(today: str) -> list[dict]:
    path = DATA_DIR / f"{today}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_archive(since: str) -> list[dict]:
    articles = []
    if not DATA_DIR.exists():
        return articles
    for f in sorted(DATA_DIR.glob("*.json"), reverse=True):
        if f.stem >= since:
            data = json.loads(f.read_text(encoding="utf-8"))
            articles.extend(
                {
                    "id": a["id"],
                    "date": a["date"],
                    "category": a["category"],
                    "title": a["title"],
                    "url": a["url"],
                    "summary": a.get("summary", ""),
                    "importance": a.get("importance", 1),
                }
                for a in data
            )
    return articles


def main() -> None:
    today = date.today().isoformat()
    since = (date.today() - timedelta(days=ARCHIVE_DAYS)).isoformat()

    today_articles = fetch_today(today)
    archive_articles = fetch_archive(since)

    if not today_articles:
        print("[WARN] 本日の記事がありません。HTMLは生成しますが空になります。", file=sys.stderr)

    DOCS_DIR.mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

    # index.html
    categories = ["経済", "AI事情", "国内", "海外"]
    by_category = {cat: [] for cat in categories}
    for a in today_articles:
        cat = a.get("category", "")
        if cat in by_category and len(by_category[cat]) < ARTICLES_PER_CATEGORY:
            by_category[cat].append(a)

    tmpl = env.get_template("index.html.j2")
    html = tmpl.render(
        today=today,
        categories=categories,
        by_category=by_category,
        total=len(today_articles),
    )
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html 生成完了（{len(today_articles)} 件）")

    # archive.html
    tmpl = env.get_template("archive.html.j2")
    html = tmpl.render(
        articles_json=json.dumps(archive_articles, ensure_ascii=False),
        today=today,
    )
    (DOCS_DIR / "archive.html").write_text(html, encoding="utf-8")
    print(f"archive.html 生成完了（{len(archive_articles)} 件）")


if __name__ == "__main__":
    main()
