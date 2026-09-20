# -*- coding: utf-8 -*-
"""about.html / guide.html 생성 스크립트 (공통 헤더·푸터·스타일을 한 곳에서 관리)"""
import json, html

SITE = "https://feargreedjapan.com"

# ─────────────────────────────────────────────
# ★ 운영자 정보 (여기 3개만 채우고 다시 빌드하면 모든 페이지에 반영됨)
#   None 이면 노란색 "要入力" 표시가 나옵니다.
# ─────────────────────────────────────────────
GSC_TOKEN = "HoU_nbY9is8mGhPZ6eENVWpMUnDZx3JJAhnjUdSYqHg"   # Google Search Console 所有権確認
OPERATOR = "Fear & Greed Index Japan 運営事務局"   # 屋号（個人名は非公開）
EMAIL = "okpika2006@gmail.com"
PUBLISH_DATE = "2026年9月20日"


def val(v, label):
    import html as _h
    if not v:
        return f'<span class="todo">［要入力：{label}］</span>'
    if "@" in v and " " not in v:
        return f'<a class="inline" href="mailto:{_h.escape(v)}">{_h.escape(v)}</a>'
    return _h.escape(v)

# ─────────────────────────────────────────────
# 공통 CSS (index.html 과 같은 색·폰트 토큰)
# ─────────────────────────────────────────────
CSS = """
  :root {
    --ink: #14284b; --ink-soft: #3a4d70; --paper: #f6f8fb; --surface: #ffffff;
    --line: #dfe5ee; --muted: #6b7a94;
    --c-ef: #b3261e; --c-f: #d9822b; --c-n: #8a94a6; --c-g: #3b8f6b; --c-eg: #1f6fb2;
    --radius: 10px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'Noto Sans JP','Hiragino Kaku Gothic ProN','Yu Gothic',Meiryo,sans-serif;
    background: var(--paper); color: var(--ink);
    line-height: 1.8; font-size: 15px; -webkit-font-smoothing: antialiased;
  }
  a { color: inherit; }
  a:focus-visible, button:focus-visible { outline: 3px solid var(--c-eg); outline-offset: 2px; }

  .site-header { background: var(--ink); color: #fff; }
  .site-header .inner {
    max-width: 1080px; margin: 0 auto; padding: 0 24px; height: 60px;
    display: flex; align-items: center; justify-content: space-between; gap: 24px;
  }
  .brand { font-weight: 900; font-size: 18px; letter-spacing: .02em; text-decoration: none; color: #fff; white-space: nowrap; }
  .brand small { font-weight: 500; font-size: 12px; opacity: .7; margin-left: 10px; }
  .nav { display: flex; gap: 4px; }
  .nav a { color: #cdd7ea; text-decoration: none; font-size: 14px; font-weight: 500; padding: 8px 14px; border-radius: 6px; }
  .nav a:hover { background: rgba(255,255,255,.08); color: #fff; }
  .nav a[aria-current="page"] { color: #fff; background: rgba(255,255,255,.14); }
  @media (max-width: 720px) {
    .site-header .inner { height: auto; padding: 12px 16px; flex-direction: column; align-items: flex-start; gap: 8px; }
    .brand small { display: none; }
    .nav { flex-wrap: wrap; }
    .nav a { padding: 6px 10px; font-size: 13px; }
  }

  .notice-bar { background: #eaf0f9; border-bottom: 1px solid var(--line); color: var(--ink-soft); font-size: 12.5px; text-align: center; padding: 8px 16px; }
  .wrap { max-width: 1080px; margin: 0 auto; padding: 0 24px; }
  @media (max-width: 720px) { .wrap { padding: 0 16px; } }

  /* ── 記事レイアウト ── */
  .article { max-width: 760px; margin: 0 auto; padding: 40px 0 8px; }
  .crumbs { font-size: 12.5px; color: var(--muted); margin-bottom: 20px; }
  .crumbs a { text-decoration: none; }
  .crumbs a:hover { text-decoration: underline; }
  .crumbs span { margin: 0 6px; }

  .article h1 { font-size: clamp(26px, 4vw, 34px); font-weight: 900; line-height: 1.45; text-wrap: balance; }
  .article .lead { margin-top: 16px; color: var(--ink-soft); font-size: 16px; line-height: 1.95; }

  .toc { margin: 32px 0 8px; padding: 20px 24px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
  .article .toc h2 { font-size: 14px; font-weight: 700; color: var(--ink-soft); margin: 0 0 8px; padding: 0; border: none; line-height: 1.6; }
  .toc ol { padding-left: 1.4em; font-size: 14.5px; }
  .toc li { padding: 3px 0; }
  .toc a { text-decoration: none; color: var(--ink); }
  .toc a:hover { text-decoration: underline; }

  .article section { padding-top: 44px; scroll-margin-top: 16px; }
  .article h2 { font-size: 22px; font-weight: 900; line-height: 1.5; padding-left: 14px; border-left: 5px solid var(--ink); margin-bottom: 16px; }
  .article h3 { font-size: 17px; font-weight: 700; margin: 26px 0 8px; }
  .article p { font-size: 16px; line-height: 1.95; color: #24365a; margin-top: 14px; }
  .article section > h2 + p { margin-top: 0; }
  .article ul { margin: 14px 0 0 1.3em; }
  .article li { font-size: 16px; line-height: 1.9; color: #24365a; padding: 2px 0; }
  .article a.inline { color: var(--c-eg); text-underline-offset: 3px; }

  .table-scroll { overflow-x: auto; margin-top: 16px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); }
  table.doc { width: 100%; border-collapse: collapse; font-size: 14.5px; min-width: 520px; }
  table.doc th, table.doc td { text-align: left; padding: 12px 16px; border-bottom: 1px solid var(--line); vertical-align: top; line-height: 1.7; }
  table.doc tr:last-child th, table.doc tr:last-child td { border-bottom: none; }
  table.doc thead th { background: #f2f5fa; color: var(--ink-soft); font-weight: 700; white-space: nowrap; }
  table.doc tbody th { font-weight: 700; white-space: nowrap; background: #fafbfd; width: 9em; }
  .article ol.clauses { margin: 12px 0 0 1.7em; }
  .article ol.clauses > li { padding: 3px 0 3px .2em; }
  .article ol.paren { list-style: none; counter-reset: p; margin: 12px 0 0; }
  .article ol.paren > li { counter-increment: p; position: relative; padding-left: 2.8em; }
  .article ol.paren > li::before { content: "(" counter(p) ")"; position: absolute; left: 0; color: var(--ink-soft); font-variant-numeric: tabular-nums; }
  .enact { margin-top: 36px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 14px; color: var(--muted); }
  @media (max-width: 720px) {
    table.doc.stack { min-width: 0; }
    table.doc.stack thead { display: none; }
    table.doc.stack, table.doc.stack tbody, table.doc.stack tr, table.doc.stack th, table.doc.stack td { display: block; width: auto; }
    table.doc.stack tr { padding: 12px 0; border-bottom: 1px solid var(--line); }
    table.doc.stack tr:last-child { border-bottom: none; }
    table.doc.stack tbody th { background: none; white-space: normal; border: none; padding: 2px 16px 6px; }
    table.doc.stack td { border: none; padding: 4px 16px; }
    table.doc.stack td::before { content: attr(data-label); display: block; font-size: 12px; font-weight: 700; color: var(--muted); margin-bottom: 1px; }
  }
  table.doc.narrow { min-width: 0; }
  table.doc.narrow tbody th { width: 8em; white-space: normal; }
  @media (max-width: 720px) { table.doc.narrow tbody th { width: 6.5em; } }
  .zone-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: baseline; }

  .callout { margin-top: 20px; padding: 16px 20px; background: #eef3fb; border-left: 4px solid var(--ink); border-radius: 4px; }
  .callout p { margin: 0; font-size: 15px; line-height: 1.85; }
  .callout.warn { background: #fff8ec; border-left-color: #d9a441; }
  .callout.warn p { color: #6a5320; }

  .faq { margin-top: 8px; }
  .faq details { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); margin-top: 10px; }
  .faq summary { cursor: pointer; padding: 16px 20px; font-weight: 700; font-size: 16px; line-height: 1.6; list-style: none; display: flex; gap: 12px; }
  .faq summary::-webkit-details-marker { display: none; }
  .faq summary::before { content: 'Q'; color: var(--c-eg); font-weight: 900; }
  .faq details[open] summary { border-bottom: 1px solid var(--line); }
  .faq .ans { padding: 14px 20px 18px 48px; font-size: 15.5px; line-height: 1.9; color: #24365a; }

  .todo { background: #fff3a3; padding: 1px 6px; border-radius: 3px; font-weight: 700; color: #6b4e00; }

  .cta { margin: 48px 0 0; padding: 24px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); text-align: center; }
  .cta p { margin: 0 0 14px; font-size: 15px; }
  .cta a { display: inline-block; background: var(--ink); color: #fff; text-decoration: none; font-weight: 700; padding: 12px 28px; border-radius: 6px; }
  .cta a:hover { background: #0e1d38; }

  .disclaimer { margin: 40px auto 0; max-width: 760px; padding: 20px 24px; background: #fff8ec; border: 1px solid #f0dcb6; border-radius: var(--radius); font-size: 13px; color: #6a5320; }
  .disclaimer strong { display: block; margin-bottom: 4px; }

  footer.site-footer { margin-top: 56px; background: var(--ink); color: #b9c6df; padding: 36px 0 28px; font-size: 13px; }
  .footer-links { display: flex; flex-wrap: wrap; gap: 8px 24px; margin-bottom: 16px; }
  .footer-links a { color: #dbe4f5; text-decoration: none; }
  .footer-links a:hover { text-decoration: underline; }
  .footer-copy { opacity: .8; font-size: 12px; }

  @media (max-width: 720px) {
    .article { padding-top: 28px; }
    .article h2 { font-size: 20px; }
    .article p, .article li { font-size: 15.5px; }
    .faq .ans { padding-left: 20px; }
  }

  .article.wide { max-width: 900px; }
  .article h1 { text-wrap: balance; }
  .article small.sub { color: var(--muted); font-size: 12.5px; }
  .eyebrow { font-size: 13px; font-weight: 700; color: var(--c-eg); letter-spacing: .04em; margin-bottom: 8px; }

  /* 区分チップ */
  .chip { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 10px; border-radius: 999px; color: #fff; background: var(--c-n); white-space: nowrap; }
  .chip.ef { background: var(--c-ef); } .chip.f { background: var(--c-f); } .chip.n { background: var(--c-n); }
  .chip.g { background: var(--c-g); } .chip.eg { background: var(--c-eg); }
  .num { font-variant-numeric: tabular-nums; }

  /* 統計バー */
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin: 24px 0 8px; }
  .stat { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 14px 16px; }
  .stat b { display: block; font-size: 24px; font-weight: 900; line-height: 1.3; font-variant-numeric: tabular-nums; }
  .stat span { font-size: 12px; color: var(--muted); }

  /* フィルター・ページャー */
  .filters { display: flex; flex-wrap: wrap; gap: 8px; margin: 20px 0 4px; align-items: center; }
  .filters .lab { font-size: 13px; color: var(--muted); margin-right: 4px; }
  .filters button, .pager button { font: inherit; font-size: 13.5px; font-weight: 700; padding: 7px 14px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--ink-soft); cursor: pointer; }
  .filters button:hover, .pager button:hover { border-color: var(--ink-soft); }
  .filters button[aria-pressed="true"], .pager button[aria-current="true"] { background: var(--ink); color: #fff; border-color: var(--ink); }
  .pager { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin: 24px 0 0; }
  .pager button { min-width: 38px; padding: 6px 10px; border-radius: 8px; }

  /* アーカイブの1日分 */
  .day { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 16px 20px; margin-top: 12px; }
  .day-head { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
  .day-date { font-weight: 900; font-size: 16px; }
  .day-score { font-size: 14px; color: var(--ink-soft); display: inline-flex; gap: 6px; align-items: center; }
  .day-score b { font-size: 18px; font-variant-numeric: tabular-nums; color: var(--ink); }
  .day p { margin-top: 8px; font-size: 14.5px; line-height: 1.85; color: #24365a; }
  .day a.more { font-size: 13px; color: var(--c-eg); text-underline-offset: 3px; }
  .note-small { font-size: 13px; color: var(--muted); margin-top: 16px; line-height: 1.8; }

  /* ブログ一覧 */
  .post-item { display: block; text-decoration: none; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 20px 22px; margin-top: 14px; }
  .post-item:hover { border-color: var(--ink-soft); }
  .post-meta { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; font-size: 13px; color: var(--muted); }
  .post-title { font-size: 19px; font-weight: 900; line-height: 1.55; margin-top: 8px; color: var(--ink); }
  .post-excerpt { font-size: 14.5px; color: var(--ink-soft); margin-top: 8px; line-height: 1.85; }

  /* ブログ記事 */
  .post-label { font-size: 13px; font-weight: 700; color: var(--c-eg); }
  .summary-box { margin: 24px 0 8px; padding: 18px 22px; background: #eef3fb; border: 1px solid #d5e0f2; border-radius: var(--radius); }
  .summary-box h2 { font-size: 15px !important; border: none !important; padding: 0 !important; margin: 0 0 8px !important; color: var(--ink-soft); }
  .summary-box ul { margin: 0 0 0 1.2em; }
  .summary-box li { font-size: 15.5px; padding: 3px 0; }
  .tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 28px; }
  .tags span { font-size: 13px; color: var(--ink-soft); background: #eef2f8; padding: 4px 12px; border-radius: 999px; }
  .sources { margin-top: 36px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 13px; color: var(--muted); line-height: 1.9; }
  .article table.doc td.r, .article table.doc th.r { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .article h3.tblcap { font-size: 15px; margin: 22px 0 6px; color: var(--ink-soft); }
  .lead-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
  .lead-links a { font-size: 14px; font-weight: 700; text-decoration: none; padding: 9px 18px; border-radius: 8px; background: var(--ink); color: #fff; }
  .lead-links a.sub { background: var(--surface); color: var(--ink); border: 1px solid var(--line); }

  @media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
"""

NAV = [
    ("/", "ダッシュボード", "index"),
    ("/archive", "市況アーカイブ", "archive"),
    ("/blog", "ブログ", "blog"),
    ("/guide", "投資ガイド", "guide"),
    ("/about", "サイトについて", "about"),
]


def shell(page_id, title, description, path, crumb_label, body, extra_ld=None, wide=False, og_type="article", crumbs=None, extra_head=""):
    import re as _re
    _amp = lambda t: _re.sub(r"&(?!amp;|lt;|gt;|quot;|#)", "&amp;", t)
    title, description = _amp(title), _amp(description)
    nav = "\n".join(
        f'      <a href="{h}"{" aria-current=\"page\"" if pid == page_id else ""}>{label}</a>'
        for h, label, pid in NAV
    )
    # パンくず：既定は「ホーム > ページ名」。3階層以上は crumbs=[(名前, パス or None), ...] で指定
    items = crumbs if crumbs else [(crumb_label, None)]
    trail = [("ホーム", "/")] + [(n, p) for n, p in items]
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + (p if p else path)}
            for i, (n, p) in enumerate(trail)
        ],
    }
    crumb_html = "<span>&gt;</span>".join(
        (f'<a href="{p}">{n}</a>' if p else n) for n, p in trail
    )
    lds = [breadcrumb] + (extra_ld if isinstance(extra_ld, list) else ([extra_ld] if extra_ld else []))
    ld_html = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n</script>' for x in lds
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google-site-verification" content="{GSC_TOKEN}" />
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Fear &amp; Greed Index Japan">
<meta property="og:image" content="{SITE}/thumbnail.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE}/thumbnail.png">
<meta name="theme-color" content="#14284b">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{extra_head}
{ld_html}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">

<!-- ▼ 公開前に、新しいGA4のIDに置き換える（index.html と同じ値） -->
<!--
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');</script>
-->
<!-- ▼ AdSense承認後に有効化（既存アカウントのpub IDをそのまま使用。アカウントは新規作成せず「サイトを追加」で登録） -->
<!--
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
-->

<style>{CSS}</style>
</head>
<body>

<header class="site-header">
  <div class="inner">
    <a class="brand" href="/">Fear &amp; Greed Index Japan<small>恐怖と強欲指数</small></a>
    <nav class="nav" aria-label="メインメニュー">
{nav}
    </nav>
  </div>
</header>

<div class="notice-bar">
  本サイトは投資判断の助言を目的としたものではありません。投資はご自身の判断と責任でお願いします。
</div>

<main>
  <div class="wrap">
    <article class="article{" wide" if wide else ""}">
      <nav class="crumbs" aria-label="パンくずリスト">{crumb_html}</nav>
{body}
    </article>

    <div class="disclaimer">
      <strong>ご利用にあたっての注意</strong>
      本サイトの情報は、投資家心理を数値化した参考情報であり、特定の金融商品の売買を勧誘・推奨するものではありません。指数は過去のデータに基づく参考値で、将来の値動きを予測・保証するものではありません。掲載データの正確性には努めていますが、遅延・誤り・欠落が生じる場合があります。投資に関する最終判断は、ご自身の責任で行ってください。
    </div>
  </div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-links">
      <a href="/">ダッシュボード</a>
      <a href="/archive">市況アーカイブ</a>
      <a href="/blog">ブログ</a>
      <a href="/guide">投資ガイド</a>
      <a href="/about">サイトについて</a>
      <a href="/terms">利用規約</a>
      <a href="/privacy">プライバシーポリシー</a>
    </div>
    <p class="footer-copy">© 2026 Fear &amp; Greed Index Japan. All rights reserved.<br>「日経225」は株式会社日本経済新聞社の登録商標です。本サイトは同社とは関係ありません。</p>
  </div>
</footer>

</body>
</html>
"""


def toc(items):
    lis = "\n".join(f'        <li><a href="#{i}">{t}</a></li>' for i, t in items)
    return f"""      <nav class="toc" aria-label="目次">
        <h2>このページの内容</h2>
        <ol>
{lis}
        </ol>
      </nav>"""


# ═════════════════════════════════════════════
#  サイトについて (about.html)
# ═════════════════════════════════════════════
def build_about():
    items = [
        ("purpose", "このサイトの目的"),
        ("indices", "提供している指数"),
        ("data", "データの出典と取り扱い"),
        ("policy", "運営方針"),
        ("operator", "運営者情報"),
        ("ip", "商標・著作権について"),
    ]
    body = f"""
      <h1>サイトについて</h1>
      <p class="lead">Fear &amp; Greed Index Japanは、日本株と米国株の「投資家心理」を0〜100の数値で毎日確認できる情報サイトです。</p>

{toc(items)}

      <section id="purpose">
        <h2>このサイトの目的</h2>
        <p>株価が上がったのか下がったのかは、ニュースやチャートですぐに確認できます。一方で、市場に参加している人たちが「いまどのくらい不安なのか」「どのくらい強気なのか」は、数字になっていないため目に見えにくいものです。</p>
        <p>当サイトは、その市場の空気感を0〜100の数値にして、日本株と米国株を並べて見られるようにすることを目的としています。売買をおすすめするためのサイトではなく、いまの市場の温度感を知るための参考情報を提供するものです。</p>
      </section>

      <section id="indices">
        <h2>提供している指数</h2>
        <p>当サイトでは、次の2つの指数を表示しています。</p>
        <div class="table-scroll">
          <table class="doc narrow">
            <tbody>
              <tr><th>日本株の指数</th><td>当サイト独自の算出。日経225・TOPIX連動ETFなどが基準</td></tr>
              <tr><th>米国株の指数</th><td>CNN Businessの公表値をそのまま表示。S&amp;P500などが基準</td></tr>
              <tr><th>表示の更新</th><td>日本の取引時間中は約1時間ごと、米国の取引時間中は約2時間ごとに自動更新（休場日は更新なし）</td></tr>
            </tbody>
          </table>
        </div>
        <p>日本株の指数は、CNN Businessの指数の考え方を参考にしつつ、日本市場のデータで当サイトが独自に算出しています。そのため、米国株の指数とは指標の構成が異なり、数値の水準をそのまま比べることはできません。算出に使う指標とウェイトは、<a class="inline" href="/#method">ダッシュボードの「指数の算出方法」</a>で公開しています。</p>
      </section>

      <section id="data">
        <h2>データの出典と取り扱い</h2>
        <ul>
          <li>日経225、TOPIX連動ETF、為替（ドル円）は Yahoo Finance の公開データ、国債利回りは財務省が公表するデータを利用しています。</li>
          <li>米国株の指数は、CNN Businessが公表している「Fear &amp; Greed Index」の数値です。</li>
          <li>データの取得元の都合により、表示が遅れたり、一時的に取得できなかったりすることがあります。取得できない場合は、その旨を画面に表示します。</li>
          <li>算出方法や使用するデータを変更した場合は、当サイト上で明記します。</li>
        </ul>
        <div class="callout">
          <p>表示内容に誤りや不自然な数値を見つけた場合は、下記の連絡先までお知らせください。確認のうえ、必要に応じて修正します。</p>
        </div>
      </section>

      <section id="policy">
        <h2>運営方針</h2>
        <ul>
          <li>特定の銘柄や金融商品の売買を勧誘・推奨しません。</li>
          <li>将来の値動きを予測したり、断定したりする表現を避けます。</li>
          <li>指数の算出方法を公開し、誰でも確認できる状態を保ちます。</li>
          <li>当サイトは広告を掲載する場合があります。広告の内容が、指数や解説の内容に影響することはありません。</li>
        </ul>
      </section>

      <section id="operator">
        <h2>運営者情報</h2>
        <div class="table-scroll">
          <table class="doc narrow">
            <tbody>
              <tr><th>サイト名</th><td>Fear &amp; Greed Index Japan</td></tr>
              <tr><th>運営者</th><td>{val(OPERATOR, "運営者名または屋号")}</td></tr>
              <tr><th>お問い合わせ</th><td>{val(EMAIL, "連絡用メールアドレス")}</td></tr>
              <tr><th>開設</th><td>2026年</td></tr>
            </tbody>
          </table>
        </div>
        <p>お問い合わせへの返信には、数日かかる場合があります。投資に関する個別のご相談にはお答えできません。</p>
      </section>

      <section id="ip">
        <h2>商標・著作権について</h2>
        <p>「日経平均株価」「日経225」に関する著作権、商標権その他の知的財産権は、株式会社日本経済新聞社に帰属します。「S&amp;P500」「CNN」などの名称は、それぞれの権利者の商標または登録商標です。</p>
        <p>当サイトは、上記の各社とは関係がなく、各社の承認や提携を受けたものではありません。</p>
      </section>

      <div class="cta">
        <p>指数の見方や使うときの注意点は、投資ガイドで解説しています。</p>
        <a href="/guide">投資ガイドを読む</a>
      </div>
"""
    return shell(
        "about",
        "サイトについて｜Fear & Greed Index Japan",
        "Fear &amp; Greed Index Japanは、日本株と米国株の投資家心理を0〜100の数値で毎日確認できる情報サイトです。指数の算出元、データの出典、運営方針、運営者情報を掲載しています。",
        "/about",
        "サイトについて",
        body,
    )


# ═════════════════════════════════════════════
#  投資ガイド (guide.html)
# ═════════════════════════════════════════════
FAQ = [
    ("指数はいつ更新されますか？",
     "日本の取引時間中は約1時間ごと、米国の取引時間中は約2時間ごとに自動で更新します。市場の休場日は更新されません。データ提供元の状況により、更新が遅れる場合があります。"),
    ("日本株の指数と、CNNの指数は同じ方法で作られていますか？",
     "いいえ、異なります。米国株はCNN Businessが公表する数値をそのまま表示しています。日本株は、CNNの考え方を参考に、日経225などのデータから当サイトが独自に算出しています。指標の構成や算出方法が違うため、両者の数値の水準を直接比べることはできません。"),
    ("数値が低いときは「買い時」ということですか？",
     "そうとは限りません。過去には恐怖が極端に高まった後に市場が持ち直した局面もありますが、恐怖の水準のまま下落が続いた局面もあります。指数は市場の現在の心理を示すもので、将来の値動きを示すものではありません。"),
    ("過去の数値は確認できますか？",
     "ダッシュボードで直近30日の推移を確認できます。長期の履歴については、今後の拡充を検討しています。"),
    ("利用に費用や会員登録は必要ですか？",
     "現在はすべて無料で、会員登録なしにご覧いただけます。"),
]


def build_guide():
    items = [
        ("what", "恐怖と強欲指数とは"),
        ("read", "数値の読み方"),
        ("contrarian", "「逆張りの指標」と言われる理由と限界"),
        ("compare", "ほかの指標との違い"),
        ("japan", "日本の個人投資家が知っておきたい視点"),
        ("caution", "使うときの注意点"),
        ("faq", "よくある質問"),
    ]
    faq_html = "\n".join(
        f'        <details><summary>{html.escape(q)}</summary><div class="ans">{html.escape(a)}</div></details>'
        for q, a in FAQ
    )
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ
        ],
    }

    def dot(c):
        return f'<span class="zone-dot" style="background:var({c})"></span>'

    body = f"""
      <h1>恐怖と強欲指数の読み方ガイド</h1>
      <p class="lead">恐怖と強欲指数は、市場の「空気感」を0〜100で表した参考指標です。このガイドでは、数値の意味、使うときの限界、ほかの指標との違いを整理します。</p>

{toc(items)}

      <section id="what">
        <h2>恐怖と強欲指数とは</h2>
        <p>恐怖と強欲指数は、株式市場に参加する人たちの心理が「恐怖」と「強欲」のどちらに傾いているかを、0〜100の数値で表したものです。0に近いほど恐怖が強く、100に近いほど強欲が強い状態を示します。</p>
        <p>もとになったのは、米国のCNN Businessが公表しているFear &amp; Greed Indexです。株価の勢い、変動性、売買の偏り、債券市場の動きなど、性質の異なる複数の指標を1つの数値にまとめる考え方で作られています。1つの指標だけを見るよりも、市場の雰囲気を多面的に捉えやすいのが特徴です。</p>
        <p>当サイトでは、米国株についてはCNN Businessの公表値を表示し、日本株については日経225などのデータから独自に算出した値を表示しています。</p>
      </section>

      <section id="read">
        <h2>数値の読み方</h2>
        <p>当サイトでは、指数を次の5つの区分に分けています。</p>
        <div class="table-scroll">
          <table class="doc">
            <thead><tr><th>区分</th><th>数値</th><th>一般的な受け止め方</th></tr></thead>
            <tbody>
              <tr><th>{dot('--c-ef')}極度の恐怖</th><td>0〜24</td><td>不安が極端に強まり、売りが売りを呼びやすい状態</td></tr>
              <tr><th>{dot('--c-f')}恐怖</th><td>25〜44</td><td>慎重な姿勢が広がり、様子見が増えやすい状態</td></tr>
              <tr><th>{dot('--c-n')}中立</th><td>45〜54</td><td>恐怖と強欲が拮抗し、方向感を探っている状態</td></tr>
              <tr><th>{dot('--c-g')}強欲</th><td>55〜74</td><td>上昇への期待が高まり、買いが優勢な状態</td></tr>
              <tr><th>{dot('--c-eg')}極度の強欲</th><td>75〜100</td><td>楽観が広がり、過熱感が意識されやすい状態</td></tr>
            </tbody>
          </table>
        </div>
        <p>数値の水準だけでなく、「前日」「1週間前」「1か月前」と比べてどう動いたかも読み取りのヒントになります。たとえば同じ「恐怖」でも、1週間前の「極度の恐怖」から持ち直してきた場合と、「中立」から悪化してきた場合とでは、市場の流れが異なります。</p>
      </section>

      <section id="contrarian">
        <h2>「逆張りの指標」と言われる理由と限界</h2>
        <p>恐怖と強欲指数は、しばしば「逆張りの指標」として紹介されます。投資家のウォーレン・バフェット氏の「他の人が強欲なときは慎重に、他の人が恐怖を感じているときは積極的に」という趣旨の言葉が広く知られており、皆が極端に悲観しているときは売りが出尽くしやすく、皆が極端に楽観しているときは買いが出尽くしやすい、という見方につながっているためです。</p>
        <p>実際に、極度の恐怖が観測された後に市場が持ち直した局面は過去にもあります。しかし、次のような点には注意が必要です。</p>
        <ul>
          <li>恐怖の水準にとどまったまま、下落が長く続く局面もあります。</li>
          <li>強欲の水準が長く続きながら、上昇が続く局面もあります。</li>
          <li>「極度の恐怖＝底」「極度の強欲＝天井」と機械的に対応するわけではありません。</li>
        </ul>
        <div class="callout warn">
          <p>指数が示しているのは「いまの心理の状態」であり、「これからの値動き」ではありません。過去の傾向が今後も繰り返される保証はありません。</p>
        </div>
      </section>

      <section id="compare">
        <h2>ほかの指標との違い</h2>
        <p>市場心理を測る指標は、恐怖と強欲指数のほかにもいくつかあります。それぞれ見ているものが異なります。</p>
        <div class="table-scroll">
          <table class="doc">
            <thead><tr><th>指標</th><th>何を表すか</th><th>特徴</th></tr></thead>
            <tbody>
              <tr><th>恐怖と強欲指数</th><td>複数の指標を合成した、市場全体の心理</td><td>0〜100で直感的に読める。構成する指標によって解釈が変わる</td></tr>
              <tr><th>VIX指数</th><td>米国のS&amp;P500オプションから算出される、今後の予想変動率</td><td>米国市場の不安の目安。恐怖と強欲指数の構成要素の1つでもある</td></tr>
              <tr><th>日経平均VI</th><td>日経225オプションから算出される、今後の予想変動率</td><td>日本市場版の変動性指標。値が高いほど、先行きの値動きが大きくなると見込まれている</td></tr>
              <tr><th>騰落レシオ</th><td>一定期間（一般に25日間）の値上がり銘柄数と値下がり銘柄数の比率</td><td>市場の過熱感や売られすぎの目安として使われる</td></tr>
            </tbody>
          </table>
        </div>
        <p>VIXや日経平均VIのような変動性指標は、「不安」という1つの側面を測るものです。恐怖と強欲指数は、こうした要素を含む複数の指標を束ねて、市場全体の雰囲気を1つの数字にしたものと考えると整理しやすくなります。</p>
      </section>

      <section id="japan">
        <h2>日本の個人投資家が知っておきたい視点</h2>

        <h3>日本株は、為替と海外投資家の動きにも左右されやすい</h3>
        <p>日本株は、円相場の動きから影響を受けやすいとされています。一般に、円安は輸出企業の業績への期待につながりやすく、円高はその逆に働きやすいと言われます。また、売買代金に占める海外投資家の割合が大きいとされ、米国市場の心理と連動して動く場面もあります。当サイトが日本株と米国株を並べて表示しているのは、こうした関係を見比べやすくするためです。</p>

        <h3>新NISAとの関係</h3>
        <p>2024年に始まった新NISAには、「つみたて投資枠」と「成長投資枠」があります。長期・分散・積立を前提に設計された制度で、積立投資は、毎回一定額を購入し続けることで、購入価格を平均化していく考え方です。</p>
        <p>こうした長期の積立と、日々変わる市場心理の指標とは、もともと目的が異なります。恐怖と強欲指数は、売買のタイミングを測る道具というより、「いまの市場の温度感を知るための参考情報」として使われることが多い指標です。</p>
        <div class="callout">
          <p>NISA制度の内容は改正されることがあります。最新の情報は、金融庁や各金融機関の公式サイトでご確認ください。</p>
        </div>
      </section>

      <section id="caution">
        <h2>使うときの注意点</h2>
        <ul>
          <li><strong>単独で売買を判断しない。</strong>指数は数ある参考情報の1つです。業績、割安・割高の度合い、自分の資金計画など、ほかの情報とあわせて確認する必要があります。</li>
          <li><strong>日本株の指数はCNNの指数と構成が異なる。</strong>日本株の指数は当サイト独自の算出です。日本株の「50」と米国株の「50」は、同じ意味の水準とは限りません。</li>
          <li><strong>データの遅れや欠落がありうる。</strong>取得元の都合で、表示が遅れたり、一時的に更新されなかったりすることがあります。</li>
          <li><strong>過去の水準は将来を保証しない。</strong>過去に見られた傾向が、今後も同じように現れるとは限りません。</li>
          <li><strong>最終判断はご自身で行う。</strong>投資には元本割れのリスクがあります。必要に応じて、金融機関や専門家にご相談ください。</li>
        </ul>
      </section>

      <section id="faq">
        <h2>よくある質問</h2>
        <div class="faq">
{faq_html}
        </div>
      </section>

      <div class="cta">
        <p>いまの日本株・米国株の数値は、ダッシュボードで確認できます。</p>
        <a href="/">ダッシュボードを見る</a>
      </div>
"""
    return shell(
        "guide",
        "恐怖と強欲指数の読み方ガイド｜Fear & Greed Index Japan",
        "恐怖と強欲指数（Fear &amp; Greed Index）の数値の読み方、逆張り指標と言われる理由と限界、VIXや日経平均VIとの違い、日本の個人投資家が知っておきたい視点をわかりやすく解説します。",
        "/guide",
        "投資ガイド",
        body,
        extra_ld=faq_ld,
    )


if __name__ == "__main__":
    open("about.html", "w", encoding="utf-8").write(build_about())
    open("guide.html", "w", encoding="utf-8").write(build_guide())
    print("built about.html, guide.html")
