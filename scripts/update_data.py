#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fear & Greed Japan - データ更新スクリプト
GitHub Actions から定期実行され、public/data/latest.json を作り直します。

  日本株 : Yahoo Finance（日経225・TOPIX連動ETF・ドル円）と財務省の国債金利CSVから独自に算出
  米国株 : CNN Business の公表値をそのまま取得

各データが取れなかった場合は、取れた分だけで計算し、直前の正常な値があれば
「stale（古い値）」の印を付けて残します。サイトが真っ白になることはありません。
"""
import hashlib
import json
import math
import os
import re
import sys
import time
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests

JST = timezone(timedelta(hours=9))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "public", "data", "latest.json")

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# ── 算出ルール（サイトの「指数の算出方法」と必ず一致させること）──
WINDOW = 250          # 各指標を「過去約1年（250営業日）の中での位置」に換算
MIN_POINTS = 120      # 比較できるデータがこれ未満なら、その指標は使わない
HISTORY_DAYS = 30     # 推移グラフに出す営業日数
BOND_DURATION = 9.0   # 10年国債の価格変動を利回り変化から概算するときの年数
MIN_WEIGHT = 0.6      # 取れた指標のウェイト合計がこれ未満なら、指数を出さない

WEIGHTS = {"momentum": 0.25, "vol": 0.25, "strength": 0.15, "rsi": 0.15, "fx": 0.10, "safe": 0.10}
NAMES = {
    "momentum": "市場モメンタム",
    "vol": "変動性",
    "strength": "株価の強さ",
    "rsi": "短期の過熱感",
    "fx": "為替（円）",
    "safe": "安全資産への選好",
}

TOPIX_ETFS = ["1306.T", "1475.T", "2557.T"]   # TOPIX指数そのものは取得できないため、連動ETFで代用

JGB_URLS = [
    "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv",
    "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv",
]

CNN_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
CNN_KEYS = [
    ("market_momentum_sp500", "市場モメンタム"),
    ("stock_price_strength", "株価の強さ"),
    ("stock_price_breadth", "株価の幅"),
    ("put_call_options", "プット／コール"),
    ("market_volatility_vix", "市場の変動性"),
    ("junk_bond_demand", "ジャンクボンド需要"),
    ("safe_haven_demand", "安全資産への需要"),
]


def log(msg):
    print(msg, flush=True)


# ════════════════════════════════════════════
#  データ取得
# ════════════════════════════════════════════
def fix_splits(series):
    """
    ETFの分割・併合などで、1日に価格が急変している（＝過去の価格が調整されていない）場合に、
    それ以前の価格を新しい価格の水準に合わせて補正する。
    日経225・為替・ETFの1日の値動きが±37%を超えることは通常ありえないため、そこを分割の目印にする。
    戻り値: (補正後の系列, 補正した箇所のリスト[(日付, 倍率)])
    """
    out = [[d, v] for d, v in series]
    fixes = []
    for i in range(len(out) - 1, 0, -1):
        prev, cur = out[i - 1][1], out[i][1]
        if prev <= 0 or cur <= 0:
            continue
        r = prev / cur
        if r >= 1.6 or r <= 1 / 1.6:
            n = float(round(r)) if r >= 1 else 1.0 / round(1.0 / r)
            if n <= 0 or abs(r / n - 1) > 0.25:
                n = r
            for j in range(i):
                out[j][1] /= n
            fixes.append((out[i][0], n))
    return [(d, v) for d, v in out], fixes


def fetch_yahoo(symbol, rng="3y"):
    """Yahoo Finance の日足終値を [(YYYY-MM-DD, 終値), ...] で返す（古い順）。失敗時は例外。"""
    last_err = "unknown"
    for host in ("query1", "query2"):
        url = "https://%s.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=%s" % (
            host, quote(symbol, safe=""), rng)
        for attempt in range(2):
            try:
                r = requests.get(url, headers=UA, timeout=20)
                if r.status_code != 200:
                    last_err = "HTTP %s" % r.status_code
                    time.sleep(2 * (attempt + 1))
                    continue
                res = r.json()["chart"]["result"][0]
                offset = (res.get("meta") or {}).get("gmtoffset", 0) or 0
                closes = res["indicators"]["quote"][0]["close"]
                by_date = {}
                for t, c in zip(res["timestamp"], closes):
                    if c is None:
                        continue
                    d = datetime.fromtimestamp(t + offset, timezone.utc).strftime("%Y-%m-%d")
                    by_date[d] = float(c)
                out = sorted(by_date.items())
                if len(out) < 30:
                    last_err = "データ不足（%d件）" % len(out)
                    continue
                out, fixes = fix_splits(out)
                for d, n in fixes:
                    log("  ⚠ %s: %s に分割らしき急変（約%g倍）を検出し、過去の価格を補正しました" % (symbol, d, n))
                return out
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
                time.sleep(2)
    raise RuntimeError(last_err)


def parse_jgb_csv(text, col="10Y"):
    """財務省の国債金利CSV（英語版）から、指定年限の金利を [(日付, 金利%), ...] で返す。"""
    idx = None
    rows = {}
    for line in text.splitlines():
        cells = [c.strip().strip('"') for c in line.split(",")]
        if not cells or not cells[0]:
            continue
        if cells[0] == "Date" and col in cells:
            idx = cells.index(col)
            continue
        m = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", cells[0])
        if m and idx is not None and len(cells) > idx:
            try:
                v = float(cells[idx])
            except ValueError:
                continue  # 「-」などの欠損
            rows["%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3)))] = v
    return sorted(rows.items())


def fetch_jgb():
    merged = {}
    last_err = "unknown"
    for url in JGB_URLS:
        try:
            r = requests.get(url, headers=UA, timeout=30)
            if r.status_code != 200:
                last_err = "HTTP %s" % r.status_code
                continue
            for d, v in parse_jgb_csv(r.content.decode("utf-8", errors="ignore")):
                merged[d] = v
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
    out = sorted(merged.items())[-800:]
    if len(out) < 60:
        raise RuntimeError(last_err if not out else "データ不足（%d件）" % len(out))
    return out


def fetch_cnn():
    """CNN Fear & Greed を取得。 (usブロック, {日付: スコア}) を返す。失敗時は例外。"""
    hdr = dict(UA)
    hdr.update({"Referer": "https://www.cnn.com/markets/fear-and-greed",
                "Origin": "https://www.cnn.com", "Accept": "application/json"})
    last_err = "unknown"
    urls = [CNN_URL, CNN_URL + "/" + datetime.now(timezone.utc).strftime("%Y-%m-%d")]
    for url in urls:
        try:
            r = requests.get(url, headers=hdr, timeout=20)
            if r.status_code != 200:
                last_err = "HTTP %s" % r.status_code
                continue
            j = r.json()
            fg = j["fear_and_greed"]
            if fg.get("score") is None:
                last_err = "score なし"
                continue

            def rnd(x):
                return None if x is None else int(round(x))

            hist = {}
            for p in ((j.get("fear_and_greed_historical") or {}).get("data") or []):
                d = datetime.fromtimestamp(p["x"] / 1000, timezone.utc).strftime("%Y-%m-%d")
                hist[d] = int(round(p["y"]))

            inds = []
            for key, name in CNN_KEYS:
                v = j.get(key)
                if isinstance(v, dict) and v.get("score") is not None:
                    inds.append({"name": name, "value": rnd(v["score"])})

            ts = fg.get("timestamp")
            us = {
                "score": rnd(fg["score"]),
                "previous_close": rnd(fg.get("previous_close")),
                "previous_1_week": rnd(fg.get("previous_1_week")),
                "previous_1_month": rnd(fg.get("previous_1_month")),
                "as_of": ts[:10] if isinstance(ts, str) else None,
                "indicators": inds,
                "stale": False,
            }
            return us, hist
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
    raise RuntimeError(last_err)


# ════════════════════════════════════════════
#  計算
# ════════════════════════════════════════════
def series_momentum(c, n=125):
    """終値と n日移動平均線との乖離率（%）"""
    out = [None] * len(c)
    for i in range(n - 1, len(c)):
        m = sum(c[i - n + 1:i + 1]) / n
        out[i] = (c[i] / m - 1) * 100
    return out


def series_vol(c, n=20):
    """直近 n営業日の変動率（日次対数収益率の標準偏差を年率換算、%）"""
    lr = [None] + [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    out = [None] * len(c)
    for i in range(n, len(c)):
        w = lr[i - n + 1:i + 1]
        m = sum(w) / n
        var = sum((x - m) ** 2 for x in w) / (n - 1)
        out[i] = math.sqrt(var) * math.sqrt(252) * 100
    return out


def series_ret(c, n=20):
    """n営業日前からの騰落率（%）"""
    out = [None] * len(c)
    for i in range(n, len(c)):
        out[i] = (c[i] / c[i - n] - 1) * 100
    return out


def series_rsi(c, n=14):
    """RSI（ワイルダー方式）"""
    out = [None] * len(c)
    if len(c) <= n:
        return out
    gains = losses = 0.0
    for i in range(1, n + 1):
        d = c[i] - c[i - 1]
        gains += max(d, 0)
        losses += max(-d, 0)
    ag, al = gains / n, losses / n
    out[n] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(n + 1, len(c)):
        d = c[i] - c[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
        out[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def _days(a, b):
    return (datetime.strptime(b, "%Y-%m-%d") - datetime.strptime(a, "%Y-%m-%d")).days


def align(base_dates, dates, vals, max_gap=10):
    """base_dates の各日について、その日以前で最新の値を返す（古すぎる値は使わない）"""
    out = []
    for d in base_dates:
        i = bisect_right(dates, d) - 1
        if i >= 0 and vals[i] is not None and _days(dates[i], d) <= max_gap:
            out.append(vals[i])
        else:
            out.append(None)
    return out


def pct_rank(window, x):
    """window の中で x が下から何%の位置か（0〜100）。同値は半分として数える。"""
    n = len(window)
    less = sum(1 for v in window if v < x)
    eq = sum(1 for v in window if v == x)
    return 100.0 * (less + 0.5 * eq) / n


def to_scores(raw, invert=False, start=0):
    out = [None] * len(raw)
    for i in range(start, len(raw)):
        x = raw[i]
        if x is None:
            continue
        w = [v for v in raw[max(0, i - WINDOW + 1):i + 1] if v is not None]
        if len(w) < MIN_POINTS:
            continue
        s = pct_rank(w, x)
        out[i] = 100.0 - s if invert else s
    return out


def compute_jp(n225, topix=None, fx=None, jgb=None):
    """日本株の指数を計算。戻り値: (jpブロック, [(日付, スコア)...]) 。計算できなければ (None, [])。"""
    dates = [d for d, _ in n225]
    c = [v for _, v in n225]
    notes = []

    raw = {
        "momentum": series_momentum(c),
        "vol": series_vol(c),
        "rsi": series_rsi(c),
    }
    ret20 = series_ret(c)

    if topix:
        td = [d for d, _ in topix]
        tc = [v for _, v in topix]
        t_ret = align(dates, td, series_ret(tc))
        raw["strength"] = [(a + b) / 2 if (a is not None and b is not None) else a
                           for a, b in zip(ret20, t_ret)]
    else:
        raw["strength"] = ret20[:]
        notes.append("TOPIX連動ETFを取得できなかったため、株価の強さは日経225のみで算出")

    if fx:
        fd = [d for d, _ in fx]
        fc = [v for _, v in fx]
        raw["fx"] = align(dates, fd, series_ret(fc))
    else:
        raw["fx"] = [None] * len(dates)

    if jgb:
        jd = [d for d, _ in jgb]
        jy = [v for _, v in jgb]
        dy = [None] * len(jy)
        for i in range(20, len(jy)):
            dy[i] = jy[i] - jy[i - 20]
        dya = align(dates, jd, dy)
        raw["safe"] = [(r + BOND_DURATION * y) if (r is not None and y is not None) else None
                       for r, y in zip(ret20, dya)]
    else:
        raw["safe"] = [None] * len(dates)

    n = len(dates)
    start = max(0, n - (HISTORY_DAYS + 5))
    scores = {k: to_scores(raw[k], invert=(k == "vol"), start=start) for k in WEIGHTS}

    hist = []
    for i in range(start, n):
        tot = wsum = 0.0
        for k, w in WEIGHTS.items():
            s = scores[k][i]
            if s is not None:
                tot += s * w
                wsum += w
        if wsum >= MIN_WEIGHT:
            hist.append((dates[i], tot / wsum))

    if not hist or hist[-1][0] != dates[-1]:
        return None, []

    def at(k):
        return int(round(hist[-k][1])) if len(hist) >= k else None

    inds, missing = [], []
    for k in WEIGHTS:
        s = scores[k][n - 1]
        if s is None:
            missing.append(NAMES[k])
        else:
            inds.append({"name": NAMES[k], "value": int(round(s))})

    jp = {
        "score": at(1),
        "previous_close": at(2),
        "previous_1_week": at(6),
        "previous_1_month": at(22),
        "as_of": dates[-1],
        "indicators": inds,
        "missing": missing,
        "notes": notes,
        "stale": False,
    }
    return jp, hist[-HISTORY_DAYS:]


# ════════════════════════════════════════════
#  メイン
# ════════════════════════════════════════════
def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def try_fetch(label, fn, *args):
    try:
        out = fn(*args)
        return out
    except Exception as e:  # noqa: BLE001
        log("  ❌ %s: %s" % (label, e))
        return None


def main():
    now = datetime.now(timezone.utc)
    prev = load_json(OUT_PATH)
    prev_ok = prev if (prev and prev.get("success")) else None

    log("=== 日本株の材料を取得 ===")
    n225 = try_fetch("日経225 (^N225)", fetch_yahoo, "^N225")
    if n225:
        log("  ✅ 日経225: %s = %.2f（%d日分）" % (n225[-1][0], n225[-1][1], len(n225)))
    topix = None
    for sym in TOPIX_ETFS:
        topix = try_fetch("TOPIX連動ETF (%s)" % sym, fetch_yahoo, sym)
        if topix:
            log("  ✅ TOPIX連動ETF %s: %s = %.2f" % (sym, topix[-1][0], topix[-1][1]))
            break
    fx = try_fetch("ドル円 (JPY=X)", fetch_yahoo, "JPY=X")
    if fx:
        log("  ✅ ドル円: %s = %.3f" % (fx[-1][0], fx[-1][1]))
    jgb = try_fetch("国債10年金利（財務省）", fetch_jgb)
    if jgb:
        log("  ✅ 国債10年: %s = %.3f%%" % (jgb[-1][0], jgb[-1][1]))

    jp, jp_hist = (None, [])
    if n225:
        jp, jp_hist = compute_jp(n225, topix, fx, jgb)
        if jp is None:
            log("  ❌ 日本株の指数を計算できませんでした（データ不足）")
    if jp:
        log("  → 日本株の指数: %d（欠けた指標: %s）" % (jp["score"], ", ".join(jp["missing"]) or "なし"))

    log("=== 米国株（CNN）を取得 ===")
    us, us_hist_map = None, {}
    got = try_fetch("CNN Fear & Greed", fetch_cnn)
    if got:
        us, us_hist_map = got
        log("  ✅ 米国株の指数: %s（細かい指標 %d/7 件）" % (us["score"], len(us["indicators"])))

    # ── 失敗したブロックは、直前の正常な値を「stale」として残す ──
    if jp is None and prev_ok and prev_ok.get("jp"):
        jp = dict(prev_ok["jp"])
        jp["stale"] = True
        jp_hist = [(h["date"], h["jp"]) for h in prev_ok.get("history", []) if h.get("jp") is not None]
        log("  ⚠ 日本株は前回の値を残します（stale）")
    if us is None and prev_ok and prev_ok.get("us"):
        us = dict(prev_ok["us"])
        us["stale"] = True
        us_hist_map = {h["date"]: h["us"] for h in prev_ok.get("history", []) if h.get("us") is not None}
        log("  ⚠ 米国株は前回の値を残します（stale）")

    if jp is None and us is None:
        log("❌ どちらも取得できず、前回の値もありません。ファイルは更新しません。")
        return 1

    # ── 推移グラフ用の履歴（日本の営業日ごとに、米国の値を寄せる）──
    history = []
    us_dates = sorted(us_hist_map)
    us_vals = [us_hist_map[d] for d in us_dates]
    if jp_hist:
        aligned_us = align([d for d, _ in jp_hist], us_dates, us_vals, max_gap=5) if us_dates else [None] * len(jp_hist)
        for (d, s), u in zip(jp_hist, aligned_us):
            row = {"date": d, "jp": int(round(s)) if not isinstance(s, int) else s}
            if u is not None:
                row["us"] = int(u)
            history.append(row)

    payload = {"success": True, "jp": jp, "us": us, "history": history}
    digest = hashlib.sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]

    if prev and prev.get("hash") == digest:
        log("変更なし：ファイルは更新しません。")
        return 0

    j = now.astimezone(JST)
    payload["hash"] = digest
    payload["updated_at"] = now.isoformat(timespec="seconds")
    payload["updated_at_jst"] = "%d年%d月%d日 %02d:%02d" % (j.year, j.month, j.day, j.hour, j.minute)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    log("✅ public/data/latest.json を更新しました（%s JST）" % payload["updated_at_jst"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
