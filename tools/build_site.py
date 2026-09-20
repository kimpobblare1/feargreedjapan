#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
サイトの自動ビルド

  content/posts/ に新しい記事ファイル（blog_post_YYYYMMDD.py）を置くと、次のページが自動で作り直されます。
    ・新しい記事ページ（前の記事へのリンク付き）と、直前の記事ページ（「次の記事」リンクを追加）
    ・ブログ一覧、サイトマップ、トップページの「最新の市況ブログ」
  ・いったん作業用の場所で全ページを作り、すべての検査に合格した場合だけ public/ に反映します。
    1つでも失敗したら、公開用のファイルは一切書き換えません（サイトが壊れません）。
  ・--all を付けると、サイトについて・投資ガイド・利用規約・プライバシーポリシー・404 も作り直します。
  ・記事ファイルを消しても、公開済みのページは自動では消えません（一覧・サイトマップからは外れます）。--prune で削除できます。
"""
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
TOOLS = os.path.join(ROOT, "tools")
MIN_PROSE = 1500          # 記事の「地の文」（表・図を除く）の最低文字数。これ未満の記事は公開しない
HANGUL = re.compile(r"[\uac00-\ud7a3]")
SYNC_EXT = (".html", ".txt", ".xml")


def prose_len(page_html):
    art = re.search(r"<article.*?</article>", page_html, re.S)
    t = art.group(0) if art else page_html
    t = re.sub(r"<svg.*?</svg>|<table.*?</table>|<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return len(re.sub(r"\s", "", _html.unescape(re.sub(r"<[^>]+>", "", t))))


def find_orphans(spub, posts):
    """記事ファイルが無いのに残っている blog/YYYYMMDD.html（記事を消した後の古いページ）"""
    ids = {m.DATE_ID for m in posts}
    out = []
    blog = os.path.join(spub, "blog")
    if os.path.isdir(blog):
        for f in sorted(os.listdir(blog)):
            mm = re.fullmatch(r"(\d{8})\.html", f)
            if mm and mm.group(1) not in ids:
                out.append("blog/" + f)
    return out


def validate(spub, posts):
    """作った全ページの検査。問題のリストを返す（空なら合格）"""
    problems = []
    pages = {}
    orphans = set(find_orphans(spub, posts))       # 古いページは検査の対象外（自動では消さない）
    for root, _, fs in os.walk(spub):
        for f in fs:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                rel = os.path.relpath(path, spub).replace(os.sep, "/")
                if rel not in orphans:
                    pages[rel] = open(path, encoding="utf-8").read()
    # 1) 記事ごとの検査
    for m in posts:
        rel = "blog/%s.html" % m.DATE_ID
        if rel not in pages:
            problems.append("記事ページが作られていません: " + rel)
            continue
        n = prose_len(pages[rel])
        if n < MIN_PROSE and not getattr(m, "ALLOW_SHORT", False):
            problems.append("%s：地の文（表を除く）が %d 字しかありません。%d 字以上にしてください（品質の下限チェック）" % (rel, n, MIN_PROSE))
    # 2) 全ページ共通の検査
    exists = lambda u: os.path.isfile(os.path.join(spub, (u.lstrip("/") or "index") + ".html")) or os.path.isfile(os.path.join(spub, u.lstrip("/")))
    for rel, s in pages.items():
        if HANGUL.search(s):
            problems.append(rel + "：韓国語（ハングル）が含まれています")
        for x in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', s, re.S):
            try:
                json.loads(x)
            except Exception:  # noqa: BLE001
                problems.append(rel + "：構造化データ（JSON-LD）の形式が正しくありません")
        for u in sorted(set(re.findall(r'href="(/[^"#?]*)', s))):
            if u.startswith("/data/"):
                continue                      # 実行時に作られるデータ
            if not exists(u):
                problems.append("%s：リンク先が存在しません → %s" % (rel, u))
    # 3) サイトマップ = 実在ページの正規URL
    sm = os.path.join(spub, "sitemap.xml")
    if os.path.isfile(sm):
        locs = set(re.findall(r"<loc>([^<]+)</loc>", open(sm, encoding="utf-8").read()))
        canon = set()
        for rel, s in pages.items():
            c = re.search(r'rel="canonical" href="([^"]+)"', s)
            if c:
                canon.add(c.group(1))
        if locs != canon:
            problems.append("サイトマップと実際のページが一致しません: 差 %s" % sorted(locs ^ canon))
    return problems


def sync(spub, public):
    """作業用の場所 → public/。内容が変わったファイルだけコピー（削除はしない）"""
    changed = []
    for root, _, fs in os.walk(spub):
        for f in sorted(fs):
            if not f.endswith(SYNC_EXT):
                continue
            src = os.path.join(root, f)
            rel = os.path.relpath(src, spub)
            dst = os.path.join(public, rel)
            new = open(src, "rb").read()
            old = open(dst, "rb").read() if os.path.exists(dst) else None
            if new != old:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as fh:
                    fh.write(new)
                changed.append(rel.replace(os.sep, "/") + ("（新規）" if old is None else ""))
    return changed


def main(argv):
    full = "--all" in argv
    stage = tempfile.mkdtemp(prefix="fgj_build_")
    spub = os.path.join(stage, "public")
    try:
        shutil.copytree(PUBLIC, spub, ignore=shutil.ignore_patterns("data"))
        os.chdir(spub)
        sys.path.insert(0, TOOLS)
        try:
            import build_content as bc
        except SystemExit as e:           # 記事ファイルの誤りは、分かりやすいメッセージで止める
            print(e)
            return 1
        bc.main()
        if full:
            import build_legal as bl
            for name, fn in (("about", bl.bp.build_about), ("guide", bl.bp.build_guide), ("terms", bl.build_terms),
                             ("privacy", bl.build_privacy), ("404", bl.build_404)):
                open(name + ".html", "w", encoding="utf-8").write(fn())
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "patch_index.py"), "index.html"], capture_output=True, text=True)
        if r.returncode != 0:
            print("トップページの更新に失敗しました:\n" + r.stdout + r.stderr)
            return 1
        problems = validate(spub, bc.P.POSTS)
        if problems:
            print("【検査に失敗したため、公開用ファイルは更新しません】")
            for x in problems:
                print("  ・" + x)
            return 1
        orphans = find_orphans(spub, bc.P.POSTS)
        changed = sync(spub, PUBLIC)
        if "--prune" in argv:
            for rel in orphans:                   # blog/YYYYMMDD.html の形のファイルだけを対象に、明示されたときだけ削除
                path = os.path.join(PUBLIC, rel)
                if os.path.isfile(path):
                    os.remove(path)
                    changed.append(rel + "（削除）")
            orphans = []
        print("記事 %d 本を確認。検査すべて合格。" % len(bc.P.POSTS))
        if orphans:
            print("【お知らせ】記事ファイルが無い古いページが残っています（自動では消しません。消す場合は --prune を付けて実行）:")
            for rel in orphans:
                print("  ・public/" + rel)
        print("更新したファイル（%d）:" % len(changed) if changed else "変更なし：公開用ファイルはそのままです。")
        for c in changed:
            print("  ・public/" + c)
        return 0
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
