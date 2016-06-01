## STEP1. デプロイ情報
以下の情報を入力してください。
- チャットボットをデプロイしたサーバーのURL
    - [kofearistokrat.com:10010](http://kofearistokrat.com:10010/) 
- デプロイに使ったサービス: AWS / DigitalOcean / Sakura / Heroku / Cloudn / etc.
    - Sakura VPS

## STEP2. 必須機能の実装
必須機能を実装する上で、創意工夫した点があれば記述してください。

## STEP3. 独自コマンドの実装
追加したコマンドの内容について説明をしてください。

次のコマンドを追加しました．
- `bot translate [translate_to] [text]` : 翻訳コマンド

翻訳コマンドは，`bot translate ja Thanks`というように目的の言語へ翻訳が可能なコマンドです．

## 今回の開発に使用した技術
今回のチャットボット開発に利用した言語、ライブラリ、フレームワーク、API等を記載してください。

### 利用した言語
- Python3

### 利用したライブラリ
- bottle
- websockets
- tinydb
- requests

### 利用したAPI
- Microsoft Translator API: 翻訳コマンド`bot translate`用

## その他独自実装した内容の説明
自分自身がオリジナルで実装した内容について説明してください。

- `bot clap` : チャットボットが拍手してくれるだけのコマンド
- `bot thanks`: チャットボットを労うコマンド
- `bot alias [command_name] [alias_name]` : `command_name`を`alias_name`としてaliasを登録
- `bot unalias [alias_name]` : `alias_name`のaliasを削除
- `bot aliases` : 全ユーザによって登録されたaliasの一覧

## その他創意工夫点、アピールポイントなど
レビューワーをうならせる創意工夫やアピールポイントがあればこちらに記載してください。
