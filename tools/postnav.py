# -*- coding: utf-8 -*-
"""記事の「前の記事／次の記事」ナビ（記事の上部と下部に自動で入る）"""
import posts as P
from scoreboard import zone

CSS = """<style>
  .pn-top { display: flex; justify-content: space-between; gap: 12px; margin: -4px 0 16px; font-size: 13.5px; }
  .pn-top a { color: var(--c-eg); text-decoration: none; font-weight: 700; padding: 4px 0; }
  .pn-top a:hover { text-decoration: underline; }
  .post-nav { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 40px; }
  .pn { display: flex; flex-direction: column; gap: 5px; padding: 16px 18px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none; color: var(--ink); }
  a.pn:hover { border-color: var(--ink-soft); }
  .pn.next { text-align: right; }
  .pn-dir { font-size: 12.5px; font-weight: 700; color: var(--c-eg); }
  .pn-date { font-size: 13px; color: var(--muted); }
  .pn-title { font-size: 14.5px; font-weight: 700; line-height: 1.65; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .pn-sc { font-size: 13px; color: var(--ink-soft); }
  .pn.empty { background: transparent; border-style: dashed; }
  .pn.empty .pn-dir, .pn.empty .pn-title { color: var(--muted); font-weight: 500; }
  .pn-back { text-align: center; margin-top: 14px; font-size: 14px; }
  .pn-back a { color: var(--c-eg); text-underline-offset: 3px; }
  @media (max-width: 640px) { .post-nav { grid-template-columns: 1fr; } .pn.next { text-align: left; } }
</style>"""


def top_nav(prev, nxt):
    if not prev and not nxt:
        return ""
    left = f'<a rel="prev" href="/blog/{prev.DATE_ID}">‹ 前の記事 {P.short_label(prev)}</a>' if prev else "<span></span>"
    right = f'<a rel="next" href="/blog/{nxt.DATE_ID}">次の記事 {P.short_label(nxt)} ›</a>' if nxt else "<span></span>"
    return f'<nav class="pn-top" aria-label="前後の記事">{left}{right}</nav>\n'


def _slot(m, kind):
    label = "← 前の記事" if kind == "prev" else "次の記事 →"
    if m is None:
        msg = "これより前の記事はありません" if kind == "prev" else "次の記事は準備中です。次の営業日の市況をまとめ次第、公開します。"
        return f'<div class="pn {kind} empty"><span class="pn-dir">{label}</span><span class="pn-title">{msg}</span></div>'
    return (f'<a class="pn {kind}" rel="{kind}" href="/blog/{m.DATE_ID}"><span class="pn-dir">{label}</span>'
            f'<span class="pn-date">{P.full_label(m)}</span><span class="pn-title">{m.TITLE}</span>'
            f'<span class="pn-sc">日本株 {m.JP_SCORE}（{zone(m.JP_SCORE)[0]}）｜米国株 {m.US_SCORE}（{zone(m.US_SCORE)[0]}）</span></a>')


def bottom_nav(prev, nxt):
    return (f'\n<nav class="post-nav" aria-label="前後の記事">{_slot(prev, "prev")}{_slot(nxt, "next")}</nav>\n'
            '<p class="pn-back"><a href="/blog">ブログ一覧へ戻る</a></p>')
