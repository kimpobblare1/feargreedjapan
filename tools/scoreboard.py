# -*- coding: utf-8 -*-
"""ブログ記事の上部に置く「恐怖と強欲指数スコアボード」（今後の記事でも使い回せる部品）"""

ZN = [(24, "極度の恐怖", "ef"), (44, "恐怖", "f"), (54, "中立", "n"), (74, "強欲", "g"), (100, "極度の強欲", "eg")]


def zone(v):
    return next((n, k) for m, n, k in ZN if round(v) <= m)


CSS = """<style>
  .sc-asof { font-size: 13px; font-weight: 700; color: var(--ink-soft); margin: 22px 0 8px; letter-spacing: .02em; }
  .scoreboard { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .sc-card { background: var(--surface); border: 1px solid var(--line); border-top: 5px solid var(--zc); border-radius: var(--radius); padding: 18px 22px 16px; }
  .sc-top { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
  .sc-name { font-weight: 900; font-size: 17px; }
  .sc-src { font-size: 12px; color: var(--muted); }
  .sc-main { display: flex; align-items: center; gap: 18px; margin-top: 8px; }
  .sc-num { font-size: 76px; font-weight: 900; line-height: 1; color: var(--zc); font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
  .sc-side { display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
  .sc-chip { display: inline-block; padding: 4px 16px; border-radius: 999px; background: var(--zc); color: #fff; font-weight: 700; font-size: 16px; white-space: nowrap; }
  .sc-delta { font-size: 14px; font-weight: 700; white-space: nowrap; }
  .sc-delta.up { color: var(--c-g); } .sc-delta.down { color: var(--c-ef); } .sc-delta.flat { color: var(--muted); }
  .sc-bar { position: relative; height: 14px; border-radius: 7px; margin-top: 20px;
    background: linear-gradient(to right, var(--c-ef) 0 25%, var(--c-f) 25% 45%, var(--c-n) 45% 55%, var(--c-g) 55% 75%, var(--c-eg) 75% 100%); }
  .sc-pin { position: absolute; top: -7px; width: 5px; height: 28px; background: var(--ink); border-radius: 3px; transform: translateX(-50%); box-shadow: 0 0 0 2px #fff; }
  .sc-ticks { position: relative; height: 16px; margin-top: 6px; font-size: 11px; color: var(--muted); }
  .sc-ticks span { position: absolute; transform: translateX(-50%); font-variant-numeric: tabular-nums; }
  .sc-ticks span:first-child { transform: none; } .sc-ticks span:last-child { transform: translateX(-100%); }
  .sc-hist { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 13px; color: var(--ink-soft); }
  .sc-hist b { font-variant-numeric: tabular-nums; color: var(--ink); font-size: 14px; }
  .sc-foot { font-size: 13.5px; color: var(--ink-soft); margin: 10px 2px 0; line-height: 1.85; }
  .sc-foot strong { color: var(--ink); }
  @media (max-width: 640px) { .scoreboard { grid-template-columns: 1fr; } .sc-num { font-size: 64px; } }
</style>"""


def _card(name, src, score, prev, w1, m1):
    zn, zk = zone(score)
    d = round(score) - round(prev)
    cls, arrow = ("up", "▲") if d > 0 else (("down", "▼") if d < 0 else ("flat", "―"))
    dtxt = "±0" if d == 0 else ("+" if d > 0 else "−") + str(abs(d))
    pos = max(0, min(100, score))
    ticks = "".join(f'<span style="left:{p}%">{p}</span>' for p in (0, 25, 45, 55, 75, 100))
    return f"""<div class="sc-card" style="--zc:var(--c-{zk})">
  <div class="sc-top"><span class="sc-name">{name}</span><span class="sc-src">{src}</span></div>
  <div class="sc-main">
    <div class="sc-num">{score}</div>
    <div class="sc-side"><span class="sc-chip">{zn}</span><span class="sc-delta {cls}">{arrow} 前日比 {dtxt}</span></div>
  </div>
  <div class="sc-bar" role="img" aria-label="{name}の指数は{score}で「{zn}」の区分です（0が極度の恐怖、100が極度の強欲）"><span class="sc-pin" style="left:{pos}%"></span></div>
  <div class="sc-ticks" aria-hidden="true">{ticks}</div>
  <div class="sc-hist"><span>前日 <b>{prev}</b></span><span>1週間前 <b>{w1}</b></span><span>1か月前 <b>{m1}</b></span></div>
</div>"""


def scoreboard(asof, jp, us, foot=""):
    """jp / us: dict(score, prev, w1, m1)"""
    gap = jp["score"] - us["score"]
    gtxt = "±0" if gap == 0 else ("+" if gap > 0 else "−") + str(abs(gap))
    who = "日本株が上" if gap > 0 else ("米国株が上" if gap < 0 else "同水準")
    return f"""<div class="sc-asof">{asof}</div>
<div class="scoreboard">
{_card("日本株", "日経225ほか（当サイト算出）", jp["score"], jp["prev"], jp["w1"], jp["m1"])}
{_card("米国株", "S&amp;P500基準（CNN Business）", us["score"], us["prev"], us["w1"], us["m1"])}
</div>
<p class="sc-foot"><strong>日米差（日本−米国）：{gtxt}（{who}）</strong>{("　" + foot) if foot else ""}</p>"""
