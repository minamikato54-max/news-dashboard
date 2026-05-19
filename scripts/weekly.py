"""週次まとめ生成・関連記事紐付け・weekly.html 出力。"""

import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from supabase import Client, create_client

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"


def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL / SUPABASE_KEY が未設定です。")
    return create_client(url, key)


def fetch_week(client: Client) -> list[dict]:
    since = (date.today() - timedelta(days=7)).isoformat()
    resp = client.table("articles").select("*").gte("date", since).order("date", desc=True).execute()
    return resp.data or []


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


def update_related_ids(oai: OpenAI, client: Client, articles: list[dict]) -> None:
    """同カテゴリ内で類似記事を判定し related_ids を更新する。"""
    by_category: dict[str, list[dict]] = {}
    for a in articles:
        by_category.setdefault(a["category"], []).append(a)

    for category, arts in by_category.items():
        if len(arts) < 2:
            continue
        titles_json = json.dumps(
            [{"id": a["id"], "title": a["title"]} for a in arts],
            ensure_ascii=False,
        )
        prompt = f"""以下は「{category}」カテゴリの記事一覧です（id と title）。
{titles_json}
各記事に対して内容が類似している記事のIDを最大2件選び、以下のJSON形式のみで返してください：
[{{"id": "記事ID", "related_ids": ["類似記事ID1", "類似記事ID2"]}}]
類似度が低い場合は related_ids を空リストにしてください。"""
        try:
            resp = oai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0,
            )
            # GPTがオブジェクトで返す場合もあるため柔軟に処理
            raw = json.loads(resp.choices[0].message.content)
            pairs = raw if isinstance(raw, list) else raw.get("articles", raw.get("result", []))
            for pair in pairs:
                client.table("articles").update(
                    {"related_ids": pair.get("related_ids", [])}
                ).eq("id", pair["id"]).execute()
            time.sleep(0.5)
        except Exception as e:
            print(f"[WARN] {category} 関連記事更新失敗: {e}", file=sys.stderr)


def build_trend_data(trend_words: list[str], articles: list[dict]) -> list[dict]:
    """トレンドワードの出現回数を記事タイトル・要約から集計する。"""
    data = []
    all_text = " ".join(a.get("title", "") + " " + a.get("summary", "") for a in articles)
    for word in trend_words:
        count = all_text.count(word)
        data.append({"word": word, "count": max(count, 1)})
    return sorted(data, key=lambda x: x["count"], reverse=True)


def main() -> None:
    supabase = get_supabase()
    oai = OpenAI()

    articles = fetch_week(supabase)
    if not articles:
        print("[WARN] 直近7日分の記事がありません。", file=sys.stderr)

    print("週次まとめ生成中...")
    summary, trend_words = generate_weekly_summary(oai, articles)
    trend_data = build_trend_data(trend_words, articles)

    print("関連記事紐付け中...")
    update_related_ids(oai, supabase, articles)

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
