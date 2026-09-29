#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市況アーカイブ更新スクリプト
  public/data/latest.json の履歴（日本株・米国株の日次の指数）から、
  public/data/archive.json に「まだ記録していない日」を追記します。

  ・latest.json の履歴（直近30営業日）にある日は、最新の計算（終値ベース）に合わせて更新します
    （取引時間中に記録された値や、データの確定で変わった値を、確定値に直すため）。それより古い日は書き換えません
  ・コメントは、数値だけから作る定型文です（相場の予想や売買の助言は含みません）
  ・失敗しても、指数の更新（update_data.py）には影響しません
"""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LATEST = os.path.join(ROOT, "public", "data", "latest.json")
ARCHIVE = os.path.join(ROOT, "public", "data", "archive.json")
BLOG_DIR = os.path.join(ROOT, "public", "blog")

ZONES = [(24, "極度の恐怖"), (44, "恐怖"), (54, "中立"), (74, "強欲"), (100, "極度の強欲")]


def zone_of(v):
    v = max(0, min(100, round(v)))
    for mx, name in ZONES:
        if v <= mx:
            return name
    return ZONES[-1][1]


def diff_text(cur, prev):
    if prev is None or cur is None:
        return ""
    d = round(cur) - round(prev)
    if d == 0:
        return "前日比±0"
    return "前日比%s%d" % ("+" if d > 0 else "−", abs(d))


def make_text(jp, jp_prev, us, us_prev):
    """数値だけから、短い定型コメントを作る"""
    parts = []
    z = zone_of(jp)
    head = "日本株 %d（%s）" % (round(jp), z)
    dj = diff_text(jp, jp_prev)
    if dj:
        head += "%s" % dj
    if us is not None:
        head += "、米国株 %d（%s）" % (round(us), zone_of(us))
        du = diff_text(us, us_prev)
        if du:
            head += "%s" % du
        g = round(jp) - round(us)
        head += "。日米差は%s。" % ("±0" if g == 0 else ("%s%d" % ("+" if g > 0 else "−", abs(g))))
    else:
        head += "。"
    parts.append(head)

    notes = []
    if jp_prev is not None and zone_of(jp_prev) != z:
        notes.append("日本株は「%s」から「%s」に区分が変わりました。" % (zone_of(jp_prev), z))
    elif jp_prev is not None and abs(round(jp) - round(jp_prev)) >= 6:
        notes.append("日本株の指数は1日で%dポイント動きました。" % abs(round(jp) - round(jp_prev)))
    if us is not None and us_prev is not None and zone_of(us_prev) != zone_of(us):
        notes.append("米国株は「%s」から「%s」に区分が変わりました。" % (zone_of(us_prev), zone_of(us)))
    if us is not None:
        gap = abs(round(jp) - round(us))
        if gap >= 15:
            notes.append("日米の指数の差が%dポイントに開いています。" % gap)
        elif zone_of(jp) == zone_of(us):
            notes.append("日米とも「%s」の区分でした。" % z)
    parts.extend(notes[:2])
    return "".join(parts)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return default


def main():
    latest = load_json(LATEST, None)
    if not latest or not latest.get("success"):
        print("latest.json がまだ無い（または失敗状態）ため、アーカイブは更新しません。")
        return 0
    hist = [h for h in latest.get("history", []) if h.get("jp") is not None]
    if not hist:
        print("履歴が空のため、アーカイブは更新しません。")
        return 0

    arc = load_json(ARCHIVE, {"entries": []})
    entries = arc.get("entries", [])
    by_date = {e["date"]: e for e in entries}
    added = updated = 0
    for i, h in enumerate(hist):
        d = h["date"]
        prev = hist[i - 1] if i > 0 else None
        jp_prev = prev["jp"] if prev else None
        us = h.get("us")
        us_prev = prev.get("us") if prev else None
        vals = {
            "jp": int(round(h["jp"])),
            "jp_prev": None if jp_prev is None else int(round(jp_prev)),
            "us": None if us is None else int(round(us)),
            "us_prev": None if us_prev is None else int(round(us_prev)),
        }
        e = by_date.get(d)
        if e is None:
            if i == 0:
                continue          # 前日が分からない最初の日は、新しくは追加しない（既存の記録はそのまま）
            e = {"date": d}
            entries.append(e)
            by_date[d] = e
            added += 1
        elif all(e.get(k) == v for k, v in vals.items()):
            continue
        else:
            # 取引時間中に記録した値や、データの確定で変わった値を、最新の計算（終値ベース）に合わせて更新する
            updated += 1
        e.update(vals)
        e["text"] = make_text(h["jp"], jp_prev, us, us_prev)
        e.pop("post", None)       # 記事へのリンクはサイト側（記事の MARKET_DATE）で結び付ける

    entries.sort(key=lambda e: e["date"])
    if added == 0 and updated == 0:
        print("追加・更新する日はありません。")
        return 0
    out = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "entries": entries}
    os.makedirs(os.path.dirname(ARCHIVE), exist_ok=True)
    with open(ARCHIVE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("アーカイブを更新しました：追加 %d 件・更新 %d 件（合計 %d 日分）" % (added, updated, len(entries)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print("アーカイブの更新に失敗しました（指数の更新には影響しません）: %s" % e)
        sys.exit(0)
