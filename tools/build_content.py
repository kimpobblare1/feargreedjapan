# -*- coding: utf-8 -*-
"""アーカイブ・ブログ一覧・ブログ記事・robots/sitemap/ads.txt を生成する"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pages as bp
from build_pages import shell, SITE
import posts as P
import postnav
from scoreboard import CSS as SB_CSS, zone as _zone

PUBLISH_ISO = "2026-09-20"


# ═════════════════════════════════════════════
#  市況アーカイブ (/archive)
# ═════════════════════════════════════════════
def build_archive():
    body = """
      <h1>市況アーカイブ</h1>
      <p class="lead">日本株と米国株の恐怖と強欲指数を、営業日ごとに記録しています。指数の推移や、「恐怖」「強欲」の区分が入れ替わった日を振り返るための記録集です。</p>

      <noscript><div class="callout warn"><p>この記録の表示にはJavaScriptが必要です。ブラウザの設定でJavaScriptを有効にしてください。</p></div></noscript>

      <div class="stats" id="stats" aria-live="polite"></div>

      <div class="filters" id="filters" role="group" aria-label="日本株の区分で絞り込み"></div>
      <div id="list"></div>
      <div class="pager" id="pager" role="navigation" aria-label="ページ送り"></div>

      <p class="note-small" id="archive-note">日本株の指数は、各指標を「過去1年間の中での位置」で評価した相対的な値で、直近3営業日の平均です。米国株はCNN Businessの公表値です。
      2026年9月18日以前の日本株の値は、現在の算出方法で遡って計算した参考値です。コメントは数値から自動で作成した定型文で、相場の予想や売買の助言を含みません。</p>

      <section id="howto" style="padding-top:36px">
        <h2>アーカイブの使い方</h2>
        <div class="table-scroll"><table class="doc">
          <thead><tr><th>見たいこと</th><th>使い方</th></tr></thead>
          <tbody>
            <tr><th>恐怖が続いた期間</th><td>上のボタンで「恐怖」「極度の恐怖」に絞り込むと、日本株がその区分にあった日だけが並びます。</td></tr>
            <tr><th>日米の温度差</th><td>各日の「日米差」（日本−米国）を確認します。差が大きい日は、両市場の心理が別方向に動いています。</td></tr>
            <tr><th>詳しい解説</th><td>「この日のブログを読む」のリンクがある日は、市況ブログで指標ごとの内訳や当日のニュースを整理しています。</td></tr>
          </tbody>
        </table></div>
        <p>指数の読み方は<a class="inline" href="/guide">投資ガイド</a>、算出方法は<a class="inline" href="/#method">ダッシュボードの「指数の算出方法」</a>をご覧ください。</p>
      </section>
"""
    js = r"""
<script>
(function () {
  var PER = 15, ALL = [], filter = 'all', page = 1;
  var ZONES = [
    { k: 'ef', name: '極度の恐怖', max: 24 }, { k: 'f', name: '恐怖', max: 44 }, { k: 'n', name: '中立', max: 54 },
    { k: 'g', name: '強欲', max: 74 }, { k: 'eg', name: '極度の強欲', max: 100 }
  ];
  var WD = ['日', '月', '火', '水', '木', '金', '土'];
  function zoneOf(v) { v = Math.max(0, Math.min(100, Math.round(v))); for (var i = 0; i < ZONES.length; i++) if (v <= ZONES[i].max) return ZONES[i]; return ZONES[4]; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; }
  function chip(v) { var z = zoneOf(v); return el('span', 'chip ' + z.k, z.name); }
  function fmtDate(s) { var a = s.split('-'); var d = new Date(+a[0], +a[1] - 1, +a[2]); return a[0] + '年' + (+a[1]) + '月' + (+a[2]) + '日（' + WD[d.getDay()] + '）'; }
  function sgn(n) { return n === 0 ? '±0' : (n > 0 ? '+' : '−') + Math.abs(n); }

  function stats() {
    var box = document.getElementById('stats'); box.textContent = '';
    if (!ALL.length) return;
    var jp = ALL.map(function (e) { return e.jp; });
    var sum = jp.reduce(function (a, b) { return a + b; }, 0);
    var mx = ALL.reduce(function (a, b) { return b.jp > a.jp ? b : a; }), mn = ALL.reduce(function (a, b) { return b.jp < a.jp ? b : a; });
    var low = jp.filter(function (v) { return v <= 44; }).length;
    [[ALL.length + '日', '記録日数'], [(sum / jp.length).toFixed(1), '日本株の平均'], [mx.jp, '日本株の最高（' + (+mx.date.slice(5, 7)) + '/' + (+mx.date.slice(8)) + '）'],
     [mn.jp, '日本株の最低（' + (+mn.date.slice(5, 7)) + '/' + (+mn.date.slice(8)) + '）'], [Math.round(low / jp.length * 100) + '%', '「恐怖」以下だった日の割合']]
      .forEach(function (x) { var d = el('div', 'stat'); d.appendChild(el('b', '', String(x[0]))); d.appendChild(el('span', '', x[1])); box.appendChild(d); });
  }

  function filters() {
    var box = document.getElementById('filters'); box.textContent = '';
    box.appendChild(el('span', 'lab', '日本株の区分：'));
    var defs = [{ k: 'all', name: '全て', n: ALL.length }].concat(ZONES.map(function (z) { return { k: z.k, name: z.name, n: ALL.filter(function (e) { return zoneOf(e.jp).k === z.k; }).length }; }));
    defs.forEach(function (d) {
      if (d.k !== 'all' && d.n === 0) return;
      var b = el('button', '', d.name + '（' + d.n + '）'); b.type = 'button'; b.setAttribute('aria-pressed', String(filter === d.k));
      b.addEventListener('click', function () { filter = d.k; page = 1; render(); }); box.appendChild(b);
    });
  }

  function list() {
    var box = document.getElementById('list'); box.textContent = '';
    var rows = ALL.filter(function (e) { return filter === 'all' || zoneOf(e.jp).k === filter; });
    var pages = Math.max(1, Math.ceil(rows.length / PER)); if (page > pages) page = pages;
    rows.slice((page - 1) * PER, page * PER).forEach(function (e) {
      var d = el('div', 'day'), h = el('div', 'day-head');
      h.appendChild(el('span', 'day-date', fmtDate(e.date)));
      var s1 = el('span', 'day-score'); s1.appendChild(document.createTextNode('日本株 ')); s1.appendChild(el('b', '', String(e.jp))); s1.appendChild(chip(e.jp)); h.appendChild(s1);
      if (e.us !== null && e.us !== undefined) {
        var s2 = el('span', 'day-score'); s2.appendChild(document.createTextNode('米国株 ')); s2.appendChild(el('b', '', String(e.us))); s2.appendChild(chip(e.us));
        s2.appendChild(el('span', '', '日米差 ' + sgn(e.jp - e.us))); h.appendChild(s2);
      }
      d.appendChild(h); d.appendChild(el('p', '', e.text || ''));
      if (e.post) { var a = el('a', 'more', 'この日のブログを読む →'); a.href = e.post; d.appendChild(a); }
      box.appendChild(d);
    });
    if (!rows.length) box.appendChild(el('p', 'note-small', '該当する日はありません。'));
    var pg = document.getElementById('pager'); pg.textContent = '';
    if (pages > 1) for (var i = 1; i <= pages; i++) (function (n) {
      var b = el('button', '', String(n)); b.type = 'button'; if (n === page) b.setAttribute('aria-current', 'true');
      b.addEventListener('click', function () { page = n; render(); window.scrollTo({ top: document.getElementById('stats').offsetTop - 20 }); }); pg.appendChild(b);
    })(i);
  }

  function render() { stats(); filters(); list(); }

  fetch('/data/archive.json?t=' + Date.now(), { cache: 'no-store' })
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (j) {
      ALL = (j.entries || []).slice().sort(function (a, b) { return a.date < b.date ? 1 : -1; });
      if (!ALL.length) { document.getElementById('list').appendChild(el('p', 'note-small', 'まだ記録がありません。毎営業日に自動で追加されます。')); return; }
      render();
    })
    .catch(function () { document.getElementById('list').appendChild(el('p', 'note-small', '記録を読み込めませんでした。しばらくしてから再読み込みしてください。')); });
})();
</script>
"""
    html = shell(
        "archive",
        "市況アーカイブ｜日本株・米国株の恐怖と強欲指数の日次記録｜Fear & Greed Index Japan",
        "日本株と米国株の恐怖と強欲指数を営業日ごとに記録した市況アーカイブ。区分の入れ替わりや日米の温度差を、日別に振り返れます。",
        "/archive",
        "市況アーカイブ",
        body,
        wide=True,
        og_type="website",
    )
    return html.replace("</main>", js + "</main>", 1)


# ═════════════════════════════════════════════
#  指数別の統計データ (/stats)  ※試験公開
# ═════════════════════════════════════════════
def build_stats():
    body = """
      <h1>指数別の統計データ <span class="chip n" style="vertical-align:middle;font-size:12px">試験公開</span></h1>
      <p class="lead">当サイトの日本株の恐怖と強欲指数が各区分にあった日に、その後の日経平均がどう動いたかを、過去のデータで集計しました。区分ごとの滞在日数、5・20・60営業日後の騰落率、全期間との差をまとめています。</p>
      <div class="callout warn"><p><strong>これは過去の集計です。</strong>将来の値動きを予測・保証するものではなく、売買を推奨するものでもありません。数値は「そうなる」という意味ではなく、「過去にはこうだった」という記録です。</p></div>

      <noscript><div class="callout warn"><p>この統計の表示にはJavaScriptが必要です。ブラウザの設定でJavaScriptを有効にしてください。</p></div></noscript>
      <div class="stats" id="st-meta" aria-live="polite"></div>
      <div id="st-empty"></div>

      <section id="days" style="padding-top:28px">
        <h2>① 区分ごとの滞在日数</h2>
        <p>指数がどの区分にどれだけの日数あったかを示します。「局面」は、同じ区分が連続した1つの塊を1と数えたものです。</p>
        <div class="table-scroll"><table class="doc" id="tbl-days"></table></div>
      </section>

      <section id="fwd" style="padding-top:28px">
        <h2>② その後の日経平均の動き</h2>
        <p>指数がその区分にあった日の終値から、一定の営業日後の終値までの騰落率を集計しました。見たい期間を選んでください。</p>
        <div class="filters" id="hz" role="group" aria-label="見る期間"></div>
        <div class="table-scroll"><table class="doc" id="tbl-fwd"></table></div>
        <div class="table-scroll" style="margin-top:18px"><table class="doc">
          <thead><tr><th>用語</th><th>意味</th></tr></thead>
          <tbody>
            <tr><th>中央値</th><td>結果を小さい順に並べたときの真ん中の値。極端な値の影響を受けにくい指標です。</td></tr>
            <tr><th>全期間との差</th><td>その区分の中央値から、全営業日の中央値（下の「全期間」）を引いた値です。差が小さければ、その区分にあったことは結果にほとんど影響していなかったことになります。</td></tr>
            <tr><th>上昇した割合</th><td>騰落率がプラスだった日の割合です。</td></tr>
            <tr><th>下位10%〜上位10%</th><td>結果のばらつきを示します。下位10%の値以下だったのが全体の1割、上位10%の値以上だったのが全体の1割です。</td></tr>
            <tr><th>参考程度</th><td>局面の数が10未満の区分に付けます。少ない出来事に左右されやすく、偶然の影響が大きくなります。</td></tr>
          </tbody>
        </table></div>
      </section>

      <section id="method" style="padding-top:28px">
        <h2>③ 集計方法</h2>
        <div class="table-scroll"><table class="doc">
          <thead><tr><th>項目</th><th>内容</th></tr></thead>
          <tbody>
            <tr><th>指数の計算</th><td>当サイトの日本株の指数と同じ方法（6つの指標、過去1年の中での位置、直近3営業日の平均）で、過去の日経平均・ドル円・国債利回り・TOPIX連動ETFのデータから再計算しています。</td></tr>
            <tr><th>先読みなし</th><td>各日の指数は、その日までのデータだけで計算しています。将来のデータは使っていません。</td></tr>
            <tr><th>除外する期間</th><td>指数を計算できた最初の約1年は、比較する期間が短く値が不安定なため、集計から外しています。</td></tr>
            <tr><th>見ている価格</th><td>日経平均の終値です。配当、売買コスト、税金は含みません。</td></tr>
            <tr><th>「N営業日後」</th><td>その日の終値から、N営業日後の終値までの騰落率です。まだN営業日後が来ていない直近の日は、その期間の集計に含まれません。</td></tr>
            <tr><th>更新</th><td>自動で約1日に1回、再計算します。</td></tr>
          </tbody>
        </table></div>
      </section>

      <section id="cautions" style="padding-top:28px">
        <h2>④ 読むときの注意</h2>
        <div class="table-scroll"><table class="doc">
          <thead><tr><th>注意点</th><th>内容</th></tr></thead>
          <tbody>
            <tr><th>日数は独立した観測ではない</th><td>隣り合う日は、見ている期間が重なるため結果が似ます。日数が多くても、独立した出来事の数ではありません。「局面」の数を目安にしてください。</td></tr>
            <tr><th>局面が少ない区分</th><td>極端な区分は出現が少なく、少数の出来事に左右されます。「参考程度」の表示がある区分は、特に慎重に見てください。</td></tr>
            <tr><th>期間による偏り</th><td>集計した期間の相場環境（上昇が続いた時期が多いなど）の影響を受けます。</td></tr>
            <tr><th>過去は将来を保証しない</th><td>過去にそうだった区分でも、今後同じ結果になるとは限りません。</td></tr>
            <tr><th>算出方法の見直し</th><td>指数の計算方法を見直した場合、過去分を含めて数値が変わることがあります。</td></tr>
            <tr><th>個別の売買判断ではない</th><td>この統計は、投資判断の材料の1つとして整理したものです。特定の金融商品の売買を勧誘・推奨するものではありません。</td></tr>
          </tbody>
        </table></div>
        <p>指数の読み方は<a class="inline" href="/guide">投資ガイド</a>、日々の記録は<a class="inline" href="/archive">市況アーカイブ</a>をご覧ください。</p>
      </section>
"""
    js = r"""
<script>
(function () {
  var DATA = null, hz = '20';
  var LABELS = { '5': '5営業日後（約1週間）', '20': '20営業日後（約1か月）', '60': '60営業日後（約3か月）' };
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; }
  function pct(x, plus) { if (x === null || x === undefined) return '—'; var a = Math.abs(x).toFixed(2); return (x > 0 && plus !== false ? '+' : x < 0 ? '−' : '') + a + '%'; }
  function diff(x) { if (x === null || x === undefined) return '—'; var a = Math.abs(x).toFixed(2); return (x > 0 ? '+' : x < 0 ? '−' : '±') + a + 'pt'; }
  function ymd(s) { var a = s.split('-'); return a[0] + '年' + (+a[1]) + '月' + (+a[2]) + '日'; }
  function cell(tag, txt, cls) { var c = el(tag, cls, txt); return c; }
  function chip(z) { return el('span', 'chip ' + z.key, z.name); }
  function head(tbl, cols) { tbl.textContent = ''; var t = el('thead'), r = el('tr'); cols.forEach(function (c, i) { var th = el('th', i ? 'r' : '', c); r.appendChild(th); }); t.appendChild(r); tbl.appendChild(t); var tb = el('tbody'); tbl.appendChild(tb); return tb; }

  function meta() {
    var box = document.getElementById('st-meta'); box.textContent = '';
    [[ymd(DATA.period.start) + '〜' + ymd(DATA.period.end), '集計期間'], [DATA.period.days.toLocaleString('ja-JP') + '日', '集計した営業日数'], [ymd(DATA.as_of), '最新の対象日']]
      .forEach(function (x) { var d = el('div', 'stat'); var b = el('b', '', x[0]); b.style.fontSize = '18px'; d.appendChild(b); d.appendChild(el('span', '', x[1])); box.appendChild(d); });
  }

  function days() {
    var tb = head(document.getElementById('tbl-days'), ['区分', '日数', '割合', '局面の数', '1局面の平均日数']);
    DATA.zones.forEach(function (z) {
      var r = el('tr'), c0 = el('td'); c0.appendChild(chip(z)); c0.appendChild(document.createTextNode(' ' + z.range)); r.appendChild(c0);
      [z.days.toLocaleString('ja-JP') + '日', z.share.toFixed(1) + '%', z.episodes + '回', z.avg_run === null ? '—' : z.avg_run.toFixed(1) + '日']
        .forEach(function (t) { r.appendChild(cell('td', t, 'r')); });
      tb.appendChild(r);
    });
  }

  function fwd() {
    var tb = head(document.getElementById('tbl-fwd'), ['区分', '対象日数', '中央値', '全期間との差', '平均', '上昇した割合', '下位10%〜上位10%']);
    var base = DATA.baseline.fwd[hz];
    var maxAbs = 0.01; DATA.zones.forEach(function (z) { var f = z.fwd[hz]; if (f) maxAbs = Math.max(maxAbs, Math.abs(f.median)); }); if (base) maxAbs = Math.max(maxAbs, Math.abs(base.median));
    function bar(v) { var w = el('span'); w.style.cssText = 'display:inline-block;height:8px;border-radius:4px;vertical-align:middle;margin-right:8px;background:' + (v < 0 ? 'var(--c-ef)' : 'var(--ink-soft)') + ';width:' + Math.max(2, Math.round(Math.abs(v) / maxAbs * 56)) + 'px'; return w; }
    DATA.zones.forEach(function (z) {
      var f = z.fwd[hz], r = el('tr'), c0 = el('td'); c0.appendChild(chip(z));
      if (z.episodes < 10) { var s = el('small', 'sub', ' 参考程度'); s.style.marginLeft = '6px'; s.style.color = 'var(--muted)'; s.style.whiteSpace = 'nowrap'; c0.appendChild(s); }
      r.appendChild(c0);
      if (!f) { for (var i = 0; i < 6; i++) r.appendChild(cell('td', '—', 'r')); tb.appendChild(r); return; }
      r.appendChild(cell('td', f.n.toLocaleString('ja-JP') + '日', 'r'));
      var m = el('td', 'r'); m.appendChild(bar(f.median)); m.appendChild(document.createTextNode(pct(f.median))); r.appendChild(m);
      r.appendChild(cell('td', base ? diff(Math.round((f.median - base.median) * 100) / 100) : '—', 'r'));
      r.appendChild(cell('td', pct(f.mean), 'r'));
      r.appendChild(cell('td', f.win.toFixed(1) + '%', 'r'));
      r.appendChild(cell('td', pct(f.p10, false) + ' 〜 ' + pct(f.p90), 'r'));
      tb.appendChild(r);
    });
    if (base) {
      var r = el('tr'); r.style.background = '#eef3fb'; var c0 = el('td'); c0.appendChild(el('strong', '', '全期間（比較用）')); r.appendChild(c0);
      r.appendChild(cell('td', base.n.toLocaleString('ja-JP') + '日', 'r'));
      var m = el('td', 'r'); m.appendChild(bar(base.median)); m.appendChild(document.createTextNode(pct(base.median))); r.appendChild(m);
      r.appendChild(cell('td', '—', 'r')); r.appendChild(cell('td', pct(base.mean), 'r')); r.appendChild(cell('td', base.win.toFixed(1) + '%', 'r'));
      r.appendChild(cell('td', pct(base.p10, false) + ' 〜 ' + pct(base.p90), 'r')); tb.appendChild(r);
    }
  }

  function buttons() {
    var box = document.getElementById('hz'); box.textContent = '';
    box.appendChild(el('span', 'lab', '見る期間：'));
    DATA.horizons.forEach(function (h) {
      var b = el('button', '', LABELS[String(h)] || (h + '営業日後')); b.type = 'button'; b.setAttribute('aria-pressed', String(String(h) === hz));
      b.addEventListener('click', function () { hz = String(h); buttons(); fwd(); }); box.appendChild(b);
    });
  }

  fetch('/data/stats.json?t=' + Date.now(), { cache: 'no-store' })
    .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
    .then(function (j) { if (!j.success) throw new Error('no data'); DATA = j; meta(); days(); buttons(); fwd(); })
    .catch(function () {
      document.getElementById('st-empty').appendChild(el('div', 'callout', '統計データを準備中です。自動更新の実行後（通常は公開の翌日まで）に表示されます。'));
      ['days', 'fwd'].forEach(function (id) { var s = document.getElementById(id); if (s) s.style.display = 'none'; });
    });
})();
</script>
"""
    html = shell(
        "stats",
        "指数別の統計データ｜区分ごとのその後の日経平均の動き（試験公開）｜Fear & Greed Index Japan",
        "日本株の恐怖と強欲指数が各区分にあった日の、その後5・20・60営業日の日経平均の動きを過去のデータで集計。中央値・上昇した割合・局面数とあわせて確認できます。",
        "/stats",
        "統計データ",
        body,
        wide=True,
        og_type="website",
    )
    return html.replace("</main>", js + "</main>", 1)


# ═════════════════════════════════════════════
#  ブログ一覧 (/blog)
# ═════════════════════════════════════════════
def chip(v):
    n, k = _zone(v)
    return f'<span class="chip {k}">{n}</span>'


def build_blog_index():
    items = []
    for m in reversed(P.POSTS):          # 新しい記事が上
        tags = "".join(f'<span class="chip n" style="background:#eef2f8;color:#3a4d70;font-weight:500">#{t}</span>' for t in m.TAGS[:5])
        items.append(f"""
      <a class="post-item" href="/blog/{m.DATE_ID}">
        <div class="post-meta"><span>{P.full_label(m)}</span>
          <span>日本株 <strong class="num">{m.JP_SCORE}</strong> {chip(m.JP_SCORE)}</span>
          <span>米国株 <strong class="num">{m.US_SCORE}</strong> {chip(m.US_SCORE)}</span></div>
        <div class="post-title">{m.TITLE}</div>
        <div class="post-excerpt">{m.EXCERPT}</div>
        <div class="tags" style="margin-top:12px">{tags}</div>
      </a>""")
    body = f"""
      <h1>市況ブログ</h1>
      <p class="lead">日本株・米国株の恐怖と強欲指数を軸に、その日の市場と経済ニュースを表で整理します。指標ごとの内訳、日米の温度差、注目の材料をまとめています。</p>
      <p class="note-small">全{len(P.POSTS)}本のレポート ｜ 日々の数値の記録は<a class="inline" href="/archive">市況アーカイブ</a>でご覧いただけます。</p>
      <div id="posts">{''.join(items)}
      </div>
"""
    return shell(
        "blog",
        "ブログ｜日本株・米国株の市況レポート｜Fear & Greed Index Japan",
        "日経平均・米国株の恐怖と強欲指数を軸に、その日の市場と経済ニュースを表で整理する市況ブログ。日銀・CPI・為替・米国市場の動きをまとめています。",
        "/blog",
        "ブログ",
        body,
        wide=True,
        og_type="website",
    )


# ═════════════════════════════════════════════
#  ブログ記事 (/blog/YYYYMMDD)  ※前の記事／次の記事のリンク付き
# ═════════════════════════════════════════════
def build_post(m, prev, nxt):
    body = postnav.top_nav(prev, nxt) + m.build() + postnav.bottom_nav(prev, nxt)
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": m.TITLE,
        "description": m.DESCRIPTION,
        "datePublished": m.PUBLISHED_ISO,
        "dateModified": m.PUBLISHED_ISO,
        "inLanguage": "ja",
        "mainEntityOfPage": f"{SITE}/blog/{m.DATE_ID}",
        "image": f"{SITE}/thumbnail.png",
        "author": {"@type": "Organization", "name": "Fear & Greed Index Japan 運営事務局"},
        "publisher": {"@type": "Organization", "name": "Fear & Greed Index Japan", "url": SITE + "/"},
        "keywords": ", ".join(m.TAGS),
    }
    meta = (f'<meta property="article:published_time" content="{m.PUBLISHED_ISO}">\n'
            f'<meta property="article:section" content="市況ブログ">')
    return shell(
        "blog",
        m.META_TITLE + "｜Fear & Greed Index Japan",
        m.DESCRIPTION,
        f"/blog/{m.DATE_ID}",
        m.TITLE,
        body,
        extra_ld=ld,
        wide=True,
        og_type="article",
        crumbs=[("ブログ", "/blog"), (P.crumb_label(m), None)],
        extra_head=meta + "\n" + SB_CSS + "\n" + postnav.CSS,
    )


# ═════════════════════════════════════════════
#  robots / sitemap / ads.txt
# ═════════════════════════════════════════════
def pages():
    return ([("/", "daily", "1.0", PUBLISH_ISO), ("/archive", "daily", "0.8", PUBLISH_ISO), ("/blog", "daily", "0.8", PUBLISH_ISO)]
            + [(f"/blog/{m.DATE_ID}", "monthly", "0.7", m.PUBLISHED_ISO) for m in reversed(P.POSTS)]
            + [("/stats", "weekly", "0.6", PUBLISH_ISO)]
            + [("/guide", "monthly", "0.7", PUBLISH_ISO), ("/about", "yearly", "0.5", PUBLISH_ISO),
               ("/terms", "yearly", "0.3", PUBLISH_ISO), ("/privacy", "yearly", "0.3", PUBLISH_ISO)])


def build_sitemap():
    urls = "\n".join(
        f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{lm}</lastmod>\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>"
        for p, cf, pr, lm in pages())
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
ADS = "google.com, pub-9496300145102373, DIRECT, f08c47fec0942fa0\n"


def main():
    os.makedirs("blog", exist_ok=True)
    open("archive.html", "w", encoding="utf-8").write(build_archive())
    open("blog.html", "w", encoding="utf-8").write(build_blog_index())
    open("stats.html", "w", encoding="utf-8").write(build_stats())
    for i, m in enumerate(P.POSTS):
        prev = P.POSTS[i - 1] if i > 0 else None
        nxt = P.POSTS[i + 1] if i + 1 < len(P.POSTS) else None
        open(f"blog/{m.DATE_ID}.html", "w", encoding="utf-8").write(build_post(m, prev, nxt))
    open("sitemap.xml", "w", encoding="utf-8").write(build_sitemap())
    open("robots.txt", "w", encoding="utf-8").write(ROBOTS)
    open("ads.txt", "w", encoding="utf-8").write(ADS)
    print("built archive, blog index, %d post(s), sitemap, robots, ads" % len(P.POSTS))


if __name__ == "__main__":
    main()
