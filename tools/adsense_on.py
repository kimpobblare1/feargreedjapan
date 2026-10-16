# -*- coding: utf-8 -*-
"""AdSense のコードを全ページで有効にする（1回実行すればOK。何度実行しても結果は同じ）。

  ・public/ の全HTML、tools/ と scripts/ のテンプレートの中で、
    コメントで無効にしてある AdSense のコード（ca-pub-XXXX…）を、実際のIDの有効なコードに置き換えます。
  ・ID は public/ads.txt と同じ pub ID を使います。
"""
import os
import re
import sys

PUB = "ca-pub-9496300145102373"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client="

# ① コメントで囲まれた無効なコード → 有効なコード
RE_COMMENTED = re.compile(
    r"<!--[ \t]*\r?\n[ \t]*(<script async src=\"" + re.escape(SRC) + r")ca-pub-[0-9X]+(\" crossorigin=\"anonymous\"></script>)[ \t]*\r?\n[ \t]*-->")
# ② すでに有効だが ID が仮のまま（XXXX）のもの
RE_PLACEHOLDER = re.compile(re.escape(SRC) + r"ca-pub-X+")
# ③ 説明コメントの文言
OLD_NOTE = "▼ AdSense承認後に有効化（既存アカウントのpub IDをそのまま使用。アカウントは新規作成せず「サイトを追加」で登録）"
NEW_NOTE = "▼ AdSense（審査と広告表示のためのコード。pub ID は public/ads.txt と同じ）"


def fix(text):
    t = RE_COMMENTED.sub(lambda m: m.group(1) + PUB + m.group(2), text)
    t = RE_PLACEHOLDER.sub(SRC + PUB, t)
    return t.replace(OLD_NOTE, NEW_NOTE)


def targets():
    for base, exts in (("public", (".html",)), ("tools", (".py",)), ("scripts", (".py",))):
        d = os.path.join(ROOT, base)
        for root, _, files in os.walk(d):
            if "__pycache__" in root or os.sep + "data" in root:
                continue
            for f in files:
                if f.endswith(exts) and f != "adsense_on.py":
                    yield os.path.join(root, f)


def main():
    changed = []
    for path in targets():
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
        new = fix(old)
        if new != old:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            changed.append(os.path.relpath(path, ROOT))
    # 確認：仮のIDやコメントアウトされたコードが残っていないか
    left = []
    for path in targets():
        t = open(path, encoding="utf-8").read()
        if "ca-pub-XXXX" in t:
            left.append(os.path.relpath(path, ROOT))
    print("AdSense のコードを有効にしたファイル（%d）:" % len(changed))
    for c in changed:
        print("  ・" + c)
    if left:
        print("【注意】仮のIDが残っているファイルがあります:")
        for c in left:
            print("  ・" + c)
        return 1
    print("仮のID（ca-pub-XXXX…）は残っていません。pub ID: " + PUB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
