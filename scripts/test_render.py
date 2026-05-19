"""Supabase なしでモックデータを使いテンプレートを描画する検証スクリプト。
生成先: docs/index.html, docs/archive.html, docs/weekly.html
"""

import json
from datetime import date, timedelta
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"

TODAY = date.today().isoformat()
WEEK_START = (date.today() - timedelta(days=7)).isoformat()


def d(days_ago: int) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


# ----------------------------------------------------------------
# 今日の記事（4カテゴリ × 4件 = 16件）
# ----------------------------------------------------------------
TODAY_ARTICLES = [
    # ---- 経済 (4件) ----
    {
        "id": "eco-001", "category": "経済", "date": TODAY,
        "title": "日本のAI競争力が向上、各社が技術開発に注力",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "日本企業のAI分野における競争力が向上している。政府の支援策も後押しし、実行力のある施策が次々と打たれている。各社の影響力も国際的に拡大しつつある。",
        "terms": [
            {"word": "競争力", "explanation": "他と比べた際の優位性・強さのこと"},
            {"word": "生成AI", "explanation": "テキストや画像などのコンテンツを自動生成するAI技術"},
        ],
        "quiz": {
            "question": "日本のAI競争力向上の主な要因として正しいものはどれですか？",
            "choices": ["政府の支援策", "円安の影響", "人口増加", "輸出規制の撤廃"],
            "answer_index": 0,
        },
        "importance": 3,
        "background": "近年、米国・中国に続く第三のAI大国を目指す動きが加速している。",
        "related_ids": ["eco-002"],
    },
    {
        "id": "eco-002", "category": "経済", "date": TODAY,
        "title": "円相場が150円台、輸出企業の収益力に追い風",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "外国為替市場で円安が進行し1ドル150円台となった。輸出企業の収益力は向上しているが、輸入品の価格上昇で家計への負担感が増している。",
        "terms": [
            {"word": "為替レート", "explanation": "異なる通貨を交換する際の比率"},
            {"word": "収益力", "explanation": "利益を生み出す能力・効率"},
        ],
        "quiz": {
            "question": "円安が進むと輸出企業にとってどのような影響がありますか？",
            "choices": ["収益が増加する", "収益が減少する", "影響はない", "コストが上がる"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "日米金利差が拡大したことが主な要因とされている。",
        "related_ids": [],
    },
    {
        "id": "eco-003", "category": "経済", "date": TODAY,
        "title": "日銀が金融政策を維持、物価安定目標の達成に向け持続力を強調",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "日本銀行は金融政策決定会合で現行の政策を維持することを決定した。物価安定目標2%の持続的実現に向け粘り強く取り組む方針を示した。",
        "terms": [
            {"word": "金融政策", "explanation": "中央銀行が金利や通貨量を調節する政策"},
        ],
        "quiz": {
            "question": "日本銀行の物価安定目標は何パーセントですか？",
            "choices": ["2%", "1%", "3%", "0%"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "日銀は2016年以降マイナス金利政策を実施してきたが、2024年に解除した。",
        "related_ids": [],
    },
    {
        "id": "eco-004", "category": "経済", "date": TODAY,
        "title": "半導体市場が回復基調、国内製造業の技術革新力に期待",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "世界的な半導体市場が回復基調に入り、日本の製造業にも恩恵が及んでいる。技術革新力を高めた国内企業が競争優位性を確立しつつある。",
        "terms": [
            {"word": "半導体", "explanation": "電気を通す導体と通さない絶縁体の中間の性質を持つ素材"},
        ],
        "quiz": None,
        "importance": 1,
        "background": "半導体は電子機器の基幹部品で、AI・自動車・スマートフォンなど幅広く使われる。",
        "related_ids": [],
    },
    # ---- AI事情 (4件) ----
    {
        "id": "ai-001", "category": "AI事情", "date": TODAY,
        "title": "Claude 4が公開、思考力と対話力が大幅向上",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "Anthropic が最新モデル Claude 4 を公開した。推論能力の向上により複雑な問題の処理能力が向上し、多くの業界での活用余地が広がっている。",
        "terms": [
            {"word": "推論能力", "explanation": "与えられた情報から論理的な結論を導く力"},
            {"word": "LLM", "explanation": "大規模言語モデル。大量のテキストで学習したAI"},
        ],
        "quiz": {
            "question": "Claude 4 を開発した会社はどこですか？",
            "choices": ["OpenAI", "Google", "Anthropic", "Meta"],
            "answer_index": 2,
        },
        "importance": 2,
        "background": "2023年以降、生成AIの進化が加速し各社が競争を繰り広げている。",
        "related_ids": ["ai-002"],
    },
    {
        "id": "ai-002", "category": "AI事情", "date": TODAY,
        "title": "AI規制法案が国会で審議入り、企業の対応力が問われる",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "生成AIの普及に伴い国会でAI規制法案の審議が始まった。個人情報保護と透明性の確保が焦点で、企業の対応力と説明責任が問われている。",
        "terms": [
            {"word": "透明性", "explanation": "システムや意思決定の過程が外部から確認できること"},
            {"word": "説明責任", "explanation": "行動や決定の理由を関係者に説明する義務"},
        ],
        "quiz": {
            "question": "AI規制法案の主な焦点として挙げられているものはどれですか？",
            "choices": ["個人情報保護と透明性", "税率引き上げ", "雇用促進", "輸出拡大"],
            "answer_index": 0,
        },
        "importance": 3,
        "background": "EUのAI規制法（AI Act）が先行施行され、日本でも議論が本格化した。",
        "related_ids": [],
    },
    {
        "id": "ai-003", "category": "AI事情", "date": TODAY,
        "title": "医療AIが診断精度を向上、医師の判断補助ツールとして実用化",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "AIを活用した医療診断支援システムの実用化が進んでいる。医師の診断精度と処理能力を補完し、患者への対応力向上が期待されている。",
        "terms": [
            {"word": "診断支援AI", "explanation": "医師が診断を下す際に補助するAIシステム"},
        ],
        "quiz": {
            "question": "医療AIの主な役割として正しいものはどれですか？",
            "choices": ["医師の判断補助", "手術の自動化", "薬の製造", "患者の選別"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "AIによる画像診断は既に一部の病院で導入されており、見落とし防止に効果を上げている。",
        "related_ids": [],
    },
    {
        "id": "ai-004", "category": "AI事情", "date": TODAY,
        "title": "AIによる偽情報拡散の抑止力強化、各プラットフォームが対策",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "SNS各社がAIを使った偽情報検知システムを強化している。抑止力のある仕組みを整えることで情報の信頼性を高める取り組みが本格化している。",
        "terms": [
            {"word": "ディープフェイク", "explanation": "AIで生成された本物そっくりの偽の映像・音声"},
        ],
        "quiz": None,
        "importance": 1,
        "background": "生成AIの普及で偽情報の作成コストが下がり、問題が深刻化している。",
        "related_ids": [],
    },
    # ---- 国内 (4件) ----
    {
        "id": "dom-001", "category": "国内", "date": TODAY,
        "title": "少子化対策として育児支援策を拡充、実行力ある政策が急務",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "政府は少子化対策の一環として育児休業給付の拡充を決定した。財源確保の実現可能性と持続可能性が課題で、実行力ある政策が急がれている。",
        "terms": [
            {"word": "育児休業給付", "explanation": "育児休業中に支給される給付金"},
            {"word": "少子化", "explanation": "出生率が低下し子どもの数が減少すること"},
        ],
        "quiz": {
            "question": "今回の少子化対策で拡充されたものはどれですか？",
            "choices": ["育児休業給付", "年金支給額", "医療費補助", "住宅ローン控除"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "日本の合計特殊出生率は1.2を下回り過去最低水準が続いている。",
        "related_ids": [],
    },
    {
        "id": "dom-002", "category": "国内", "date": TODAY,
        "title": "能登半島の復興状況を視察、地域の持続力を支援",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "首相が能登半島地震の被災地を視察し、インフラ整備の加速を指示した。道路・水道の復旧が急がれており、地域社会の持続力を支える支援が続いている。",
        "terms": [],
        "quiz": None,
        "importance": 1,
        "background": "2024年1月の能登半島地震で甚大な被害が出た。復興には数年を要するとされている。",
        "related_ids": [],
    },
    {
        "id": "dom-003", "category": "国内", "date": TODAY,
        "title": "国会議員の政治資金問題、透明性と説明責任が焦点",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "政治資金をめぐる問題が国会で議論されている。政治家の説明責任と資金管理の透明性確保を求める声が高まっており、制度改正の実現可能性が問われている。",
        "terms": [
            {"word": "政治資金規正法", "explanation": "政治活動に関わる資金の収支公開などを規定した法律"},
        ],
        "quiz": {
            "question": "政治資金問題で特に求められているものはどれですか？",
            "choices": ["透明性と説明責任", "支出の増加", "規制の撤廃", "海外送金"],
            "answer_index": 0,
        },
        "importance": 3,
        "background": "2024年に自民党の派閥パーティー券問題が発覚し、政治不信が高まった。",
        "related_ids": [],
    },
    {
        "id": "dom-004", "category": "国内", "date": TODAY,
        "title": "インバウンド需要が過去最高、観光地の受容力整備が課題",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "訪日外国人数が過去最高を更新し、観光消費額も拡大している。一方で人気観光地の受容力を超えるオーバーツーリズムが問題となっており、対策が急がれている。",
        "terms": [
            {"word": "インバウンド", "explanation": "外国から自国への旅行者・旅行需要"},
            {"word": "オーバーツーリズム", "explanation": "観光客が過剰になり地域住民の生活に支障が出る状態"},
        ],
        "quiz": {
            "question": "オーバーツーリズムとはどのような問題ですか？",
            "choices": ["観光客過多による地域への悪影響", "観光客の減少", "旅費の高騰", "ビザ発給の停止"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "円安が追い風となり訪日外国人数は月間300万人を超えることも多くなっている。",
        "related_ids": [],
    },
    # ---- 海外 (4件) ----
    {
        "id": "int-001", "category": "海外", "date": TODAY,
        "title": "G7サミット開幕、AIガバナンスと気候変動が議題に",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "主要7カ国首脳会議（G7サミット）が開幕した。AIの国際規制と気候変動対策が主要議題で、各国の指導力と影響力が試される場となっている。",
        "terms": [
            {"word": "ガバナンス", "explanation": "組織や社会を適切に管理・統治する仕組み"},
            {"word": "G7", "explanation": "日米英仏独伊加の7カ国による首脳会議"},
        ],
        "quiz": {
            "question": "今回のG7サミットの主要議題に含まれていないものはどれですか？",
            "choices": ["宇宙開発", "AIガバナンス", "気候変動対策", "国際規制枠組み"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "G7はGDP上位7カ国で構成され、世界の主要課題を議論する場として機能している。",
        "related_ids": ["int-002"],
    },
    {
        "id": "int-002", "category": "海外", "date": TODAY,
        "title": "中東情勢が緊迫、原油価格が急騰し世界経済への影響力が拡大",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "中東の軍事的緊張が高まり原油価格が1バレル90ドルを超えた。エネルギー輸入依存度の高い日本への影響力は大きく、物価上昇への懸念が強まっている。",
        "terms": [
            {"word": "原油価格", "explanation": "石油の取引価格。世界経済に広く影響を与える"},
        ],
        "quiz": {
            "question": "中東情勢の緊迫化により原油価格はどうなりましたか？",
            "choices": ["急騰した", "急落した", "横ばいだった", "乱高下した"],
            "answer_index": 0,
        },
        "importance": 3,
        "background": "中東は世界の原油生産量の約3割を占めており、地域情勢が価格に直結する。",
        "related_ids": [],
    },
    {
        "id": "int-003", "category": "海外", "date": TODAY,
        "title": "米大統領が対中関税を維持、貿易摩擦の持続力が懸念",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "米国が中国に対する追加関税の維持を発表した。貿易摩擦の長期化が世界のサプライチェーンに影響を及ぼしており、各国の対応力が試されている。",
        "terms": [
            {"word": "関税", "explanation": "輸入品に課せられる税金"},
            {"word": "サプライチェーン", "explanation": "製品の原材料調達から消費者への届けまでの一連の流れ"},
        ],
        "quiz": {
            "question": "米国が中国に対して行っている経済的措置はどれですか？",
            "choices": ["追加関税の維持", "関税の撤廃", "貿易協定の締結", "投資の促進"],
            "answer_index": 0,
        },
        "importance": 2,
        "background": "米中貿易摩擦は2018年のトランプ政権時代から続いており、バイデン・トランプ政権でも維持されている。",
        "related_ids": [],
    },
    {
        "id": "int-004", "category": "海外", "date": TODAY,
        "title": "ウクライナ支援継続をNATO確認、防衛能力の強化が急務",
        "url": "https://www3.nhk.or.jp/news/",
        "summary": "NATO加盟国がウクライナへの軍事・財政支援の継続を確認した。防衛能力の強化と持久力のある支援体制の構築が急務とされている。",
        "terms": [
            {"word": "NATO", "explanation": "北大西洋条約機構。米国を中心とした集団防衛機構"},
        ],
        "quiz": {
            "question": "NATOがウクライナに対して確認したことはどれですか？",
            "choices": ["支援継続", "支援停止", "停戦仲介", "加盟承認"],
            "answer_index": 0,
        },
        "importance": 3,
        "background": "2022年2月のロシアによるウクライナ侵攻以来、NATO諸国は支援を続けている。",
        "related_ids": [],
    },
]

# ----------------------------------------------------------------
# 過去7日分のアーカイブ用記事（各日4件）
# ----------------------------------------------------------------
ARCHIVE_ARTICLES = []
for days_ago in range(1, 8):
    dt = d(days_ago)
    ARCHIVE_ARTICLES += [
        {
            "id": f"arch-{days_ago}-1", "category": "経済", "date": dt,
            "title": f"経済ニュース {dt}：GDP改定値が公表",
            "url": "https://www3.nhk.or.jp/news/",
            "summary": f"{dt} の経済ニュース。GDPの改定値が公表され、実質成長率が前期比でプラスとなった。",
            "importance": 2,
        },
        {
            "id": f"arch-{days_ago}-2", "category": "AI事情", "date": dt,
            "title": f"AI事情 {dt}：新サービスが相次いでリリース",
            "url": "https://www3.nhk.or.jp/news/",
            "summary": f"{dt} のAIニュース。大手テック企業から新しいAIサービスが相次いでリリースされた。",
            "importance": 2,
        },
        {
            "id": f"arch-{days_ago}-3", "category": "国内", "date": dt,
            "title": f"国内ニュース {dt}：国会審議が続く",
            "url": "https://www3.nhk.or.jp/news/",
            "summary": f"{dt} の国内ニュース。重要法案の国会審議が続いており、与野党の攻防が続いている。",
            "importance": 1,
        },
        {
            "id": f"arch-{days_ago}-4", "category": "海外", "date": TODAY,
            "title": f"海外ニュース {dt}：国際情勢が緊迫",
            "url": "https://www3.nhk.or.jp/news/",
            "summary": f"{dt} の海外ニュース。国際情勢の緊迫化を受け、各国首脳が緊急会議を開催した。",
            "importance": 2,
        },
    ]

ALL_ARTICLES = TODAY_ARTICLES + ARCHIVE_ARTICLES


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)

    categories = ["経済", "AI事情", "国内", "海外"]

    # ---- index.html ----
    by_category = {cat: [] for cat in categories}
    for a in TODAY_ARTICLES:
        by_category[a["category"]].append(a)

    html = env.get_template("index.html.j2").render(
        today=TODAY,
        categories=categories,
        by_category=by_category,
        total=len(TODAY_ARTICLES),
    )
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"[OK] index.html   ({len(TODAY_ARTICLES)} articles)")

    # ---- archive.html ----
    archive_fields = ["id", "date", "category", "title", "url", "summary", "importance"]
    archive_data = [{k: a.get(k, "") for k in archive_fields} for a in ALL_ARTICLES]

    html = env.get_template("archive.html.j2").render(
        articles_json=json.dumps(archive_data, ensure_ascii=False),
        today=TODAY,
    )
    (DOCS_DIR / "archive.html").write_text(html, encoding="utf-8")
    print(f"[OK] archive.html ({len(archive_data)} articles)")

    # ---- weekly.html ----
    important = [a for a in ALL_ARTICLES if a.get("importance") == 3][:6]
    trend_words = ["AI", "競争力", "円安", "中東", "少子化", "原油価格", "NATO", "半導体"]
    all_text = " ".join(a.get("title","") + " " + a.get("summary","") for a in ALL_ARTICLES)
    trend_data = sorted(
        [{"word": w, "count": max(all_text.count(w), 1)} for w in trend_words],
        key=lambda x: x["count"], reverse=True,
    )
    weekly_summary = (
        "今週は国内外でAI関連の話題が目立った。"
        "国内ではAI規制法案の審議入りや少子化対策の拡充が議論された。"
        "海外では中東情勢の緊迫化による原油価格上昇とG7サミットでのAIガバナンス議論が注目を集めた。"
        "経済面では円安が続き輸出企業への追い風となる一方、輸入物価の上昇が家計を圧迫している。"
    )

    html = env.get_template("weekly.html.j2").render(
        week_end=TODAY,
        week_start=WEEK_START,
        summary=weekly_summary,
        trend_data=trend_data,
        important_articles=important,
        total=len(ALL_ARTICLES),
    )
    (DOCS_DIR / "weekly.html").write_text(html, encoding="utf-8")
    print(f"[OK] weekly.html  ({len(important)} important articles)")

    print(f"\n--- 3 pages generated in {DOCS_DIR} ---")
    print(f"Open: start {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
