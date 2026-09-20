# -*- coding: utf-8 -*-
"""public/index.html を新仕様に更新する（冪等：何度実行しても同じ結果）"""
import json
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "public/index.html"
s = open(PATH, encoding="utf-8").read()

TITLE = "日経平均 恐怖と強欲指数 リアルタイム｜日本・米国 Nikkei Fear &amp; Greed Index"
DESC = "日本のNikkeiと米国S&amp;P500の恐怖と強欲指数をリアルタイムで確認できます。騰落率、変動性、安全資産需要など6つの指標を総合した日米の投資心理ダッシュボード。"
SITE_NAME = "Fear &amp; Greed Index Japan"


def sub_once(pattern, repl, flags=re.S):
    global s
    new, n = re.subn(pattern, repl, s, count=1, flags=flags)
    assert n == 1, ("pattern not found", pattern[:70])
    s = new


# ───────── head ─────────
sub_once(r"<title>.*?</title>", f"<title>{TITLE}</title>")
sub_once(r'<meta name="description" content=".*?">', f'<meta name="description" content="{DESC}">')
sub_once(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{TITLE}">')
sub_once(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{DESC}">')
sub_once(r'<meta property="og:site_name" content=".*?">', f'<meta property="og:site_name" content="{SITE_NAME}">')
sub_once(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{TITLE}">')
sub_once(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{DESC}">')
if 'og:image:width' not in s:
    sub_once(r'(<meta property="og:image" content="[^"]*">)', r'\1\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">')
if "apple-touch-icon" not in s:
    sub_once(r'<link rel="icon" href="[^"]*">',
             '<link rel="icon" href="/favicon.ico" sizes="any">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">')

website_ld = {
    "@context": "https://schema.org", "@type": "WebSite",
    "name": "Fear & Greed Index Japan", "alternateName": "日経平均 恐怖と強欲指数",
    "url": "https://feargreedjapan.com/", "inLanguage": "ja",
    "description": "日本のNikkeiと米国S&P500の恐怖と強欲指数をリアルタイムで確認できる、日米の投資心理ダッシュボード",
}
sub_once(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "WebSite".*?</script>',
         '<script type="application/ld+json">\n' + json.dumps(website_ld, ensure_ascii=False, indent=2) + "\n</script>")

# Google Search Console の所有権確認タグ（重複して入らないようにする）
if "google-site-verification" not in s:
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<meta name="google-site-verification" content="HoU_nbY9is8mGhPZ6eENVWpMUnDZx3JJAhnjUdSYqHg" />', 1)

# ───────── header / nav / footer ─────────
sub_once(r'<a class="brand" href="/">.*?</a>', f'<a class="brand" href="/">{SITE_NAME}<small>恐怖と強欲指数</small></a>')
sub_once(r'<nav class="nav" aria-label="メインメニュー">.*?</nav>',
         '<nav class="nav" aria-label="メインメニュー">\n'
         '      <a href="/" aria-current="page">ダッシュボード</a>\n'
         '      <a href="/archive">市況アーカイブ</a>\n'
         '      <a href="/blog">ブログ</a>\n'
         '      <a href="/guide">投資ガイド</a>\n'
         '      <a href="/about">サイトについて</a>\n'
         '    </nav>')
sub_once(r'<div class="footer-links">.*?</div>',
         '<div class="footer-links">\n'
         '      <a href="/">ダッシュボード</a>\n      <a href="/archive">市況アーカイブ</a>\n      <a href="/blog">ブログ</a>\n'
         '      <a href="/guide">投資ガイド</a>\n      <a href="/about">サイトについて</a>\n'
         '      <a href="/terms">利用規約</a>\n      <a href="/privacy">プライバシーポリシー</a>\n    </div>')
sub_once(r'© 2026 Fear &amp; Greed[^<]*?\. All rights reserved\.', f"© 2026 {SITE_NAME}. All rights reserved.")

# ───────── hero: eyebrow ─────────
if 'class="eyebrow"' not in s:
    sub_once(r'(<div class="hero">\s*)(<h1>)', r'\1<div class="eyebrow">日経平均・S&amp;P500 恐怖と強欲指数</div>\n      \2')

# ───────── 追加CSS ─────────
EXTRA_CSS = """
<style>
  .eyebrow { font-size: 13px; font-weight: 700; color: var(--c-eg); letter-spacing: .06em; margin-bottom: 10px; }
  .chip { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 10px; border-radius: 999px; color: #fff; background: var(--c-n); white-space: nowrap; }
  .chip.ef { background: var(--c-ef); } .chip.f { background: var(--c-f); } .chip.n { background: var(--c-n); }
  .chip.g { background: var(--c-g); } .chip.eg { background: var(--c-eg); }
  .content-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 28px; }
  .content-card p { color: var(--ink-soft); font-size: 15px; line-height: 1.95; margin-top: 12px; }
  .content-card p:first-child { margin-top: 0; }
  .content-card a.inline, .sec-lead a.inline { color: var(--c-eg); text-underline-offset: 3px; }
  table.method th.w-s { width: 9.5em; white-space: nowrap; }
  table.method td.top, table.method th.top { vertical-align: top; line-height: 1.75; }
  .callout { margin-top: 18px; padding: 14px 18px; background: #eef3fb; border-left: 4px solid var(--ink); border-radius: 4px; }
  .callout p { margin: 0; font-size: 14px; line-height: 1.85; color: var(--ink-soft); }
  .callout.warn { background: #fff8ec; border-left-color: #d9a441; } .callout.warn p { color: #6a5320; }
  .latest-card { display: block; text-decoration: none; }
  .latest-card:hover { border-color: var(--ink-soft); }
  .latest-card .meta { font-size: 13px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; }
  .latest-card .ttl { font-size: 18px; font-weight: 900; line-height: 1.6; margin-top: 8px; color: var(--ink); }
  .latest-card .ex { font-size: 14.5px; color: var(--ink-soft); margin-top: 8px; line-height: 1.85; }
  .btn-row { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
  .btn-row a { font-size: 14px; font-weight: 700; text-decoration: none; padding: 9px 18px; border-radius: 8px; background: var(--ink); color: #fff; }
  .btn-row a.sub { background: var(--surface); color: var(--ink); border: 1px solid var(--line); }
  .faq { margin-top: 4px; }
  .faq details { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); margin-top: 10px; }
  .faq summary { cursor: pointer; padding: 16px 20px; font-weight: 700; font-size: 15.5px; line-height: 1.65; list-style: none; display: flex; gap: 12px; }
  .faq summary::-webkit-details-marker { display: none; }
  .faq summary::before { content: 'Q'; color: var(--c-eg); font-weight: 900; }
  .faq details[open] summary { border-bottom: 1px solid var(--line); }
  .faq .ans { padding: 14px 20px 18px 48px; font-size: 15px; line-height: 1.9; color: var(--ink-soft); }
  @media (max-width: 720px) { .faq .ans { padding-left: 20px; } .content-card { padding: 20px; } }
</style>
"""
if ".content-card" not in s:
    s = s.replace("</style>", "</style>" + EXTRA_CSS, 1)


def chip(k, name):
    return f'<span class="chip {k}">{name}</span>'


# ───────── 新しいセクション ─────────
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import posts as _P
from scoreboard import zone as _zone
_m = _P.POSTS[-1]                                  # いちばん新しい記事
_jn, _jk = _zone(_m.JP_SCORE)
_un, _uk = _zone(_m.US_SCORE)
_ex = getattr(_m, "CARD_EXCERPT", _m.EXCERPT)
LATEST = f"""
  <!-- 最新の市況ブログ -->
  <section class="block" id="latest">
    <div class="wrap">
      <h2>最新の市況ブログ</h2>
      <p class="sec-lead">その日の日本株・米国株の動きと経済ニュースを、恐怖と強欲指数とあわせて表で整理しています。</p>
      <a class="content-card latest-card" href="/blog/{_m.DATE_ID}">
        <div class="meta"><span>{_P.full_label(_m)}</span><span>日本株 <strong>{_m.JP_SCORE}</strong> {chip(_jk, _jn)}</span><span>米国株 <strong>{_m.US_SCORE}</strong> {chip(_uk, _un)}</span></div>
        <div class="ttl">{_m.TITLE}</div>
        <div class="ex">{_ex}</div>
      </a>
      <div class="btn-row"><a href="/blog">ブログ一覧を見る</a><a class="sub" href="/archive">市況アーカイブを見る</a></div>
    </div>
  </section>
"""

STATS_TEASER = """
  <!-- 独自データ（統計） -->
  <section class="block" id="stats-teaser">
    <div class="wrap">
      <h2>独自データ：区分別の統計（試験公開）</h2>
      <p class="sec-lead">指数が各区分にあった日の、その後の日経平均の動きを過去のデータで集計しました。局面の数や全期間との比較とあわせて確認できます。</p>
      <div class="btn-row"><a href="/stats">統計データを見る</a></div>
    </div>
  </section>
"""

WHAT = """
  <!-- 恐怖と強欲指数とは -->
  <section class="block" id="about-index">
    <div class="wrap">
      <h2>恐怖と強欲指数とは？</h2>
      <div class="content-card">
        <p>恐怖と強欲指数（Fear &amp; Greed Index）は、株式市場に参加する人たちの心理が「恐怖」と「強欲」のどちらに傾いているかを、0〜100の数値で表した指標です。数値が低いほど恐怖（売りが優勢になりやすい状態）、高いほど強欲（買いが優勢になりやすい状態）を示します。</p>
        <p>もとになったのは、米国のCNN Businessが公表しているFear &amp; Greed Indexです。株価の勢い、値動きの大きさ、売買の偏り、債券市場の動きなど、性質の異なる複数の指標を1つの数値にまとめることで、市場の雰囲気を多面的に捉えられます。</p>
        <p>当サイトでは、米国株はCNN Businessの公表値をそのまま表示し、日本株は日経225などのデータから独自に算出した値を表示しています。日本株の指数には、株価の動きに加えて、日本市場に影響しやすい為替（ドル円）と国債利回りも組み込んでいます。</p>
        <div class="table-scroll" style="margin-top:20px"><table class="method">
          <thead><tr><th>ポイント</th><th>内容</th></tr></thead>
          <tbody>
            <tr><th class="w-s top">何を表すか</th><td class="top">市場参加者の心理（勢い・不安・安全資産への動き）を数値にしたものです。株価の水準そのものではありません。</td></tr>
            <tr><th class="w-s top">何に使うか</th><td class="top">いまの市場の温度感を知るための参考情報です。売買のタイミングを示すものではありません。</td></tr>
            <tr><th class="w-s top">気をつける点</th><td class="top">過去のデータに基づく数値で、将来の値動きを予測・保証するものではありません。</td></tr>
          </tbody>
        </table></div>
        <p style="margin-top:16px">くわしい読み方は<a class="inline" href="/guide">投資ガイド</a>、日々の記録は<a class="inline" href="/archive">市況アーカイブ</a>をご覧ください。</p>
      </div>
    </div>
  </section>
"""

ZONE_GUIDE = """
  <!-- 区間別の考え方ガイド -->
  <section class="block" id="zone-guide">
    <div class="wrap">
      <h2>区間別の投資の考え方ガイド</h2>
      <p class="sec-lead">指数の区分ごとに、一般に言われる市場の状態と、投資の判断材料として考えられる視点を整理しました。特定の売買を勧めるものではなく、ご自身の投資方針を考えるときの参考としてお使いください。</p>
      <div class="method-card">
        <div class="table-scroll">
          <table class="method">
            <thead><tr><th>区分</th><th>市場の状態</th><th>過去に見られた傾向</th><th>考え方の視点</th><th>注意点</th></tr></thead>
            <tbody>
              <tr><td class="top"><strong>極度の恐怖</strong><br>0〜24<br>""" + chip("ef", "EXTREME FEAR") + """</td>
                  <td class="top">不安が極端に強まり、売りが売りを呼びやすい状態です。</td>
                  <td class="top">急落局面で観測され、その後に持ち直した例がある一方、下落が続いた例もあります。</td>
                  <td class="top">「安いから買う」と決めつけず、生活資金や投資資金の余裕、分散の度合いを先に確認します。買い増しを検討する場合も、時期を分ける考え方があります。</td>
                  <td class="top">底を見極めるのは困難です。この水準が長く続くこともあります。</td></tr>
              <tr><td class="top"><strong>恐怖</strong><br>25〜44<br>""" + chip("f", "FEAR") + """</td>
                  <td class="top">慎重な姿勢が広がり、様子見が増える状態です。</td>
                  <td class="top">値動きが荒くなりやすく、悪材料に敏感になりやすいとされます。</td>
                  <td class="top">積立投資を続けている場合は、あらかじめ決めた方針を守るという考え方があります。新規の投資は資金配分を意識して検討します。</td>
                  <td class="top">「恐怖」から「極度の恐怖」へ進むこともあります。</td></tr>
              <tr><td class="top"><strong>中立</strong><br>45〜54<br>""" + chip("n", "NEUTRAL") + """</td>
                  <td class="top">恐怖と強欲が拮抗し、方向感を探っている状態です。</td>
                  <td class="top">材料待ちで値動きが限られる場面が多いとされます。</td>
                  <td class="top">指数以外の材料（業績、金利、為替、イベント）を中心に確認します。</td>
                  <td class="top">「中立」は安全を意味しません。方向が変わる前の静けさのこともあります。</td></tr>
              <tr><td class="top"><strong>強欲</strong><br>55〜74<br>""" + chip("g", "GREED") + """</td>
                  <td class="top">上昇への期待が高まり、買いが優勢な状態です。</td>
                  <td class="top">上昇が続く局面と、過熱感から調整に転じる局面があります。</td>
                  <td class="top">利益が出ている場合は、保有比率が当初の方針から大きくずれていないかを点検する人もいます。</td>
                  <td class="top">強欲の水準でも上昇が続くことがあります。追いかけ買いには慎重さが求められます。</td></tr>
              <tr><td class="top"><strong>極度の強欲</strong><br>75〜100<br>""" + chip("eg", "EXTREME GREED") + """</td>
                  <td class="top">楽観が極端に広がり、過熱感が意識される状態です。</td>
                  <td class="top">過熱の後に調整が入った例がある一方、その後も上昇が続いた例もあります。</td>
                  <td class="top">「他の人が強欲なときは慎重に」という投資格言がよく引き合いに出されます。大きな新規投資は、資金配分を見直してから検討します。</td>
                  <td class="top">天井を見極めるのは困難です。</td></tr>
            </tbody>
          </table>
        </div>
        <div class="callout warn"><p>上の表は、一般的な考え方の整理です。個別の金融商品の売買を勧誘・推奨するものではなく、将来の値動きを予測・保証するものでもありません。投資に関する最終判断は、ご自身の責任で行ってください。</p></div>
      </div>
    </div>
  </section>
"""

HOWTO = """
  <!-- 実践的な使い方 -->
  <section class="block" id="howto">
    <div class="wrap">
      <h2>恐怖と強欲指数の実践的な使い方</h2>
      <p class="sec-lead">数値を見るだけでなく、「何を、どの順番で見るか」を決めておくと、日々の値動きに振り回されにくくなります。</p>
      <div class="method-card">
        <div class="table-scroll">
          <table class="method">
            <thead><tr><th>手順</th><th>見るもの</th><th>ポイント</th></tr></thead>
            <tbody>
              <tr><th class="w-s top">1. 日米を並べて見る</th><td class="top">日本株と米国株の指数</td><td class="top">同じ方向か、離れているかを確認します。差が大きい日は、金融政策・為替・決算など、市場ごとの事情を調べます。</td></tr>
              <tr><th class="w-s top">2. 変化の方向を見る</th><td class="top">前日・1週間前・1か月前との比較</td><td class="top">水準だけでなく、恐怖の中で持ち直しているのか、悪化しているのかを見ます。</td></tr>
              <tr><th class="w-s top">3. 内訳を確認する</th><td class="top">構成する指標の点数</td><td class="top">指数を押し下げている（押し上げている）指標はどれか。1つの指標に偏っていないかを確認します。</td></tr>
              <tr><th class="w-s top">4. 流れを見る</th><td class="top">直近30日の推移グラフ</td><td class="top">一時的な動きか、続いている流れかを判断します。区分をまたいだ日は、その理由を確認します。</td></tr>
              <tr><th class="w-s top">5. 他の情報で補う</th><td class="top">決算・金利・為替・経済指標・ニュース</td><td class="top">指数は「なぜそうなったか」を教えてくれません。理由は他の情報で補います。</td></tr>
              <tr><th class="w-s top">6. 自分のルールを決める</th><td class="top">投資期間・比率・追加投資の上限</td><td class="top">相場が荒れる前に、見直しの頻度や資金配分を決めておくと、感情に流されにくくなります。</td></tr>
            </tbody>
          </table>
        </div>
        <h3 style="font-size:16px;font-weight:700;margin:28px 0 8px">よくある使い方の間違い</h3>
        <div class="table-scroll">
          <table class="method">
            <thead><tr><th>ありがちな使い方</th><th>望ましい考え方</th></tr></thead>
            <tbody>
              <tr><td class="top">「恐怖だから買い、強欲だから売り」と機械的に判断する</td><td class="top">指数は将来を予測しません。判断材料の1つとして使います。</td></tr>
              <tr><td class="top">毎日の小さな数値の上下に一喜一憂する</td><td class="top">区分の変化や、1週間・1か月の流れを見ます。</td></tr>
              <tr><td class="top">この指数だけで売買を決める</td><td class="top">業績、割安・割高の度合い、資金計画など、他の情報もあわせて確認します。</td></tr>
              <tr><td class="top">日本株と米国株の数値の高低を単純に比べる</td><td class="top">算出方法が異なります。それぞれの推移や区分の変化を見ます。</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
"""

CAUTIONS = """
  <!-- 注意事項 -->
  <section class="block" id="cautions">
    <div class="wrap">
      <h2>投資をするときに必ず知っておきたい注意事項</h2>
      <p class="sec-lead">恐怖と強欲指数を使う前に、投資全般に共通する基本事項と、当サイトの指数の特性を確認してください。</p>
      <div class="method-card">
        <div class="table-scroll">
          <table class="method">
            <thead><tr><th>項目</th><th>内容</th></tr></thead>
            <tbody>
              <tr><th class="w-s top">元本割れのリスク</th><td class="top">株式や投資信託は価格が変動し、投資した元本を割り込むことがあります。投資は余裕資金で行い、生活のための資金は別に確保しておくことが基本とされています。</td></tr>
              <tr><th class="w-s top">指数は予測ではない</th><td class="top">恐怖と強欲指数は現在の市場心理を示すもので、将来の値動きを予測・保証するものではありません。</td></tr>
              <tr><th class="w-s top">過去は将来を保証しない</th><td class="top">極度の恐怖の後に反発した例があっても、同じ結果になるとは限りません。</td></tr>
              <tr><th class="w-s top">単独で判断しない</th><td class="top">業績、財務、割安・割高の度合い、金利や為替の動き、ご自身の資金計画とあわせて検討します。</td></tr>
              <tr><th class="w-s top">当サイトの日本株指数の特性</th><td class="top">当サイト独自の算出で、各指標を過去1年の中での相対的な位置として評価し、直近3営業日の平均で表示します。CNNの指数とは構成が異なり、水準を直接比べることはできません。データの遅延や欠落が生じる場合があります。</td></tr>
              <tr><th class="w-s top">為替リスク</th><td class="top">米国株など外貨建ての資産は、円換算の損益が為替の変動の影響を受けます。</td></tr>
              <tr><th class="w-s top">レバレッジ・信用取引</th><td class="top">少ない資金で大きな取引ができる反面、損失が投資した資金を上回ることがあります。仕組みとリスクを十分に理解してから判断します。</td></tr>
              <tr><th class="w-s top">税金・制度の変更</th><td class="top">NISAなどの制度や税制は改正されることがあります。最新の情報は、金融庁や各金融機関の公式サイトでご確認ください。</td></tr>
              <tr><th class="w-s top">情報の出どころ</th><td class="top">SNSやブログの情報は、真偽や利害関係が不明なことがあります。投資の勧誘や詐欺にも注意し、不安なときは登録のある金融機関や公的な相談窓口に相談してください。</td></tr>
            </tbody>
          </table>
        </div>
        <div class="callout warn"><p>当サイトは、金融商品取引法に基づく投資助言・代理業その他の金融商品取引業を行うものではありません。掲載情報は参考情報であり、投資の最終判断はご自身の責任で行ってください。</p></div>
      </div>
    </div>
  </section>
"""

FAQ = [
    ("日本株の恐怖と強欲指数は、どんなデータで計算していますか？",
     "日経225、TOPIX連動ETF、ドル円、日本の10年国債利回りを使い、6つの指標を「過去1年の中での位置」で0〜100に換算して加重平均し、直近3営業日の平均を表示しています。くわしくは、このページ下部の「指数の算出方法」をご覧ください。"),
    ("日本株と米国株で、指数の水準が違うのはなぜですか？",
     "米国株はCNN Businessが公表する7指標の指数、日本株は当サイト独自の6指標の指数です。構成も計算方法も異なるため、水準を直接比べるのではなく、それぞれの推移や区分の変化を見るのが適しています。"),
    ("指数が「恐怖」のとき、株価は必ず下がりますか？",
     "いいえ。恐怖と強欲指数は現在の心理を示すもので、株価の将来を示すものではありません。恐怖の水準でも株価が上がる日はありますし、下落が続くこともあります。日経平均が大きく上がった日でも、指数が「恐怖」にとどまることがあります。"),
    ("指数を見て売買のタイミングを決めてもよいですか？",
     "指数は判断材料の1つです。業績や金利、為替、ご自身の資金計画とあわせて検討することが大切です。当サイトは、特定の金融商品の売買を勧誘・推奨するものではありません。"),
    ("新NISAで積立をしています。指数を気にした方がよいですか？",
     "積立投資は、一定額を定期的に購入して購入価格をならす考え方で、短期の心理指標とは目的が異なります。指数は「いまの市場の温度感を知るための参考情報」として見るのが一般的です。制度の詳細は、金融庁や金融機関の公式情報でご確認ください。"),
    ("タイトルに「リアルタイム」とありますが、秒単位で更新されますか？",
     "秒単位の更新ではありません。日本の取引時間中は約1時間ごと、米国の取引時間中は約2時間ごとに自動で更新します。データ提供元の都合で遅れる場合があり、国債利回りなど一部のデータは前営業日のものを使います。"),
    ("日経平均VIやVIX指数とは何が違いますか？",
     "VIXや日経平均VIは、オプション価格から算出される「今後の予想変動率」で、不安という1つの側面を測ります。恐怖と強欲指数は、そうした要素を含む複数の指標をまとめた、総合的な心理の指数です。比較表は投資ガイドで解説しています。"),
    ("過去の推移や、その日の解説はどこで見られますか？",
     "営業日ごとの記録は「市況アーカイブ」、その日のニュースと指標の内訳の解説は「ブログ」でご覧いただけます。"),
]
faq_html = "\n".join(
    f'        <details><summary>{q}</summary><div class="ans">{a}</div></details>' for q, a in FAQ)
FAQ_SEC = f"""
  <!-- よくある質問 -->
  <section class="block" id="faq">
    <div class="wrap">
      <h2>よくある質問</h2>
      <div class="faq">
{faq_html}
      </div>
    </div>
  </section>
"""
faq_ld = {
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
}
FAQ_LD = '<script type="application/ld+json">\n' + json.dumps(faq_ld, ensure_ascii=False, indent=2) + "\n</script>\n"

# ───────── 挿入（既に入っていれば一旦取り除いてから入れ直す：冪等） ─────────
for sid in ("latest", "about-index", "stats-teaser", "zone-guide", "howto", "cautions", "faq"):
    s = re.sub(r'\n  <!-- [^\n]*-->\n  <section class="block" id="%s">.*?</section>\n' % sid, "", s, flags=re.S)
s = re.sub(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "FAQPage".*?</script>\n', "", s, flags=re.S)

# 推移(#history)の直後：最新ブログ + 指数とは
s, n = re.subn(r'(  </section>\n)(\n  <!-- ゾーン -->)', lambda m: m.group(1) + LATEST + WHAT + STATS_TEASER + m.group(2), s, count=1)
assert n == 1, "history/zones boundary not found"
# 数値の見方(#zones)の直後：区間別ガイド + 使い方 + 注意事項 + FAQ
s, n = re.subn(r'(  </section>\n)(\n  <!-- 算出方法 -->)', lambda m: m.group(1) + ZONE_GUIDE + HOWTO + CAUTIONS + FAQ_SEC + m.group(2), s, count=1)
assert n == 1, "zones/method boundary not found"
# FAQ 構造化データ（head の WebSite の後）
s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', FAQ_LD + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)

open(PATH, "w", encoding="utf-8").write(s)
print("index.html を更新しました：", len(s), "bytes")
