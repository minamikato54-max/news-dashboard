"""articles_raw.json を読み込み ChatGPT で処理して articles_processed.json に保存する。"""

import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

INPUT_FILE = Path(__file__).parent.parent / "articles_raw.json"
OUTPUT_FILE = Path(__file__).parent.parent / "articles_processed.json"

SYSTEM_PROMPT = """あなたはニュース記事の分析アシスタントです。
与えられた記事タイトルをもとに以下の情報を日本語で生成し、JSON形式のみで返してください。
{
  "summary": "記事の内容を2〜3文で要約。ニュースキャスターが読み上げる話し言葉（です・ます調）で書く。「〜ということです。」「注目したいのは〜です。」「〜が明らかになりました。」のような口語表現を使う。「〜である」「〜とされる」などの書き言葉は使わない",
  "terms": [{"word": "難しい専門用語", "explanation": "簡単な説明（1文）"}],
  "quiz": {
    "question": "記事内容に関する4択クイズの問題文",
    "choices": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "answer_index": 0
  },
  "importance": 2,
  "background": "この記事を理解するための背景知識（1〜2文）"
}
termsは0〜3個、importanceは1〜3の整数で重要度を示す（3が最重要）。

【クイズ作成の厳守ルール】
・難易度は高めに設定すること。「記事によると〜は何か」のような単純な読み取り問題は禁止。
・具体的な数値・固有名詞・因果関係・背景知識など、記事の核心部分を問うこと。
・誤答3つはいずれも一見もっともらしい内容にし、正解と紛らわしくする（明らかに間違いとわかる選択肢は禁止）。
・「なぜ〜か」「〜の主な目的は」「〜が意味することは」など、考察を要する問い方にすること。"""


def process_article(client: OpenAI, article: dict) -> dict:
    user_content = f"カテゴリ: {article['category']}\nタイトル: {article['title']}\nURL: {article['url']}"
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            result = json.loads(response.choices[0].message.content)
            return {**article, **result}
        except Exception as e:
            if attempt == 0:
                print(f"  [RETRY] {e}", file=sys.stderr)
                time.sleep(2)
            else:
                print(f"  [SKIP] {article['title']}: {e}", file=sys.stderr)
                return {
                    **article,
                    "summary": "（要約の取得に失敗しました）",
                    "terms": [],
                    "quiz": None,
                    "importance": 1,
                    "background": "",
                }


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"[ERROR] {INPUT_FILE} が見つかりません。fetch_news.py を先に実行してください。", file=sys.stderr)
        sys.exit(1)

    articles = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    client = OpenAI()
    processed = []

    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] 処理中: {article['title'][:40]}...")
        result = process_article(client, article)
        processed.append(result)
        time.sleep(0.5)

    OUTPUT_FILE.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"処理完了: {len(processed)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
