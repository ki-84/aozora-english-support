# やさしい英語で読む名作 — 紹介・サポートサイト

iPhoneアプリのPR、使い方・問い合わせ、プライバシーポリシー、出典を公開する静的サイトです。メールアドレスは掲載せず、GitHub Issue Formsを窓口にしています。

| App Store Connectの項目 | 公開URL |
| --- | --- |
| マーケティングURL | https://ki-84.github.io/aozora-english-support/ |
| サポートURL | https://ki-84.github.io/aozora-english-support/support/ |
| プライバシーポリシーURL | https://ki-84.github.io/aozora-english-support/privacy/ |

出典・学習方針：https://ki-84.github.io/aozora-english-support/sources/

## 編集・確認

Python 3.9以降の標準ライブラリだけで生成します。npmや外部パッケージのインストールは不要です。

```sh
python3 scripts/build.py
python3 scripts/check_site.py
python3 -m http.server 8764 --bind 127.0.0.1 --directory docs
```

http://127.0.0.1:8764/ を開きます。`src/`や設定を変更したら再生成し、生成物の`docs/`も一緒にコミットしてください。CIは内部リンク、目次・対訳ボタンの参照先、画像、メタ情報、10作品、サイトマップ、生成物の更新を確認します。

| 場所 | 内容 |
| --- | --- |
| `site.json` | アプリ名、公開URL、問い合わせ、App Storeリンク |
| `scripts/build.py` | 全ページの本文とHTML生成 |
| `src/books.json` | 10作品の著者・タイトル・原作リンク |
| `src/retelling-sample.json` | 語り直しの実例。アプリ収録の原文1文と英文7文 |
| `src/assets/` | 共通CSS・JS、アイコン、実際のアプリ画面 |
| `.github/ISSUE_TEMPLATE/` | 問い合わせ・要望フォーム |
| `docs/` | GitHub Pagesへ公開する生成物 |

GitHub Pagesの公開元は **main /docs** です。独自ドメインは不要で、公開後はmainの更新に追従します。本サイト独自の分析、広告、外部フォント、追跡Cookieはありません。JavaScriptは紹介ページの対訳デモのみで使用します。

## 問い合わせ窓口

現在はGitHub Issue Formsです。送信にはGitHubへのログインが必要で、投稿・添付は公開されます。サイトとフォームの冒頭にこの条件を明記しています。開発者はIssue上で回答してください。問い合わせを受け付けるため、リポジトリのIssuesを有効にしておきます。

### Googleフォームへ切り替える場合

Googleフォームを作成し、実際の公開URLを取得してから`site.json`を変更します。フォームは「相談内容」「端末・バージョン（任意）」程度の最小限の項目にしてください。

```json
"contact": {
  "provider": "google",
  "url": "実際のGoogleフォームのHTTPS公開URL",
  "feedback_url": "実際のGoogleフォームのHTTPS公開URL"
}
```

一般ユーザーが送信できる公開範囲に設定し、メールアドレスの自動収集、組織内限定、ファイル添付によるログイン要求などの設定を確認してください。記名や返信先の収集を追加する場合は、取得項目・利用目的・回答方法をフォームとプライバシーポリシーにも明記します。返信先を収集しないフォームは個別回答できないため、その場合は受付・回答方法の案内も変更してください。

`scripts/build.py`の`contact_notice()`、`support()`、`privacy()`を実際のフォーム設定に合わせて確認し、再生成・検証・PUSHします。Googleフォームは未作成なので、存在しないURLや埋め込み枠は公開していません。

## App Storeへの公開時

App Storeの製品URLが確定したら`site.json`の`app_store_url`へ設定し、再生成してください。紹介ページにApp Storeへのボタンが表示されます。それまでは「アプリの公開準備中」と表示します。

申請時の確認事項は[APP_STORE.md](APP_STORE.md)を参照してください。公開URLの用意は審査の一部で、審査通過を保証するものではありません。
