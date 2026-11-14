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
BOOKS = json.loads((ROOT / "src/books.json").read_text())
SAMPLE = json.loads((ROOT / "src/retelling-sample.json").read_text())
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

def icon(name):
    paths = {
        "arrow": '<path d="M4 12h15m-6-6 6 6-6 6"/>',
        "book": '<path d="M12 5v15M3 4c4-1 6 0 9 1 3-1 5-2 9-1v15c-4-1-6 0-9 1-3-1-5-2-9-1z"/>',
        "audio": '<path d="M4 14v-3a8 8 0 0 1 16 0v3M4 12H2v7h4v-7zm16 0h2v7h-4v-7z"/>',
        "offline": '<path d="m3 3 18 18M6 8c5-3 10-2 15 1M3 9l1-1m5 5c3-1 6-1 9 1m-6 5h.01"/>',
        "translate": '<path d="M3 5h12M9 3v2M5 8c1 5 4 8 8 9m0-12c0 5-3 10-10 13m12 3 4-11 4 11m-6-4h4"/>',
        "help": '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5m0 3h.01"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>'

def contact_notice():
    if IS_GITHUB:
        return "GitHubへのログインが必要です。投稿内容と添付画像は公開されます。氏名・メールアドレスなどの個人情報は記入しないでください。回答は投稿したIssue上で行います。"
    return "Googleフォームを開きます。送信画面の案内をご確認ください。回答に不要な個人情報は記入しないでください。"

def page(slug, title, description, body, absolute_assets=False):
    prefix = BASE + "/" if absolute_assets else ("../" if slug else "./")
    link = lambda path: prefix + path
    canonical = BASE + (f"/{slug}/" if slug else "/")
    asset = lambda name: link("assets/" + name) + "?v=" + hashlib.sha256((ROOT / "src/assets" / name).read_bytes()).hexdigest()[:12]
    nav_support = ' aria-current="page"' if slug == "support" else ""
    return f'''<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{e(title)}｜{e(NAME)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:site_name" content="{e(NAME)}">
  <meta property="og:title" content="{e(title)}｜{e(NAME)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(canonical)}">
  <meta property="og:image" content="{e(BASE)}/assets/app-icon.png">
  <meta name="twitter:card" content="summary">
  <meta name="theme-color" content="#f8f6f0">
  <link rel="icon" href="{link('assets/favicon.png')}" type="image/png">
  <link rel="apple-touch-icon" href="{link('assets/app-icon.png')}">
  <link rel="stylesheet" href="{asset('site.css')}">
  <script src="{asset('site.js')}" defer></script>
</head>
<body>
<a class="skip" href="#main">本文へスキップ</a>
<header class="site-header"><div class="wrap header-inner">
  <a class="brand" href="{prefix}" aria-label="{e(NAME)} ホーム"><img src="{link('assets/app-icon.png')}" width="38" height="38" alt=""><span>{e(NAME)}</span></a>
  <nav class="site-nav" aria-label="メインナビゲーション"><a class="nav-reading" href="{prefix}#reading">読み方</a><a class="nav-contact" href="{link('support/')}"{nav_support}>サポート</a></nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
  <div class="footer-top"><a class="brand" href="{prefix}"><img src="{link('assets/app-icon.png')}" width="32" height="32" alt=""><span>{e(NAME)}</span></a>
  <nav class="footer-nav" aria-label="フッターナビゲーション"><a href="{link('support/')}">サポート</a><a href="{link('privacy/')}">プライバシー</a><a href="{link('sources/')}">出典・このサイトについて</a></nav></div>
  <div class="footer-note"><p>本アプリは青空文庫の公式アプリではありません。</p><p>© 2026 {e(CONFIG['owner'])}</p></div>
</div></footer>
</body></html>
'''

def book_cards():
    result = []
    for i, book in enumerate(BOOKS, 1):
        result.append(f'''<li><article aria-labelledby="book-{e(book['id'])}">
          <div class="book-cover" style="--cover:#{e(book['color'])}"><img class="cover-art" src="assets/covers/{e(book['id'])}.jpg" width="360" height="540" loading="lazy" alt=""><span class="edition">AOZORA EDITIONS</span><div class="cover-title"><h3 id="book-{e(book['id'])}">{e(book['title'])}</h3><p>{e(book['author'])}</p></div></div>
          <div class="book-meta"><p lang="en">{e(book['englishTitle'])}</p><a href="{e(book['cardURL'])}">青空文庫の原作 ↗</a></div>
        </article></li>''')
    return "\n".join(result)

def home():
    store = CONFIG.get("app_store_url")
    first_cta = f'<a class="button blue" href="{e(store)}">App Storeで見る {icon("arrow")}</a>' if store else f'<a class="button blue" href="#retelling">英文の実例を見る {icon("arrow")}</a>'
    sample_sentences = "".join(f'<li>{e(sentence)}</li>' for sentence in SAMPLE['english'])
    availability = "iPhone / iOS 17以降" if store else "iPhone / iOS 17以降 · アプリの公開準備中"
    bars = "".join(f'<i style="--h:{h}px"></i>' for h in [12,24,38,20,48,64,42,72,54,34,61,44,29,52,36,20,13])
    body = f'''<main id="main">
<section class="wrap hero" aria-labelledby="hero-title">
  <div class="hero-copy"><p class="eyebrow">{e(CONFIG['subtitle'])}</p><h1 id="hero-title"><span>名作のつづきが、</span><span><em>英語で読める。</em></span></h1>
  <p class="hero-lead">原作の長い一文は、いくつもの短い英文に。<br>難しい表現は、身近な言葉で説明し直す。<br>日本の名作を、中学英語を目安に語り直しました。</p><p class="hero-audience">英語を学び直したい大人のための読書アプリ。</p>
  <div class="actions">{first_cta}<a class="button secondary" href="support/">使い方・サポート</a></div><p class="availability">{availability}</p></div>
  <figure class="hero-visual"><div class="phone"><img src="assets/illustrated-reader.jpg" width="660" height="1434" alt="『注文の多い料理店』の英文と、二人の青年と白い犬を描いた挿絵が並ぶ更新版の実際の読書画面" fetchpriority="high"></div><figcaption class="screen-note">挿絵入り更新版1.3.0の実画面</figcaption></figure>
</section>
<aside class="wrap edition-note" aria-label="挿絵入り更新版について"><strong>NEW EDITION · 1.3.0</strong><p>表紙13枚と挿絵217枚を追加した、次回アップデートをご紹介しています。掲載する挿絵入りの画面は更新版のものです。App Storeでの公開をお待ちください。</p></aside>
<div class="wrap promise-strip" aria-label="アプリの特長"><div>{icon('book')}<span>13作品を、すべて全文。</span></div><div>{icon('translate')}<span>一文ごとに、日本語訳。</span></div><div>{icon('offline')}<span>本文はオフラインで。</span></div></div>
<section class="wrap section art-section" id="illustrations" aria-labelledby="art-title">
  <div class="section-heading"><div><p class="eyebrow">PICTURE THE SCENE. STAY IN THE STORY.</p><h2 id="art-title">英語のすぐそばに、<br>物語の風景を。</h2></div><p>二人が歩く森。小狐の暮らす里。<br>想像を広げる、未来の実験室。</p></div>
  <div class="scene-grid">
    <figure><img src="assets/scenes/restaurant.jpg" width="900" height="600" loading="lazy" alt="秋の山道を進む、洋風の猟服を着た二人と大きな白い犬二匹"><figcaption><span>宮沢賢治</span>注文の多い料理店</figcaption></figure>
    <figure><img src="assets/scenes/gon.jpg" width="900" height="600" loading="lazy" alt="秋の里山で、巣穴の前に立つ小さな狐"><figcaption><span>新美南吉</span>ごん狐</figcaption></figure>
    <figure><img src="assets/scenes/thousand-years.jpg" width="900" height="600" loading="lazy" alt="ベッドや本棚、装置が並ぶ球形の実験室"><figcaption><span>海野十三</span>千年後の世界</figcaption></figure>
  </div><div class="art-details"><p>場面の切れ目に合わせて、全13作品に217枚の挿絵を。英文の内容を思い浮かべながら読み進められます。絵に触れると拡大でき、本文に戻ると同じページへ。表示設定で挿絵を隠すこともできます。</p><p>表紙と挿絵もすべて同梱。オフラインで楽しめます。本アプリ用にAIを用いて独自制作した画像です。</p></div>
</section>
<section class="wrap section retelling-section" id="retelling" aria-labelledby="retelling-title">
  <div class="section-heading"><div><p class="eyebrow">CLASSIC STORIES, RETOLD IN SIMPLE ENGLISH</p><h2 id="retelling-title">名作を、やさしい英語で語り直す。</h2></div><p>出来事をひとつずつ、短い文で。<br>言葉の難しさをほどいて、物語はそのままに。</p></div>
  <p class="retelling-lead">原作の一文をそのまま英語に置き換えるのではなく、伝える内容を整理し、複数の短い英文で説明し直しています。難しい一語も、身近な言葉でわかる表現へ。場面・会話・結末まで残し、物語全体を読みやすい英語につくり直しました。</p>
  <div class="retelling-example"><div class="original-example"><p class="example-label">原作の、長い一文</p><blockquote>{e(SAMPLE['japanese'])}</blockquote><p class="example-source">{e(SAMPLE['author'])}『{e(SAMPLE['title'])}』冒頭<br><a href="{e(SAMPLE['sourceURL'])}">青空文庫の原文を読む ↗</a></p></div>
  <div class="english-example"><p class="example-label">アプリでは、{len(SAMPLE['english'])}つの短い英文に。</p><ol lang="en">{sample_sentences}</ol><p class="example-source">実際に収録している英文です。一文ずつ、場面を思い浮かべながら読めます。</p></div></div>
</section>
<section class="wrap section" id="reading" aria-labelledby="reading-title">
  <div class="section-heading"><div><p class="eyebrow">A STORY, AT YOUR PACE</p><h2 id="reading-title">物語を、自分のペースで。</h2></div><p>気になる一文を確かめながら、<br>英語で読む時間を少しずつ。</p></div>
  <div class="step-grid">
    <article class="step"><div class="number">01</div><div><h3>語り直した英語で、読む。</h3><p>長い一文は短く分け、難しい表現は説明し直す。中学英語を目安に、物語を丸ごと読みやすくしています。</p></div></article>
    <article class="step"><div class="number">02</div><div><h3>その一文だけ、確かめる。</h3><p>英文をタップすると、その文に対応する自然な日本語訳へ。青空文庫の原文も別に参照できます。</p></div></article>
    <article class="step"><div class="number">03</div><div><h3>耳でも、つづきを楽しむ。</h3><p>音読しながら、今の文を目で追って。速度も文字の大きさも、読みやすい設定に変えられます。</p></div></article>
  </div>
</section>
<section class="reading-section" aria-labelledby="translation-title"><div class="wrap reading-grid">
  <div class="reading-copy"><p class="eyebrow">ONE SENTENCE AT A TIME</p><h2 id="translation-title">わからない一文で、<br>物語を止めない。</h2><p>「この文、どういう意味だろう」。<br>日本語で確かめたら、また英語のつづきへ。<br>一文ずつの対訳が、読む時間を支えます。主な単語の意味も訳のすぐ下に表示。詳しい語義もタップで確かめられます。</p><p class="fine">この文章で、対訳を確認する感覚をお試しください。<br>日本語訳は英文に合わせて制作したもので、原文とは別に表示します。</p></div>
  <div class="quote-card"><p class="quote-label">注文の多い料理店 / THE RESTAURANT OF MANY ORDERS</p><p class="sample-english" lang="en">Two young men were walking deep in the mountains.</p><button type="button" class="translation-toggle" data-translation-toggle aria-expanded="false" aria-controls="sample-translation">{icon('translate')}<span>日本語訳を見る</span></button><div class="translation" id="sample-translation" hidden><p>二人の若い男が山奥を歩いていました。</p><small>この英文に対応する日本語訳</small></div><noscript><div class="translation"><p>二人の若い男が山奥を歩いていました。</p></div></noscript><cite class="quote-credit">原作：宮沢賢治『注文の多い料理店』／英訳・日本語訳：本アプリ独自制作</cite></div>
</div></section>
<section class="wrap section" aria-labelledby="books-title"><div class="section-heading"><div><p class="eyebrow">THIRTEEN STORIES, MANY WORLDS</p><h2 id="books-title">あの名作を、もう一度。</h2></div><p>短い寓話から、ミステリー、空想科学まで。<br>13作品すべてを、全文英訳で。</p></div><ol class="book-grid">{book_cards()}</ol><p class="book-note">中学英語は制作上の目安です。固有名詞や、物語を伝えるために必要な言葉も含まれます。</p></section>
<section class="wrap section" aria-labelledby="listen-title"><div class="listen-panel"><div><p class="eyebrow">READ. LISTEN. RETURN.</p><h2 id="listen-title">目で読んで、耳で聴く。</h2><p>Apple音声ですぐに音読。0.5〜2倍速で、今の自分に合う速さを選べます。再生中の文を追いながら、画面をロックして聴くこともできます。</p><p>任意で音声合成モデル「Supertonic 3」（約380MB）を取得すると、iPhone内で英文から高品質な音声を生成できます。取得後は通信せずに音読できます。本文・対訳はダウンロードなしでオフライン閲覧できます。</p></div><div class="audio-graphic" aria-label="0.5倍から2倍までの音読速度に対応"><div class="waveform" aria-hidden="true">{bars}</div><div class="rate-list"><span>0.5×</span><span>0.75×</span><strong>1.0×</strong><span>1.5×</span><span>2.0×</span></div><p>ログイン・広告・アプリ内課金なし</p></div></div></section>
<section class="wrap learning" aria-labelledby="learning-title"><div><p class="eyebrow">THE JOY OF UNDERSTANDING</p><h2 id="learning-title">わかる英語を、<br>たっぷり読む。</h2><p>自分にとって読みやすい文章を、内容を楽しみながら読みつづける。「多読」の考え方をヒントに、やさしい英語と一文の対訳を組み合わせました。理論と参考文献はアプリ内でも紹介しています。</p><a href="sources/#learning">学習方針と参考文献について {icon('arrow')}</a></div><p class="margin-note">読みたいから、読む。<br>わかるから、つづく。<br>そんな英語の時間を。</p></section>
<section class="wrap last-cta" aria-label="App Storeへ"><div><h2>次の一文から、始めよう。</h2><p>名作も、SFも。自分にわかる英語から。</p></div>{first_cta}</section>
</main>'''
    return page("", "名作のつづきが、英語で読める。", "原作の長い一文を複数の短い英文に。難しい表現を身近な言葉で説明し直し、中学英語を目安に語り直した日本の名作13作品。一文の日本語訳と音読も使えるiPhoneリーダー。", body)

def document(slug, title, intro, toc, content):
    links = "".join(f'<a href="#{key}">{e(label)}</a>' for key, label in toc)
    return page(slug, title, intro, f'''<main id="main"><div class="wrap page-head"><p class="breadcrumbs"><a href="../">ホーム</a> / {e(title)}</p><p class="eyebrow">{e(NAME)}</p><h1>{e(title)}</h1><p class="intro">{intro}</p></div><div class="wrap page-layout"><aside class="toc" aria-label="ページ内の目次"><p>このページの内容</p>{links}</aside><div class="prose">{content}</div></div></main>''')

def support():
    provider = "GitHub" if IS_GITHUB else "Google"
    feedback = CONTACT.get("feedback_url", CONTACT["url"])
    faqs = [
        ("どのように、やさしい英語にしていますか？", "原作を一文ずつ直訳するのではなく、長い一文で伝えている内容をいくつもの短い英文に分け、出来事や考えの順序を追いやすくしています。難しい単語も、身近な言葉を使った短い説明に置き換えます。場面・会話・結末を残し、物語全体を中学英語を目安に語り直しています。"),
        ("日本語訳はどうやって見ますか？", "本文の英文を一文タップすると、その英文と対応する日本語訳が開きます。左右端のタップはページ送りです。下部の「対訳」を選ぶと、本文にも英語と日本語訳を並べられます。"),
        ("日本語訳と青空文庫の原文は違いますか？", "一文の日本語訳は、短く書き直した英文に合わせて独自に制作したものです。原文を読むには、対訳パネルの「青空文庫の原文」を開いてください。その文を含む段落の原文を、末尾までスクロールして確認できます。"),
        ("音が出ない、または音読が止まりました。", "iPhoneの音量と音声の出力先、Bluetooth接続を確認してください。「音声と速度」でApple音声を選び、再生ボタンを押してお試しください。着信やイヤホンの取り外し、対訳を開いたときは一時停止する仕様です。対訳を閉じると、その直前に再生していた場合のみ再開します。"),
        ("高品質音声が選べません。", "高品質音声は、音声合成モデル「Supertonic 3」（約380MB）をすべて取得すると選択できます。取得後は、そのモデルを使ってiPhone内で英文から音声を生成します。「音声と速度」からダウンロードしてください。通信状態と空き容量を確認し、Wi-Fiでの取得をおすすめします。未取得の間もApple音声は使えます。"),
        ("音声のダウンロードに失敗・中断した場合は？", "通信状態と十分な空き容量を確認して、もう一度ダウンロードしてください。取得が完了したファイルは再利用されます。取得・合成に失敗した場合もApple音声で読むことができます。"),
        ("インターネットにつながっていなくても使えますか？", "13作品の本文と日本語訳・原文はアプリに同梱しています。端末に用意されているApple音声と、取得済みの高品質音声は端末内で音読します。高品質音声の初回取得、出典や問い合わせなどの外部リンクを開くときは通信が必要です。"),
        ("文字が読みにくい・背景を変えたい。", "読書画面右上の「Aa」から、文字サイズ・行間・背景を変えられます。「紙・白・夜」を選ぶと、設定画面の文字や操作部もその場で切り替わります。"),
        ("どこまで読んだかは保存されますか？", "読書位置と音読位置は別に端末へ保存します。再起動後も保存した位置へ戻れます。音読は自動開始せず、再生ボタンを押すと保存した文の先頭から再開します。アプリ内の前後操作は文単位、ロック画面の前後操作は段落単位です。"),
        ("機種変更やアプリの削除をするとどうなりますか？", "本アプリ独自のクラウド同期はありません。アプリを削除すると端末内の読書記録と音声合成モデルも削除されます。iOSのバックアップや端末移行からの復元はAppleの設定・機能に従います。音声モデルはバックアップの対象外のため、必要に応じて再取得してください。"),
        ("中学で習った単語だけで読めますか？", "中学英語を学び終えた方が読み進めやすいよう、短い文・基本的な語順・身近な言葉で制作しています。固有名詞や物語に必要な文化的な語も含みます。読みやすさには個人差があるため、難しい一文は日本語訳で確かめながらお楽しみください。"),
        ("アカウント登録は必要ですか？", "アプリの読書・音読にアカウント登録は不要です。サポートの問い合わせをGitHubで送信する場合のみ、GitHubへのログインが必要です。" if IS_GITHUB else "アプリの読書・音読にアカウント登録は不要です。問い合わせフォームは送信画面の案内に従ってご利用ください。"),
    ]
    faq_html = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)
    content = f'''<section class="contact-card" id="contact"><p class="eyebrow">WE'RE HERE TO HELP</p><h2>お問い合わせ</h2><p>不具合・使い方のご相談と、ご意見・ご要望は、こちらからお送りください。</p><div class="actions"><a class="button blue" href="{e(CONTACT['url'])}">お問い合わせフォーム {icon('arrow')}</a><a class="button secondary" href="{e(feedback)}">ご意見・ご要望</a></div><p class="notice">{e(contact_notice())}</p><p><small>運営・対応：<a href="https://github.com/{e(CONFIG['owner'])}">{e(CONFIG['owner'])}</a> ／ <a href="../privacy/">情報の取り扱い</a></small></p></section>
<section id="start"><h2>最初の読み方</h2><ol class="steps-list"><li>本棚で作品を選び、スワイプや左右端のタップで読み進めます。</li><li>意味を確かめたい英文を一文タップすると、その文の日本語訳が開きます。</li><li>音読は下部の「音読する」から。前の文・次の文への移動や、0.5〜2倍速に対応します。</li><li>右上の「Aa」で文字や背景、ヘッドホンのボタンで音声と速度を変えられます。</li></ol><div class="support-topics"><a href="#faq">{icon('help')}よくある質問</a><a href="../privacy/">{icon('book')}データの取り扱い</a><a href="../sources/">{icon('book')}原文と出典</a></div></section>
<section class="faq" id="faq"><h2>よくある質問</h2>{faq_html}</section>
<section id="report"><h2>不具合のご報告に添えてほしいこと</h2><p>わかる範囲で、次の内容を添えていただくと確認がスムーズです。</p><ul><li>どの画面で、何をしたときに、何が起きたか</li><li>iPhoneの機種・iOSとアプリのバージョン</li><li>本文・訳の場合は、作品名と該当する短い文</li><li>音読の場合は、Apple音声／高品質音声と再生速度</li></ul><p>スクリーンショットは、個人情報が写っていないことを確認して添付してください。</p><a class="button secondary" href="{e(CONTACT['url'])}">フォームを開く {icon('arrow')}</a></section>
<section id="environment"><h2>対応環境</h2><p>iOS 17以降のiPhoneに対応しています。本文13作品と対訳は同梱され、ログインは不要です。広告・アプリ内課金・アプリ独自のクラウド同期はありません。</p><p class="updated">ページ更新：{e(CONFIG['updated'])}</p></section>'''
    return document("support", "サポート", "使い方や、お困りのときの確認方法をご案内します。解決しない場合はお問い合わせフォームからご連絡ください。", [("contact","お問い合わせ"),("start","最初の読み方"),("faq","よくある質問"),("report","不具合のご報告"),("environment","対応環境")], content)

def privacy():
    contact_paragraph = "お問い合わせにはGitHub Issuesを利用します。送信者のGitHubアカウント名、投稿本文、添付画像、やり取りはGitHub上に公開されます。開発者はご相談への回答、不具合の調査、改善のためにこれらの情報を確認します。公開の場ですので、氏名・メールアドレス・電話番号・パスワードなどを記入しないでください。投稿の訂正・削除に関するご相談は、該当Issueのコメントからお知らせください。" if IS_GITHUB else "お問い合わせにはGoogleフォームを利用します。送信内容はご相談への回答、不具合の調査、改善のために確認します。個人情報は回答に必要な範囲にとどめ、送信画面の案内をご確認ください。情報の訂正・削除に関するご相談もお問い合わせフォームから受け付けます。"
    provider_link = '<a href="https://docs.github.com/ja/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシーに関する声明</a>' if IS_GITHUB else '<a href="https://policies.google.com/privacy?hl=ja">Googleのプライバシーポリシー</a>'
    content = f'''<div class="policy-summary"><p><strong>読むためのデータは、端末の中に。</strong><br>本アプリの開発者は、読んだ作品・本文・読書位置・音読内容を収集・送信する機能を設けていません。問い合わせは外部サービスで別に受け付けます。</p></div>
<section id="scope"><h2>1. 適用範囲と運営者</h2><p>このポリシーは「{e(NAME)}」（以下「本アプリ」）と、その紹介・サポートサイトに適用します。運営者は <a href="https://github.com/{e(CONFIG['owner'])}">{e(CONFIG['owner'])}</a> です。お問い合わせは<a href="../support/#contact">サポート窓口</a>から受け付けます。</p></section>
<section id="device"><h2>2. アプリ内で保存する情報</h2><p>読書・音読を再開するための位置、読了状態、表示テーマ・文字サイズ・行間、対訳の表示、音声と再生速度の設定を端末内に保存します。任意で取得した高品質音声の音声合成モデルも端末内に保存し、合成音声の一時ファイルは再生処理に使用します。</p><p>本アプリ独自のアカウント登録、広告配信、行動解析、他アプリをまたぐトラッキング、クラウド同期の機能は設けていません。端末内の読書記録や設定を開発者のサーバーへ送信しません。</p></section>
<section id="network"><h2>3. 音声とネットワーク通信</h2><p>Apple音声はiOSの読み上げ機能を利用し、高品質音声は取得済みのSupertonic 3モデルを使って端末内で合成します。本アプリが本文を外部の翻訳API・音声合成APIへ送信する構成ではありません。</p><p>高品質音声のデータをダウンロードするときはGitHub Releasesとその配信先へ接続します。この通信では配信事業者がIPアドレスなど通信に必要な情報を処理する場合があります。作品の閲覧履歴・読書位置・音読内容はダウンロード先へ送信しません。</p><p>出典・参考文献・サポートなどの外部リンクを選ぶと外部サイトを開きます。リンク先にはそのサービスの規約とプライバシーポリシーが適用されます。</p></section>
<section id="contact-data"><h2>4. お問い合わせの情報</h2><p>{contact_paragraph}</p><p>問い合わせサービスによる情報の取り扱いは、{provider_link}もご確認ください。</p></section>
<section id="website"><h2>5. このウェブサイト</h2><p>本サイトはGitHub Pagesで配信しています。本サイト独自の広告、アクセス解析、追跡用Cookieは使用しません。サイト配信に伴うアクセス情報はGitHubが取り扱う場合があります。詳しくは<a href="https://docs.github.com/ja/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシーに関する声明</a>をご確認ください。</p></section>
<section id="delete"><h2>6. 端末内データの削除・バックアップ</h2><p>iPhoneの設定から本アプリを削除すると、端末内の読書記録・設定・取得した音声合成モデルも削除されます。「Appを取り除く」はデータを保持するiOSの機能のため、削除する場合は「Appを削除」を選んでください。</p><p>iOSが提供するバックアップ・端末移行・診断などはAppleの設定とポリシーに従います。本アプリ独自のクラウド同期とは別の仕組みです。音声モデルの保存場所はバックアップ対象外としています。</p></section>
<section id="change"><h2>7. ポリシーの変更・連絡先</h2><p>機能や情報の取り扱いを変更した場合は、このページを更新します。本ポリシーについてのご相談も<a href="../support/#contact">お問い合わせフォーム</a>からお送りください。</p><p class="updated">制定・最終更新：{e(CONFIG['updated'])}</p></section>'''
    return document("privacy", "プライバシーポリシー", "アプリの読書データ、音声、外部サービス、お問い合わせに関する情報の取り扱いを説明します。", [("scope","適用範囲"),("device","端末内の情報"),("network","音声と通信"),("contact-data","お問い合わせ"),("website","ウェブサイト"),("delete","削除とバックアップ"),("change","変更・連絡先")], content)

def sources():
    books = "".join(f'<li><div>{e(b["title"])} <span>／ {e(b["author"])}</span></div><a href="{e(b["cardURL"])}">青空文庫の図書カード ↗</a></li>' for b in BOOKS)
    content = f'''<section id="books"><h2>原作と青空文庫</h2><p>本アプリの原作は、青空文庫の公開ファイルを使用しています。作品ごとの底本・入力者・校正者などの出典情報は、アプリの作品情報画面に掲載しています。本アプリは青空文庫の公式アプリではありません。</p><ul class="source-list">{books}</ul><p><a href="https://www.aozora.gr.jp/guide/kijyunn.html">青空文庫収録ファイルの取り扱い規準</a></p></section>
<section id="translation"><h2>名作を、やさしい英語で語り直す</h2><p>原作の一文をそのまま英語へ置き換えるのではなく、伝える内容を整理し、複数の短い英文で説明し直しています。複雑な心理描写も、考えの順序を追える短い文へ。難しい言葉は身近な表現や短い説明に置き換え、場面・会話・結末を残したまま、物語全体を読みやすくつくり直しています。</p><p>たとえば『注文の多い料理店』の冒頭は、原作の一文を7つの短い英文にしています。<a href="../#retelling">実際の原文と英文の例を見る</a>。</p><p>一文の日本語訳は、こうして書き直した英文に合わせて別に制作しています。青空文庫の原文とは区別して表示し、原文も別に参照できます。</p><p>中学英語は制作上の目安です。物語に必要な固有名詞・文化的な語も含まれます。特定の語彙範囲だけで構成した教材や、公式の語学レベル認定を受けた教材としての表示ではありません。</p></section>
<section id="learning"><h2>学習方針と参考文献</h2><p>理解できる文章を、興味に合わせて多く読む体験を目指しています。アプリ内では、理解可能なインプット仮説と多読の実践・研究結果を分けて紹介しています。読む経験を土台に、会話や作文も目的に応じて組み合わせる考え方です。</p><p>これらは制作上の参考文献で、本アプリ自体の学習効果を測定したものではありません。</p><ul><li><a href="https://www.sdkrashen.com/content/books/principles_and_practice.pdf">Krashen（1982）Principles and Practice in Second Language Acquisition</a></li><li><a href="https://nflrc.hawaii.edu/rfl/item/61">Day &amp; Bamford（2002）Top Ten Principles for Teaching Extensive Reading</a></li><li><a href="https://doi.org/10.1002/tesq.157">Nakanishi（2015）A Meta-Analysis of Extensive Reading Research</a></li><li><a href="https://doi.org/10.1007/s10648-025-10068-6">Sangers ほか（2025）Learning a Language Through Reading</a></li></ul></section>
<section id="software"><h2>音声・ソフトウェア</h2><p>Apple音声はiOSの標準機能を使用します。任意で使用するSupertonic Swift HelperとONNX RuntimeはMITライセンス、Supertonic 3モデルはOpenRAIL-Mライセンスです。詳細とライセンス文はアプリの「利用しているソフトウェア」から確認できます。</p></section>
<section id="site"><h2>このサイトについて</h2><p>アプリの紹介、使い方のご案内、お問い合わせ窓口を提供するためのサイトです。掲載する読書画面は実際のアプリの画面です。運営・サポート：<a href="https://github.com/{e(CONFIG['owner'])}">{e(CONFIG['owner'])}</a>。</p><p><a href="../support/">サポート</a> ／ <a href="../privacy/">プライバシーポリシー</a></p></section>'''
    return document("sources", "出典・このサイトについて", "収録作品の原文、英訳と日本語訳、学習方針、利用している音声について。", [("books","原作・青空文庫"),("translation","英訳について"),("learning","学習方針"),("software","音声・ソフトウェア"),("site","このサイト")], content)

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "src/assets", OUT / "assets", dirs_exist_ok=True)
    for slug, render in [("", home), ("support", support), ("privacy", privacy), ("sources", sources)]:
        folder = OUT / slug
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(render(), encoding="utf-8")
    (OUT / "404.html").write_text(page("", "ページが見つかりません", "お探しのページが見つかりません。", '<main id="main" class="wrap not-found"><p class="eyebrow">404</p><h1>ページが見つかりません。</h1><p>リンクが変わったか、ページが存在しない可能性があります。</p><a class="button" href="' + e(BASE) + '/">ホームへ戻る</a></main>', absolute_assets=True), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{BASE}/{slug}</loc></url>" for slug in ["", "support/", "privacy/", "sources/"])
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>')
    print(f"Built 4 pages and a 404 page in {OUT}")

if __name__ == "__main__":
    main()
