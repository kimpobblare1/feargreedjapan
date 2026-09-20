#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数別の統計データ（public/data/stats.json）を作成します。

  日本株の「恐怖と強欲指数」を、過去の価格データから当サイトと同じ計算方法で再計算し、
  各区分（極度の恐怖〜極度の強欲）にあった日の「その後の日経平均の動き」
  （5・20・60営業日後）を集計します。

  ・指数の過去分は、その日より前のデータだけで計算します（先読みなし）
  ・日経平均は終値ベースで、配当・売買コスト・税金は含みません
  ・計算は約20時間に1回だけ行います（毎時の更新では何もしません）
  ・失敗しても、指数の更新など他の処理には影響しません
"""
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "public", "data", "stats.json")

HORIZONS = (5, 20, 60)                 # 何営業日後を見るか（約1週間・1か月・3か月）
RANGE = "10y"                          # 取得する価格データの期間
STALE_HOURS = 20                       # この時間より新しければ、再計算しない
MIN_DAYS = 250                         # 集計に使える営業日がこれ未満なら、統計は作らない
ZONES = [                              # (キー, 名前, 範囲, 上限値)
    ("ef", "極度の恐怖", "0〜24", 24),
    ("f", "恐怖", "25〜44", 44),
    ("n", "中立", "45〜54", 54),
    ("g", "強欲", "55〜74", 74),
    ("eg", "極度の強欲", "75〜100", 100),
]


def log(msg):
    print(msg, flush=True)


def load_update_data():
    spec = importlib.util.spec_from_file_location("update_data", os.path.join(HERE, "update_data.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ───────── 集計の部品 ─────────
def zone_index(score):
    s = max(0, min(100, round(score)))
    for i, z in enumerate(ZONES):
        if s <= z[3]:
            return i
    return len(ZONES) - 1


def percentile(sorted_vals, p):
    """線形補間のパーセンタイル（p は 0〜100）"""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    k = (n - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, n - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def r2(x):
    return round(x, 2)


def summarize(rets):
    """リターン（小数）のリスト → 中央値・平均・上昇した割合などの要約（%表記）"""
    if not rets:
        return None
    v = sorted(rets)
    n = len(v)
    return {
        "n": n,
        "median": r2(percentile(v, 50) * 100),
        "mean": r2(sum(v) / n * 100),
        "win": round(sum(1 for x in v if x > 0) / n * 100, 1),
        "p10": r2(percentile(v, 10) * 100),
        "p90": r2(percentile(v, 90) * 100),
        "min": r2(v[0] * 100),
        "max": r2(v[-1] * 100),
    }


def compute_stats(closes, hist):
    """
    closes: [(日付, 日経平均の終値), ...]（古い順）
    hist  : [(日付, 指数(平滑化後), parts), ...]（古い順）
    """
    pos = {d: i for i, (d, _) in enumerate(closes)}
    rows = []                                   # (終値系列上の位置, 区分の番号, {h: リターン})
    for h_ in hist:
        d, score = h_[0], h_[1]
        i = pos.get(d)
        if i is None:
            continue
        rets = {}
        for h in HORIZONS:
            if i + h < len(closes):
                rets[h] = closes[i + h][1] / closes[i][1] - 1
        rows.append((i, zone_index(score), rets))
    if not rows:
        return None

    zones_out = []
    for zi, (key, name, rng, _mx) in enumerate(ZONES):
        mine = [r for r in rows if r[1] == zi]
        # 「連続した期間（局面）」の数：営業日が連続して同じ区分にあった塊
        episodes, prev_i, prev_z = 0, None, None
        for i, z, _ in rows:
            if z == zi and not (prev_z == zi and prev_i is not None and i == prev_i + 1):
                episodes += 1
            prev_i, prev_z = i, z
        days = len(mine)
        zones_out.append({
            "key": key, "name": name, "range": rng,
            "days": days,
            "share": round(days / len(rows) * 100, 1),
            "episodes": episodes,
            "avg_run": round(days / episodes, 1) if episodes else None,
            "fwd": {str(h): summarize([r[2][h] for r in mine if h in r[2]]) for h in HORIZONS},
        })
    baseline = {"days": len(rows), "fwd": {str(h): summarize([r[2][h] for r in rows if h in r[2]]) for h in HORIZONS}}
    first, last = closes[rows[0][0]][0], closes[rows[-1][0]][0]
    return {
        "success": True,
        "as_of": last,
        "period": {"start": first, "end": last, "days": len(rows)},
        "horizons": list(HORIZONS),
        "zones": zones_out,
        "baseline": baseline,
    }


# ───────── データ取得と指数の再計算 ─────────
def fetch_jgb_long(u):
    """update_data.fetch_jgb と同じ取得方法だが、古いデータも捨てずに長く使う"""
    merged = {}
    for url in u.JGB_URLS:
        try:
            r = u.requests.get(url, headers=u.UA, timeout=30)
            if r.status_code != 200:
                continue
            for d, v in u.parse_jgb_csv(r.content.decode("utf-8", errors="ignore")):
                merged[d] = v
        except Exception as e:  # noqa: BLE001
            log("  国債データの取得に失敗: %s" % e)
    out = sorted(merged.items())
    if len(out) < 60:
        raise RuntimeError("国債データ不足（%d件）" % len(out))
    return out


def fetch_all(u):
    n225 = u.fetch_yahoo("^N225", RANGE)
    fx = topix = jgb = None
    try:
        fx = u.fetch_yahoo("JPY=X", RANGE)
    except Exception as e:  # noqa: BLE001
        log("  ドル円を取得できませんでした（この指標なしで計算します）: %s" % e)
    for sym in u.TOPIX_ETFS:
        try:
            topix = u.fetch_yahoo(sym, RANGE)
            break
        except Exception as e:  # noqa: BLE001
            log("  %s を取得できませんでした: %s" % (sym, e))
    try:
        jgb = fetch_jgb_long(u)
    except Exception as e:  # noqa: BLE001
        log("  国債利回りを取得できませんでした（この指標なしで計算します）: %s" % e)
    return n225, topix, fx, jgb


def compute_all(u, n225, topix, fx, jgb):
    u.HISTORY_DAYS = 10 ** 6            # 直近30日ではなく、計算できた全期間の履歴を得る
    jp, hist = u.compute_jp(n225, topix, fx, jgb)
    if not jp:
        return None
    # 指数を計算できた最初の約1年（比較期間が1年に満たない期間）は、値が不安定なので集計から外す
    hist = hist[u.WINDOW:]
    if len(hist) < MIN_DAYS:
        return None
    res = compute_stats(n225, hist)
    if res:
        res["method"] = {"window": u.WINDOW, "smooth_days": u.SMOOTH_DAYS}
    return res


# ───────── 保存 ─────────
def strip_time(d):
    d = dict(d)
    d.pop("generated_at", None)
    return d


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def main():
    old = load_json(OUT)
    if old and old.get("generated_at") and not os.environ.get("FORCE_STATS"):
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(old["generated_at"])).total_seconds() / 3600
            if age < STALE_HOURS:
                log("統計データは %.1f 時間前に作成済みのため、今回は再計算しません。" % age)
                return 0
        except Exception:  # noqa: BLE001
            pass
    u = load_update_data()
    log("=== 指数別の統計データを作成します（過去%s分の価格から再計算） ===" % RANGE)
    n225, topix, fx, jgb = fetch_all(u)
    res = compute_all(u, n225, topix, fx, jgb)
    if not res:
        log("指数を十分な日数だけ計算できなかったため、統計データは更新しません。")
        return 0
    res["generated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if old and strip_time(old) == strip_time(res):
        old["generated_at"] = res["generated_at"]
        res = old
        log("内容に変更はありません（作成時刻だけ更新）。")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    log("stats.json を更新しました：対象 %d 営業日（%s〜%s）" % (res["period"]["days"], res["period"]["start"], res["period"]["end"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print("統計データの作成に失敗しました（他の更新には影響しません）: %s" % e)
        sys.exit(0)
