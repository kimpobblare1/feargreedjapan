# -*- coding: utf-8 -*-
"""terms.html / privacy.html 생성 (about.html, guide.html 도 함께 다시 빌드)"""
import build_pages as bp
from build_pages import shell, toc, val

GOOGLE_PARTNER = "https://policies.google.com/technologies/partner-sites?hl=ja"
GOOGLE_ADS = "https://policies.google.com/technologies/ads?hl=ja"
GOOGLE_PRIVACY = "https://policies.google.com/privacy?hl=ja"
GA_PROTECT = "https://support.google.com/analytics/answer/6004245?hl=ja"


def ext(url, label):
    return f'<a class="inline" href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'


# ═════════════════════════════════════════════
#  利用規約 (terms.html)
# ═════════════════════════════════════════════
def build_terms():
    items = [
        ("a1", "第1条（適用）"),
        ("a2", "第2条（本サービスの内容）"),
        ("a3", "第3条（利用条件・費用）"),
        ("a4", "第4条（投資情報に関する注意）"),
        ("a5", "第5条（禁止事項）"),
        ("a6", "第6条（知的財産権）"),
        ("a7", "第7条（データの提供元・外部サービス）"),
        ("a8", "第8条（リンク）"),
        ("a9", "第9条（サービスの変更・中断・終了）"),
        ("a10", "第10条（免責事項）"),
        ("a11", "第11条（規約の変更）"),
        ("a12", "第12条（準拠法・管轄）"),
    ]
    body = f"""
      <h1>利用規約</h1>
      <p class="lead">この利用規約は、Fear &amp; Greed Index Japan（以下「当サイト」）の利用条件を定めるものです。ご利用の前にお読みください。</p>

{toc(items)}

      <section id="a1">
        <h2>第1条（適用）</h2>
        <ol class="clauses">
          <li>本規約は、当サイトが提供する情報およびサービス（以下「本サービス」）を利用する方（以下「利用者」）と、当サイトの運営者（<a class="inline" href="/about#operator">「サイトについて」</a>に記載。以下「運営者」）との間の、本サービスの利用に関わる一切の関係に適用されます。</li>
          <li>利用者は、本サービスを利用することにより、本規約に同意したものとみなします。</li>
          <li>当サイト上に掲載する個別の注意書きや、<a class="inline" href="/privacy">プライバシーポリシー</a>は、本規約の一部を構成します。</li>
        </ol>
      </section>

      <section id="a2">
        <h2>第2条（本サービスの内容）</h2>
        <p>本サービスは、日本株および米国株の投資家心理を数値化した指数（恐怖と強欲指数）と、その解説を提供する情報サイトです。売買注文の受付、投資の助言、金融商品の仲介、その他の取引に関するサービスは提供しません。</p>
      </section>

      <section id="a3">
        <h2>第3条（利用条件・費用）</h2>
        <ol class="clauses">
          <li>本サービスは、会員登録なしで、無料でご利用いただけます。</li>
          <li>本サービスの閲覧に必要な機器、通信回線、通信費用などは、利用者の負担とします。</li>
        </ol>
      </section>

      <section id="a4">
        <h2>第4条（投資情報に関する注意）</h2>
        <ol class="clauses">
          <li>本サービスに掲載する指数、数値、解説その他の情報は、投資家心理を示す参考情報です。特定の金融商品の売買その他の取引を勧誘・推奨するものではありません。</li>
          <li>当サイトは、金融商品取引法に基づく投資助言・代理業、投資運用業その他の金融商品取引業を行うものではありません。</li>
          <li>指数は過去および現在のデータに基づく参考値です。将来の市場動向や投資成果を予測・保証するものではありません。</li>
          <li>投資には、価格の変動などにより元本を割り込むリスクがあります。投資に関する最終的な判断は、利用者ご自身の責任で行ってください。必要に応じて、金融機関や専門家にご相談ください。</li>
        </ol>
      </section>

      <section id="a5">
        <h2>第5条（禁止事項）</h2>
        <p>利用者は、本サービスの利用にあたり、次の行為をしてはなりません。</p>
        <ol class="paren">
          <li>法令または公序良俗に違反する行為</li>
          <li>運営者または第三者の知的財産権、プライバシーその他の権利・利益を侵害する行為</li>
          <li>本サービスの運営を妨害する行為（サーバーやネットワークに過度な負荷をかける行為、不正アクセスを含みます）</li>
          <li>検索エンジンの通常のクロールを除き、プログラムなどの自動化された手段で、本サービスまたは当サイトのデータ提供機能に繰り返しアクセスする行為（運営者が許可した場合を除きます）</li>
          <li>本サービスの情報を、出典を示さずに、または改変したうえで、自己または第三者の情報として公開・配布する行為</li>
          <li>当サイトが特定の金融商品を推奨しているかのような誤解を与える方法で、本サービスの情報を引用・利用する行為</li>
          <li>その他、運営者が不適切と判断する行為</li>
        </ol>
      </section>

      <section id="a6">
        <h2>第6条（知的財産権）</h2>
        <ol class="clauses">
          <li>本サービスの文章、デザイン、プログラムその他のコンテンツに関する著作権などの権利は、運営者または正当な権利者に帰属します。</li>
          <li>著作権法上認められる範囲での引用は、出典として当サイト名とURLを明記し、引用部分が明確に区別できる形で行う場合に限り認めます。</li>
          <li>引用の範囲を超える転載、複製、販売、その他の利用には、あらかじめ運営者の許可が必要です。</li>
          <li>「日経平均株価」「日経225」に関する知的財産権は、株式会社日本経済新聞社に帰属します。米国株の恐怖と強欲指数に関する権利は、CNN Businessなどの権利者に帰属します。</li>
        </ol>
      </section>

      <section id="a7">
        <h2>第7条（データの提供元・外部サービス）</h2>
        <ol class="clauses">
          <li>本サービスは、Yahoo Finance、財務省、CNN Businessなど第三者が提供するデータを利用しています。これらのデータの内容、正確性、継続的な提供について、運営者は保証しません。</li>
          <li>提供元の都合により、データの表示が遅れたり、内容が変更されたり、取得できなくなったりする場合があります。</li>
          <li>当サイトからリンクする外部サイトの内容について、運営者は責任を負いません。</li>
        </ol>
      </section>

      <section id="a8">
        <h2>第8条（リンク）</h2>
        <p>当サイトへのリンクは、原則として自由です。ただし、違法または公序良俗に反するサイトからのリンク、当サイトの信用を損なうおそれのあるリンク、誤認を与える態様のリンクはお断りします。</p>
      </section>

      <section id="a9">
        <h2>第9条（サービスの変更・中断・終了）</h2>
        <p>運営者は、利用者に事前に通知することなく、本サービスの内容を変更し、または提供を中断・終了することがあります。</p>
      </section>

      <section id="a10">
        <h2>第10条（免責事項）</h2>
        <ol class="clauses">
          <li>運営者は、本サービスの情報について、正確性、完全性、最新性、有用性、特定の目的への適合性を保証しません。</li>
          <li>運営者は、本サービスの利用または利用不能により利用者に生じた損害（投資による損失を含みます）について、運営者に故意または重大な過失がある場合を除き、責任を負いません。</li>
          <li>本条の規定が、消費者契約法その他の法令により適用されない場合は、その範囲で適用されないものとします。</li>
        </ol>
      </section>

      <section id="a11">
        <h2>第11条（規約の変更）</h2>
        <p>運営者は、必要と判断した場合、利用者に個別に通知することなく、本規約を変更できます。変更後の規約は、当サイトに掲載した時点から効力を生じます。変更後に本サービスを利用した場合、利用者は変更後の規約に同意したものとみなします。</p>
      </section>

      <section id="a12">
        <h2>第12条（準拠法・管轄）</h2>
        <p>本規約は日本法に準拠します。本サービスに関して紛争が生じた場合は、東京地方裁判所を第一審の専属的合意管轄裁判所とします。</p>
      </section>

      <p class="enact">制定日：{val(bp.PUBLISH_DATE, "公開日")}</p>
"""
    return shell(
        "terms",
        "利用規約｜Fear & Greed Index Japan",
        "Fear &amp; Greed Index Japanの利用規約です。投資情報に関する注意、禁止事項、知的財産権、免責事項などを定めています。",
        "/terms",
        "利用規約",
        body,
    )


# ═════════════════════════════════════════════
#  プライバシーポリシー (privacy.html)
# ═════════════════════════════════════════════
def build_privacy():
    items = [
        ("operator", "運営者と基本方針"),
        ("info", "取得する情報"),
        ("purpose", "利用目的"),
        ("analytics", "アクセス解析ツールについて"),
        ("ads", "広告の配信について"),
        ("external", "情報の外部送信について"),
        ("cookie", "Cookieの設定について"),
        ("sharing", "第三者提供・委託・国外での取扱い"),
        ("rights", "開示・訂正・削除などの請求"),
        ("changes", "本ポリシーの変更・お問い合わせ"),
    ]
    body = f"""
      <h1>プライバシーポリシー</h1>
      <p class="lead">Fear &amp; Greed Index Japan（以下「当サイト」）が取得する情報、その利用目的、外部への送信、利用者が選べる設定について説明します。</p>

{toc(items)}

      <section id="operator">
        <h2>運営者と基本方針</h2>
        <p>当サイトの運営者は、次のとおりです。</p>
        <div class="table-scroll">
          <table class="doc narrow">
            <tbody>
              <tr><th>運営者</th><td>{val(bp.OPERATOR, "運営者名または屋号")}</td></tr>
              <tr><th>連絡先</th><td>{val(bp.EMAIL, "連絡用メールアドレス")}</td></tr>
            </tbody>
          </table>
        </div>
        <p>運営者は、個人情報の保護に関する法律（個人情報保護法）その他の関係法令を守り、利用者の情報を適切に取り扱います。</p>
      </section>

      <section id="info">
        <h2>取得する情報</h2>
        <h3>お問い合わせの情報</h3>
        <p>メールでお問い合わせいただいた場合に、メールアドレス、お名前、お問い合わせの内容を取得します。</p>
        <h3>アクセス情報</h3>
        <p>当サイトを閲覧した際に、次のような情報が自動的に取得されます。</p>
        <ul>
          <li>閲覧したページ、閲覧日時、参照元のURL</li>
          <li>IPアドレス、ブラウザ・OS・端末の種類、おおよその地域</li>
          <li>Cookieなどの識別子</li>
        </ul>
        <p>これらの情報のみで、特定の個人を識別することは通常できません。</p>
        <div class="callout">
          <p>当サイトには会員登録がなく、住所、電話番号、クレジットカード情報などを取得することはありません。</p>
        </div>
      </section>

      <section id="purpose">
        <h2>利用目的</h2>
        <p>取得した情報は、次の目的で利用します。</p>
        <ul>
          <li>お問い合わせへの回答・対応</li>
          <li>当サイトの利用状況の把握・分析と、サービスの改善</li>
          <li>広告の配信と、その効果の測定</li>
          <li>不正アクセスの防止など、セキュリティの確保</li>
          <li>法令に基づく対応</li>
        </ul>
        <p>お問い合わせでお預かりしたメールアドレスを、宣伝や営業の連絡に使うことはありません。</p>
      </section>

      <section id="analytics">
        <h2>アクセス解析ツールについて</h2>
        <p>当サイトは、利用状況の把握のために、Google LLCのアクセス解析サービス「Google アナリティクス」を利用しています。Google アナリティクスはCookieを使って、当サイトの閲覧に関する情報を収集します。</p>
        <p>収集される情報は、特定の個人を識別しない形で利用されます。Google アナリティクスによる測定は、ブラウザのアドオンで無効にできます。詳しくは、{ext(GA_PROTECT, "Google アナリティクス ヘルプ「データの保護」")}をご覧ください。また、Googleによる情報の取扱いについては、{ext(GOOGLE_PARTNER, "Googleのサービスを使用するサイトやアプリから収集した情報のGoogleによる使用")}をご確認ください。</p>
      </section>

      <section id="ads">
        <h2>広告の配信について</h2>
        <p>当サイトは、Googleなどの第三者配信事業者が提供する広告配信サービス「Google アドセンス」を利用しています。</p>
        <ul>
          <li>第三者配信事業者は、Cookieを使用して、利用者が当サイトや他のサイトに過去にアクセスした際の情報に基づいて、広告を配信します。</li>
          <li>Googleが広告Cookieを使用することにより、Googleやそのパートナーは、当サイトや他のサイトへのアクセス情報に基づいて、利用者に広告を表示できます。</li>
          <li>利用者は、Googleの広告設定で、パーソナライズ広告を無効にできます。設定方法は、{ext(GOOGLE_ADS, "Googleの広告に関するページ")}をご覧ください。</li>
        </ul>
        <div class="callout warn">
          <p>広告の内容は、広告配信事業者が決定します。広告に掲載された商品・サービス（金融商品を含みます）は、当サイトが推奨するものではなく、その内容について運営者は責任を負いません。</p>
        </div>
      </section>

      <section id="external">
        <h2>情報の外部送信について</h2>
        <p>当サイトを閲覧すると、利用者のブラウザから、次の事業者に情報が送信されます。</p>
        <div class="table-scroll">
          <table class="doc stack">
            <thead><tr><th>送信先</th><th>送信される情報</th><th>利用目的</th></tr></thead>
            <tbody>
              <tr>
                <th>Google LLC<br>（Google アナリティクス）</th>
                <td data-label="送信される情報">閲覧したページのURL、閲覧日時、参照元、端末・ブラウザ・OSの種類、Cookieなどの識別子、おおよその地域</td>
                <td data-label="利用目的">アクセス状況の分析、サイトの改善</td>
              </tr>
              <tr>
                <th>Google LLC<br>（Google アドセンス）</th>
                <td data-label="送信される情報">Cookieなどの識別子、広告識別子、閲覧したページのURL、広告の表示・クリックなどの情報、IPアドレス、端末・ブラウザの情報</td>
                <td data-label="利用目的">広告の配信、効果の測定、不正の防止</td>
              </tr>
              <tr>
                <th>Google LLC<br>（Google Fonts）</th>
                <td data-label="送信される情報">IPアドレス、ブラウザ・端末の情報</td>
                <td data-label="利用目的">Webフォントの配信</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p>送信先の事業者における情報の取扱いは、各事業者のプライバシーポリシーに従います。Googleについては、{ext(GOOGLE_PRIVACY, "Google プライバシー ポリシー")}をご覧ください。</p>
      </section>

      <section id="cookie">
        <h2>Cookieの設定について</h2>
        <p>Cookieは、ブラウザの設定で、受け入れないようにしたり、削除したりできます。設定方法は、お使いのブラウザのヘルプをご確認ください。</p>
        <p>Cookieを無効にしても、当サイトの閲覧はできます。ただし、広告の表示など一部の機能に影響が出る場合があります。</p>
      </section>

      <section id="sharing">
        <h2>第三者提供・委託・国外での取扱い</h2>
        <h3>第三者への提供</h3>
        <p>運営者は、法令に基づく場合を除き、ご本人の同意なく、個人データを第三者に提供しません。</p>
        <h3>取扱いの委託</h3>
        <p>サイトの運営に必要な範囲で、ホスティング、メールなどのサービス提供事業者に、情報の取扱いを委託する場合があります。その場合は、適切に管理されるよう配慮します。</p>
        <h3>国外での取扱い</h3>
        <p>当サイトは、運営者の所在する大韓民国から運営しています。お預かりした情報は、大韓民国のほか、利用するサービス提供事業者（Googleなど）のサーバーが所在する国・地域（米国など）で、保管・処理される場合があります。</p>
        <h3>安全管理と保管期間</h3>
        <p>運営者は、情報の漏えい、滅失、不正な利用を防ぐため、適切な安全管理措置を講じます。お問い合わせの情報は、対応の完了後、必要な期間だけ保管し、不要になった時点で遅滞なく削除します。</p>
      </section>

      <section id="rights">
        <h2>開示・訂正・削除などの請求</h2>
        <p>ご本人から、お預かりしている個人情報の開示、訂正、追加、削除、利用の停止などのご請求があった場合は、ご本人であることを確認したうえで、法令に従い、合理的な期間内に対応します。ご請求は、下記の連絡先までメールでお送りください。</p>
      </section>

      <section id="changes">
        <h2>本ポリシーの変更・お問い合わせ</h2>
        <p>運営者は、法令の変更やサービスの変更に応じて、本ポリシーを見直し、変更することがあります。変更後の内容は、当サイトに掲載した時点から効力を生じます。</p>
        <p>本ポリシーに関するお問い合わせは、次の連絡先までお願いします。</p>
        <div class="table-scroll">
          <table class="doc narrow">
            <tbody>
              <tr><th>運営者</th><td>{val(bp.OPERATOR, "運営者名または屋号")}</td></tr>
              <tr><th>連絡先</th><td>{val(bp.EMAIL, "連絡用メールアドレス")}</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <p class="enact">制定日：{val(bp.PUBLISH_DATE, "公開日")}</p>
"""
    return shell(
        "privacy",
        "プライバシーポリシー｜Fear & Greed Index Japan",
        "Fear &amp; Greed Index Japanのプライバシーポリシーです。取得する情報、利用目的、Google アナリティクス・アドセンスの利用、情報の外部送信、Cookieの設定について説明しています。",
        "/privacy",
        "プライバシーポリシー",
        body,
    )


# ═════════════════════════════════════════════
#  404 ページ (404.html)  ※Cloudflare が「存在しないURL」で自動的に表示します
# ═════════════════════════════════════════════
def build_404():
    import re
    body = """
      <h1>ページが見つかりません</h1>
      <p class="lead">お探しのページは、移動または削除された可能性があります。URLをご確認のうえ、下のリンクからお探しください。</p>
      <div class="cta">
        <p>トップページでは、日本株と米国株の恐怖と強欲指数を確認できます。</p>
        <a href="/">ダッシュボードへ戻る</a>
      </div>
      <p style="margin-top:20px; font-size:14px;"><a class="inline" href="/guide">投資ガイド</a>　／　<a class="inline" href="/about">サイトについて</a></p>
"""
    page = shell("404", "ページが見つかりません｜Fear & Greed Index Japan", "お探しのページは見つかりませんでした。", "/404", "ページが見つかりません", body)
    # 404 ページは検索結果に載せない・正規URLも持たない
    page = re.sub(r'<link rel="canonical"[^>]*>\n', '', page)
    page = re.sub(r'<meta property="og:url"[^>]*>\n', '', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\n', '', page, flags=re.S)
    page = page.replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"', 1)
    return page


if __name__ == "__main__":
    open("about.html", "w", encoding="utf-8").write(bp.build_about())
    open("guide.html", "w", encoding="utf-8").write(bp.build_guide())
    open("terms.html", "w", encoding="utf-8").write(build_terms())
    open("privacy.html", "w", encoding="utf-8").write(build_privacy())
    open("404.html", "w", encoding="utf-8").write(build_404())
    print("built about, guide, terms, privacy, 404")
