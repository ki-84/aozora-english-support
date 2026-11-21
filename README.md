# やさしい英語で読む名作 サポート

iPhoneアプリのサポートとプライバシーポリシーを公開する静的サイトです。

- [アプリのご案内](https://ki-84.github.io/aozora-english-support/)
- [サポート・お問い合わせ](https://ki-84.github.io/aozora-english-support/support/)
- [プライバシーポリシー](https://ki-84.github.io/aozora-english-support/privacy/)
- [出典](https://ki-84.github.io/aozora-english-support/sources/)

お問い合わせはGitHub Issue Formsで受け付けます。投稿にはログインが必要で、内容と添付ファイルは公開されます。

## 更新と検証

```sh
python3 scripts/build.py
python3 scripts/check_site.py
```

ページの本文と構成は `scripts/build.py`、アプリと問い合わせのURLは `site.json` にあります。生成した `docs/` も一緒にコミットしてください。GitHub Pagesは `main` ブランチの `/docs` を公開します。App Store ConnectのURL設定は [APP_STORE.md](APP_STORE.md) を参照できます。
