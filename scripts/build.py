#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a small, dependency-free, readable-without-JavaScript support site."""
import json
import hashlib
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
CONFIG = json.loads((ROOT / "site.json").read_text())
NAME = CONFIG["name"]
BASE = CONFIG["base_url"].rstrip("/")
CONTACT = CONFIG["contact"]
IS_GITHUB = CONTACT["provider"] == "github"

def e(value):
    return escape(str(value), quote=True)

def checked_url(value):
    if urlparse(value).scheme != "https":
        raise ValueError("Public URLs must use HTTPS")
    return value

for value in [BASE, CONTACT["url"], CONTACT.get("feedback_url", CONTACT["url"])]:
    checked_url(value)
if CONTACT["provider"] not in {"github", "google"}:
    raise ValueError("Contact provider must be github or google")
if CONFIG.get("app_store_url"):
    checked_url(CONFIG["app_store_url"])

def contact_notice():
    if IS_GITHUB:
        return "GitHubへのログインが必要です。投稿内容と添付画像は公開されます。氏名・メールアドレスなどの個人情報は記入しないでください。回答は投稿したIssue上で行います。"
    return "Googleフォームを開きます。送信画面の案内をご確認ください。回答に不要な個人情報は記入しないでください。"

def page(slug, title, description, body, absolute_assets=False):
    prefix = BASE + "/" if absolute_assets else ("../" if slug else "./")
    link = lambda path: prefix + path
    canonical = BASE + (f"/{slug}/" if slug else "/")
    page_title = title if title == NAME else f"{title}｜{NAME}"
    asset = lambda name: link("assets/" + name) + "?v=" + hashlib.sha256((ROOT / "src/assets" / name).read_bytes()).hexdigest()[:12]
    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{e(page_title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:site_name" content="{e(NAME)}">
  <meta property="og:title" content="{e(page_title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:image" content="{e(BASE)}/assets/app-icon.png">
  <meta name="twitter:card" content="summary">
  <meta name="theme-color" content="#f8f6f0">
  <link rel="icon" href="{link('assets/favicon.png')}" type="image/png">
  <link rel="apple-touch-icon" href="{link('assets/app-icon.png')}">
  <link rel="stylesheet" href="{asset('site.css')}">
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{prefix}"><img src="{link('assets/app-icon.png')}" width="32" height="32" alt="">{e(NAME)}</a>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
  <nav aria-label="関連情報">
    <a href="{link('support/')}">サポート</a>
    <a href="{link('privacy/')}">プライバシーポリシー</a>
    <a href="{link('sources/')}">出典</a>
  </nav>
  <p>© 2026 {e(CONFIG['owner'])}</p>
</div></footer>
</body></html>
'''

def home():
    description = "名作をやさしい英語で読めるiPhoneアプリです。"
    content = f'''<main id="main" class="wrap home">
  <h1>{e(NAME)}</h1>
  <p>{description}</p>
  <div class="actions">
    <a class="button" href="{e(CONFIG['app_store_url'])}">App Storeで見る</a>
    <a href="support/">サポート・お問い合わせ</a>
  </div>
</main>'''
    return page("", NAME, description, content)

def document(slug, title, intro, toc, content):
    links = "".join(f'<a href="#{key}">{e(label)}</a>' for key, label in toc)
    return page(slug, title, intro, f'''<main id="main" class="wrap document">
  <h1>{e(title)}</h1>
  <p>{intro}</p>
  <nav class="toc" aria-label="ページ内の目次">{links}</nav>
  {content}
</main>''')


def support():
    feedback = CONTACT.get("feedback_url", CONTACT["url"])
    faqs = [
        ("日本語訳はどうやって見ますか？", "英文を一文タップすると日本語訳が開きます。読書画面の「対訳」では英語と日本語を並べて読めます。"),
        ("高品質音声はどうやって使いますか？", "読書画面の「音声と速度」から、約380MBの音声モデルを取得します。利用条件が表示されたら、内容を確認して同意してください。取得後は「高品質音声」を選ぶと、オフラインで音読できます。"),
        ("音が出ないときは？", "iPhoneの音量と音声の出力先を確認してください。「音声と速度」でApple音声を選ぶと、モデルをダウンロードせずに音読できます。"),
        ("文字サイズや背景を変えるには？", "読書画面の「Aa」で、文字サイズ、行間、背景を変更できます。"),
    ]
    faq_html = "".join(f'<details><summary>{e(question)}</summary><p>{e(answer)}</p></details>'
                       for question, answer in faqs)
    content = f'''<section id="contact">
  <h2>お問い合わせ</h2>
  <div class="actions">
    <a class="button" href="{e(CONTACT['url'])}">お問い合わせフォーム</a>
    <a href="{e(feedback)}">ご意見・ご要望</a>
  </div>
  <p class="notice">{e(contact_notice())}</p>
</section>
<section id="faq">
  <h2>よくある質問</h2>
  {faq_html}
</section>'''
    return document("support", "サポート", "使い方のご案内とお問い合わせ窓口です。",
                    [("contact", "お問い合わせ"), ("faq", "よくある質問")], content)


def privacy():
    contact_paragraph = "お問い合わせにはGitHub Issuesを利用します。送信者のGitHubアカウント名、投稿本文、添付画像、やり取りはGitHub上に公開されます。開発者はご相談への回答、不具合の調査、改善のためにこれらの情報を確認します。公開の場ですので、氏名・メールアドレス・電話番号・パスワードなどを記入しないでください。投稿の訂正・削除に関するご相談は、該当Issueのコメントからお知らせください。" if IS_GITHUB else "お問い合わせにはGoogleフォームを利用します。送信内容はご相談への回答、不具合の調査、改善のために確認します。個人情報は回答に必要な範囲にとどめ、送信画面の案内をご確認ください。情報の訂正・削除に関するご相談もお問い合わせフォームから受け付けます。"
    provider_link = '<a href="https://docs.github.com/ja/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシーに関する声明</a>' if IS_GITHUB else '<a href="https://policies.google.com/privacy?hl=ja">Googleのプライバシーポリシー</a>'
    content = f'''<div class="policy-summary"><p><strong>読むためのデータは、端末の中に。</strong><br>本アプリの開発者は、読んだ作品・本文・読書位置・音読内容を収集・送信する機能を設けていません。問い合わせは外部サービスで別に受け付けます。</p></div>
<section id="scope"><h2>1. 適用範囲と運営者</h2><p>このポリシーは「{e(NAME)}」（以下「本アプリ」）と、そのサポートサイトに適用します。運営者は <a href="https://github.com/{e(CONFIG['owner'])}">{e(CONFIG['owner'])}</a> です。お問い合わせは<a href="../support/#contact">サポート窓口</a>から受け付けます。</p></section>
<section id="device"><h2>2. アプリ内で保存する情報</h2><p>読書・音読を再開するための位置、読了状態、表示テーマ・文字サイズ・行間、対訳の表示、音声と再生速度の設定を端末内に保存します。高品質音声の利用条件に同意した場合は、同意した条件の版も端末に保存します。任意で取得した高品質音声の音声合成モデルも端末内に保存し、合成音声の一時ファイルは再生処理に使用します。</p><p>本アプリ独自のアカウント登録、広告配信、行動解析、他アプリをまたぐトラッキング、クラウド同期の機能は設けていません。端末内の読書記録や設定を開発者のサーバーへ送信しません。</p></section>
<section id="network"><h2>3. 音声とネットワーク通信</h2><p>Apple音声はiOSの読み上げ機能を利用し、高品質音声は取得済みのSupertonic 3モデルを使って端末内で合成します。本アプリが本文を外部の翻訳API・音声合成APIへ送信する構成ではありません。</p><p>高品質音声のデータをダウンロードするときはGitHub Releasesとその配信先へ接続します。この通信では配信事業者がIPアドレスなど通信に必要な情報を処理する場合があります。作品の閲覧履歴・読書位置・音読内容はダウンロード先へ送信しません。</p><p>出典・参考文献・サポートなどの外部リンクを選ぶと外部サイトを開きます。リンク先にはそのサービスの規約とプライバシーポリシーが適用されます。</p></section>
<section id="contact-data"><h2>4. お問い合わせの情報</h2><p>{contact_paragraph}</p><p>問い合わせサービスによる情報の取り扱いは、{provider_link}もご確認ください。</p></section>
<section id="website"><h2>5. このウェブサイト</h2><p>本サイトはGitHub Pagesで配信しています。本サイト独自の広告、アクセス解析、追跡用Cookieは使用しません。サイト配信に伴うアクセス情報はGitHubが取り扱う場合があります。詳しくは<a href="https://docs.github.com/ja/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシーに関する声明</a>をご確認ください。</p></section>
<section id="delete"><h2>6. 端末内データの削除・バックアップ</h2><p>iPhoneの設定から本アプリを削除すると、端末内の読書記録・設定・取得した音声合成モデルも削除されます。「Appを取り除く」はデータを保持するiOSの機能のため、削除する場合は「Appを削除」を選んでください。</p><p>iOSが提供するバックアップ・端末移行・診断などはAppleの設定とポリシーに従います。本アプリ独自のクラウド同期とは別の仕組みです。音声モデルの保存場所はバックアップ対象外としています。</p></section>
<section id="change"><h2>7. ポリシーの変更・連絡先</h2><p>機能や情報の取り扱いを変更した場合は、このページを更新します。本ポリシーについてのご相談も<a href="../support/#contact">お問い合わせフォーム</a>からお送りください。</p><p class="updated">制定・最終更新：{e(CONFIG['updated'])}</p></section>'''
    return document("privacy", "プライバシーポリシー", "アプリの読書データ、音声、外部サービス、お問い合わせに関する情報の取り扱いを説明します。", [("scope","適用範囲"),("device","端末内の情報"),("network","音声と通信"),("contact-data","お問い合わせ"),("website","ウェブサイト"),("delete","削除とバックアップ"),("change","変更・連絡先")], content)

def sources():
    content = '''<section id="books">
  <h2>作品の出典</h2>
  <p>作品ごとの底本、出典、青空文庫の入力・校正の情報は、アプリ内の「作品情報と出典」でご覧いただけます。</p>
  <p><a href="https://www.aozora.gr.jp/guide/kijyunn.html">青空文庫収録ファイルの取り扱い規準</a></p>
</section>
<section id="software">
  <h2>音声・ソフトウェア</h2>
  <p>利用ライブラリとライセンスは、アプリ内の「ソフトウェアと出典」に掲載しています。</p>
  <p><a href="https://huggingface.co/Supertone/supertonic-3/blob/main/LICENSE">Supertonic 3のライセンス</a></p>
</section>'''
    return document("sources", "出典", "作品とソフトウェアの出典をご案内します。",
                    [("books", "作品の出典"), ("software", "音声・ソフトウェア")], content)


def main():
    OUT.mkdir(exist_ok=True)
    assets = OUT / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("app-icon.png", "favicon.png", "site.css"):
        shutil.copyfile(ROOT / "src/assets" / name, assets / name)
    for slug, render in [("", home), ("support", support), ("privacy", privacy), ("sources", sources)]:
        folder = OUT / slug
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(render(), encoding="utf-8")
    (OUT / "404.html").write_text(page("", "ページが見つかりません", "お探しのページが見つかりません。", '<main id="main" class="wrap document"><h1>ページが見つかりません。</h1><p>リンクが変わったか、ページが存在しない可能性があります。</p><a class="button" href="' + e(BASE) + '/">ホームへ戻る</a></main>', absolute_assets=True), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{BASE}/{slug}</loc></url>" for slug in ["", "support/", "privacy/", "sources/"])
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>')
    print(f"Built 4 pages and a 404 page in {OUT}")

if __name__ == "__main__":
    main()
