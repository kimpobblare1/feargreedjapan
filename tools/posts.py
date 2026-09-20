# -*- coding: utf-8 -*-
"""
ブログ記事の登録簿（自動読み込み）
  content/posts/ に置いた blog_post_YYYYMMDD.py を、すべて自動で読み込みます。
  → 新しい記事は「ファイルを1つ置くだけ」。この一覧を書き換える必要はありません。
  並び順は日付から自動で決まります（前の記事／次の記事、ブログ一覧、サイトマップ、トップの最新記事も自動）。

  記事ファイルに必要な項目：
    DATE_ISO, DATE_ID, PUBLISHED_ISO, TITLE, META_TITLE, DESCRIPTION, EXCERPT, TAGS, JP_SCORE, US_SCORE, build()
  （任意）CARD_EXCERPT：トップページ用の短い紹介文 / ALLOW_SHORT：文字数の下限チェックを免除
"""
import datetime as _dt
import glob
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.environ.get("POSTS_DIR") or os.path.join(ROOT, "content", "posts")
REQUIRED = ["DATE_ISO", "DATE_ID", "PUBLISHED_ISO", "TITLE", "META_TITLE", "DESCRIPTION", "EXCERPT", "TAGS", "JP_SCORE", "US_SCORE", "build"]
_WD = ["月", "火", "水", "木", "金", "土", "日"]


def _fail(msg):
    raise SystemExit("【記事ファイルのエラー】" + msg)


def _load():
    if POSTS_DIR not in sys.path:
        sys.path.insert(0, POSTS_DIR)          # 記事が使う補助ファイル（data18.py など）を読めるように
    mods = []
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "blog_post_*.py"))):
        name = os.path.basename(path)[:-3]
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        except SyntaxError as e:
            _fail("%s の書き方に誤りがあります（%d行目）: %s" % (os.path.basename(path), e.lineno or 0, e.msg))
        except Exception as e:  # noqa: BLE001
            _fail("%s を読み込めませんでした: %s: %s" % (os.path.basename(path), type(e).__name__, e))
        missing = [k for k in REQUIRED if not hasattr(m, k)]
        if missing:
            _fail("%s に必要な項目がありません: %s" % (os.path.basename(path), ", ".join(missing)))
        try:
            _dt.date.fromisoformat(m.DATE_ISO)
        except Exception:  # noqa: BLE001
            _fail("%s の DATE_ISO が日付の形式（YYYY-MM-DD）ではありません: %r" % (os.path.basename(path), m.DATE_ISO))
        if m.DATE_ID != m.DATE_ISO.replace("-", "") or name != "blog_post_" + m.DATE_ID:
            _fail("%s：ファイル名・DATE_ID・DATE_ISO の日付が一致していません" % os.path.basename(path))
        for k in ("JP_SCORE", "US_SCORE"):
            if not isinstance(getattr(m, k), int) or not 0 <= getattr(m, k) <= 100:
                _fail("%s の %s は 0〜100 の整数にしてください" % (os.path.basename(path), k))
        mods.append(m)
    mods.sort(key=lambda m: m.DATE_ISO)
    ids = [m.DATE_ID for m in mods]
    if len(ids) != len(set(ids)):
        _fail("同じ日付の記事が2つあります")
    if not mods:
        _fail("記事が1つもありません（%s）" % POSTS_DIR)
    return mods


POSTS = _load()   # 古い順


def _d(m):
    y, mo, d = map(int, m.DATE_ISO.split("-"))
    return y, mo, d, _WD[_dt.date(y, mo, d).weekday()]


def full_label(m):     # 2026年9月18日（金）
    y, mo, d, w = _d(m)
    return f"{y}年{mo}月{d}日（{w}）"


def short_label(m):    # 9/18（金）
    y, mo, d, w = _d(m)
    return f"{mo}/{d}（{w}）"


def crumb_label(m):    # 9月18日の市況
    y, mo, d, w = _d(m)
    return f"{mo}月{d}日の市況"
