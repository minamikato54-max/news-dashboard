"""Supabase から記事を取得して index.html / archive.html を生成する。"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from supabase import Client, create_client

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"
ARCHIVE_DAYS = 30
ARTICLES_PER_CATEGORY = 4


def get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL / SUPABASE_KEY が未設定です。")
    return create_client(url, key)


def fetch_today(client: Client, today: str) -> list[dict]:
    resp = (
        client.table("articles")
        .select("*")
        .eq("date", today)
        .order("category")
        .execute()
    )
    return resp.data or []


def fetch_archive(client: Client, since: str) -> list[dict]:
    resp = (
        client.table("articles")
        .select("id,date,category,title,url,summary,importance")
        .gte("date", since)
        .order("date", desc=True)
        .execute()
    )
    return resp.data or []


def main() -> None:
    today = date.today().isoformat()
    since = (date.today() - timedelta(days=ARCHIVE_DAYS)).isoformat()

    client = get_client()
    today_articles = fetch_today(client, today)
    archive_articles = fetch_archive(client, since)

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
