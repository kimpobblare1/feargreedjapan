# -*- coding: utf-8 -*-
"""記事ファイルで使う部品（表・段落・囲み・チップ・折れ線グラフ）。記事側は `from postkit import *` で使えます。"""
import datetime as _dt
import html as _h

from scoreboard import scoreboard, zone   # noqa: F401  （記事側から使えるように再公開）

ZN = [(24, "極度の恐怖", "ef"), (44, "恐怖", "f"), (54, "中立", "n"), (74, "強欲", "g"), (100, "極度の強欲", "eg")]
WD = ["月", "火", "水", "木", "金", "土", "日"]


def zkey(v):
    return next((k for m, n, k in ZN if round(v) <= m), "n")


def chip(v):
    n, k = zone(v)
    return f'<span class="chip {k}">{n}</span>'


def e(t):
    return _h.escape(t)


def md(d):
    """'2026-09-18' → '9/18（金）'"""
    y, m, dd = map(int, d.split("-"))
    return f"{m}/{dd}（{WD[_dt.date(y, m, dd).weekday()]}）"


def tbl(headers, rows, right=(), caption=None, narrow=False):
    th = "".join(f'<th class="r">{h}</th>' if i in right else f"<th>{h}</th>" for i, h in enumerate(headers))
    body = []
    for r in rows:
        tds = "".join(f'<td class="r">{c}</td>' if i in right else f"<td>{c}</td>" for i, c in enumerate(r))
        body.append(f"<tr>{tds}</tr>")
    cap = f'<h3 class="tblcap">{caption}</h3>' if caption else ""
    return (f'{cap}<div class="table-scroll"><table class="doc{" narrow" if narrow else ""}">'
            f'<thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def p(t):
    return f"<p>{t}</p>"


def callout(t, warn=False):
    return f'<div class="callout{" warn" if warn else ""}"><p>{t}</p></div>'


def line_chart(dates, jp, us, label=""):
    """日本株・米国株の指数の折れ線グラフ（SVG）。dates は 'YYYY-MM-DD' のリスト"""
    W, H, L, R, T, B = 820, 320, 44, 18, 16, 40
    cw, ch = W - L - R, H - T - B
    X = lambda i: L + i * cw / (len(dates) - 1)
    Y = lambda v: T + ch - v / 100 * ch
    col = {"ef": "#b3261e", "f": "#d9822b", "n": "#8a94a6", "g": "#3b8f6b", "eg": "#1f6fb2"}
    bounds = [0, 25, 45, 55, 75, 100]
    aria = label or f"日本株と米国株の恐怖と強欲指数の推移（{md(dates[0])}〜{md(dates[-1])}）。日本株は{min(jp)}〜{max(jp)}、米国株は{min(us)}〜{max(us)}の範囲で推移"
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{aria}" style="max-width:820px;display:block">']
    for i, (m_, n, k) in enumerate(ZN):
        y1, y0 = Y(bounds[i + 1]), Y(bounds[i])
        out.append(f'<rect x="{L}" y="{y1:.1f}" width="{cw}" height="{y0 - y1:.1f}" fill="{col[k]}" opacity="0.08"/>')
    for v in (0, 25, 50, 75, 100):
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#dfe5ee" stroke-dasharray="4 4"/>')
        out.append(f'<text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="11" fill="#6b7a94">{v}</text>')
    for i, d in enumerate(dates):
        if i % 5 == 0 or i == len(dates) - 1:
            _, m_, dd = d.split("-")
            out.append(f'<text x="{X(i):.1f}" y="{H - 14}" text-anchor="middle" font-size="11" fill="#6b7a94">{int(m_)}/{int(dd)}</text>')
    pts = lambda vs: " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vs))
    out.append(f'<polyline points="{pts(us)}" fill="none" stroke="#1f6fb2" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{pts(jp)}" fill="none" stroke="#14284b" stroke-width="2.8" stroke-linejoin="round"/>')
    jp_high = jp[-1] >= us[-1]
    for vs, c, dy in ((jp, "#14284b", -9 if jp_high else 19), (us, "#1f6fb2", 19 if jp_high else -9)):
        i = len(vs) - 1
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(vs[i]):.1f}" r="4.5" fill="#fff" stroke="{c}" stroke-width="2.4"/>')
        out.append(f'<text x="{X(i) - 8:.1f}" y="{Y(vs[i]) + dy:.1f}" text-anchor="end" font-size="13" font-weight="700" fill="{c}">{vs[i]}</text>')
    out.append(f'<text x="{L + 8}" y="{T + 14}" font-size="12" font-weight="700" fill="#14284b">━ 日本株（3日平均）</text>')
    out.append(f'<text x="{L + 170}" y="{T + 14}" font-size="12" font-weight="700" fill="#1f6fb2">━ 米国株（CNN）</text>')
    out.append("</svg>")
    return "".join(out)


def operator_note(paragraphs):
    """運営者のひとこと（記事の最後、まとめの前に置く）。paragraphs は段落の文字列のリスト"""
    body = "".join(f'<p style="margin:10px 0 0;line-height:1.95">{t}</p>' for t in paragraphs)
    return ('<section id="operator" style="margin-top:36px">'
            '<div style="background:var(--surface);border:1px solid var(--line);border-left:5px solid var(--ink);'
            'border-radius:var(--radius);padding:20px 24px">'
            '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">'
            '<span style="font-weight:900;font-size:16px">運営者のひとこと</span>'
            '<span style="font-size:12.5px;color:var(--muted)">Fear &amp; Greed Index Japan 運営事務局</span></div>'
            f'{body}'
            '<p style="margin:12px 0 0;font-size:12.5px;color:var(--muted)">※運営者の個人的な見方であり、特定の金融商品の売買を勧めるものではありません。</p>'
            '</div></section>')
