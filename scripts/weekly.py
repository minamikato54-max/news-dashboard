"""週次まとめ生成・weekly.html 出力。"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data" / "articles"


def fetch_week() -> list[dict]:
    since = (date.today() - timedelta(days=7)).isoformat()
    articles = []
    if not DATA_DIR.exists():
        return articles
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.stem >= since:
            articles.extend(json.loads(f.read_text(encoding="utf-8")))
    return sorted(articles, key=lambda a: a["date"], reverse=True)


def generate_weekly_summary(oai: OpenAI, articles: list[dict]) -> tuple[str, list[str]]:
    """週次まとめ文とトレンドワード上位5件を生成する。"""
    titles = "\n".join(f"- [{a['category']}] {a['title']}" for a in articles[:40])
    prompt = f"""以下は今週のニュース記事タイトル一覧です。
{titles}

以下のJSON形式のみで返してください：
{{
  "summary": "今週のニュースを3〜5文でまとめた文章",
  "trend_words": ["キーワード1", "キーワード2", "キーワード3", "キーワード4", "キーワード5"]
}}"""
    resp = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("summary", ""), data.get("trend_words", [])


def build_trend_data(trend_words: list[str], articles: list[dict]) -> list[dict]:
    """トレンドワードの出現回数を記事タイトル・要約から集計する。"""
    data = []
    all_text = " ".join(a.get("title", "") + " " + a.get("summary", "") for a in articles)
    for word in trend_words:
        count = all_text.count(word)
        data.append({"word": word, "count": max(count, 1)})
    return sorted(data, key=lambda x: x["count"], reverse=True)


def main() -> None:
    oai = OpenAI()

    articles = fetch_week()
    if not articles:
        print("[WARN] 直近7日分の記事がありません。", file=sys.stderr)

    print("週次まとめ生成中...")
    summary, trend_words = generate_weekly_summary(oai, articles)
    trend_data = build_trend_data(trend_words, articles)

    DOCS_DIR.mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    tmpl = env.get_template("weekly.html.j2")

    important = [a for a in articles if a.get("importance") == 3][:6]
    html = tmpl.render(
        week_end=date.today().isoformat(),
        week_start=(date.today() - timedelta(days=7)).isoformat(),
        summary=summary,
        trend_data=trend_data,
        important_articles=important,
        total=len(articles),
    )
    (DOCS_DIR / "weekly.html").write_text(html, encoding="utf-8")
    print("weekly.html 生成完了")


if __name__ == "__main__":
    main()
