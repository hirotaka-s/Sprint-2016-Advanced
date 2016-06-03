## STEP1. デプロイ情報
以下の情報を入力してください。
- チャットボットをデプロイしたサーバーのURL
    - [kofearistokrat.com:10010](http://kofearistokrat.com:10010/) 
- デプロイに使ったサービス: AWS / DigitalOcean / Sakura / Heroku / Cloudn / etc.
    - Sakura VPS

## STEP2. 必須機能の実装
必須機能を実装する上で、創意工夫した点があれば記述してください。

必須機能の実装後も追加でコマンドを実装することと，botのコマンドはコマンドを文字列で指定して呼び出すことを考慮して，botのコマンド処理についてはBotCommandクラスを作成してそこに`bot `の後に記述されるコマンド名と同名のメソッドのみを定義し，getattr関数を用いてディスパッチする形で実装しました．
以降は，コマンドごとに必要に応じてクラスを追加実装して，BotCommandクラスにそのインスタンスを持たせて，利用するコマンド名と同名のメソッドをBotCommandに実装するのみで新たなコマンドが実装できます．
getattr関数でオブジェクトからの属性を取得する際に，`__init__`メソッドやプライベートなフィールドにアクセスされるのは防ぐ必要があるため，コマンドの文字列の先頭がアンダースコアで始まるかどうかをチェックしています．


## STEP3. 独自コマンドの実装
追加したコマンドの内容について説明をしてください。

次のコマンドを追加しました．
- `bot translate [translate_to] [text]` : 翻訳コマンド

翻訳コマンドは，入力したテキストを目的の言語へ翻訳が可能なコマンドです．
例えば，`bot translate ja Thank you`を送ると，
```
bot translate ja Thank you
bot: ありがとう
```

というように英語(en)を日本語(ja)に翻訳してくれます．
先ほどのお返しに「どういたしまして」を伝えてみます．
```
bot translate en どういたしまして．
bot: You are welcome.
```

日本語や英語に限らず，APIで対応可能な言語はすべて翻訳可能です．
```
bot translate zh Thank you
bot: 谢谢
```

翻訳頼りですが，様々な国の人とチャットでやり取りできるかもしれません．

## 今回の開発に使用した技術
今回のチャットボット開発に利用した言語、ライブラリ、フレームワーク、API等を記載してください。

### 利用した言語
- Python3

### 利用したライブラリ，フレームワーク
- bottle: Webフレームワーク
- websockets: WebSocketライブラリ
- tinydb:　Key-Value型の軽量ドキュメントデータベース
- requests: HTTPライブラリ

### 利用したAPI
- Microsoft Translator API: 翻訳コマンド`bot translate`用

## その他独自実装した内容の説明
自分自身がオリジナルで実装した内容について説明してください。

他に独自実装したコマンドを以下に示します．
- `bot clap` : チャットボットが拍手してくれるだけのコマンド
- `bot thanks`: チャットボットを労うコマンド
- `bot alias [command_name] [alias_name]` : `command_name`を`alias_name`としてaliasを登録
    - aliasを設定可能なコマンドは`ping`,`todo`,`translate`,`clap`,`thanks`,`alias`,`unalias`,`aliases`,`wordchecker`
- `bot unalias [alias_name]` : `alias_name`のaliasを削除
- `bot aliases` : 全ユーザによって登録されたaliasの一覧
- `bot wordchecker [command] [param]`: 設定したワードを検閲により削除するコマンド
    - `[command]`として`add`, `delete`, `wordcheck`, `list`, `is_enable`, `enable`, `disable`を実装しています

### alias, unalias, aliasesコマンドについて
`bot `の直後に続くコマンドのaliasを`alias`コマンドで登録できます．

既に利用可能なコマンド名や，既にaliasとして登録されているalias名はaliasとして`[alias_name]`として使用できません．
また，aliasのaliasは設定できないようにしています．

再度`alias`,`unalias`,`aliases`コマンドの書式を示します．
- `bot alias [command_name] [alias_name]`
- `bot unalias [alias_name]`
- `bot aliases`


実行例:
```
input # bot alias thanks t
output# bot alias: Set alias thanks -> t
input # bot t
output# bot: You are welcome :)
input # bot alias clap c
output# bot alias: Set alias clap -> c
input # bot aliases
output# [thanks -> t, clap -> c]
input # bot delete c
output# bot unalias: Alias clap -> c is deleted
input # bot aliases
output# [thanks -> t]
```

### wordcheckerコマンドについて
辞書登録された任意のワードを検閲して削除する機能です．
この機能がenableな場合には，クライアントが送信したメッセージをチャットサーバが配信する際に自動的に検閲が入り，辞書に登録された語が削除されます．
ただし，botからのメッセージには`wordchecker wordcheck`コマンドの結果以外で検閲は行われません．

各コマンドの書式を次に示します．
- `bot wordchecker add [word]`: 検閲する語`[word]`を辞書に追加
- `bot wordchecker delete [word]`: 検閲から外したい語`[word]`を辞書から削除
- `bot wordchecker wordcheck [text]`: `[text]`を検閲して辞書に登録された語を削除
- `bot wordchecker list`: 辞書に登録された語の一覧
- `bot wordchecker is_enable`: 検閲が有効かどうか
- `bot wordchecker enable`: 検閲を有効化
- `bot wordchecker disable`: 検閲を無効化

実行例:
```
input # bot wordchecker add テスト
output# bot wordchecker: Add word: テスト
input # bot wordchecker is_enable
output# bot wordchecker: Enabled
input # 今日は期末テスト なので朝から憂鬱です．
output# 今日は期末 [検閲により削除] なので朝から憂鬱です．
input # bot wordchecker disable
output# bot wordchecker: Disabled
input # 今日は期末テストなので朝から憂鬱です．
output# 今日は期末テストなので朝から憂鬱です．
input # bot wordchecker add 憂鬱
output# bot wordchecker: Add word: 憂鬱
input # bot wordchecker list
output# [ テスト, 憂鬱 ]
input # bot wordchecker enable
output# bot wordchecker: Enabled
input # 今日は期末テストなので朝から憂鬱です．
output# 今日は期末 [検閲により削除] なので朝から [検閲により削除] です．
input # bot wordchecker delete テスト
output# bot wordchecker: word deleted
input # bot wordchecker wordcheck 今日は期末テストなので朝から憂鬱です．
output# 今日は期末テストなので朝から [検閲により削除] です．
```

## その他創意工夫点、アピールポイントなど
レビューワーをうならせる創意工夫やアピールポイントがあればこちらに記載してください。

botのメインのコマンドに対するサブコマンドの呼び出しも，コマンドの呼び出しと同様にgetattr関数で呼び出すように実装しました．
botのコマンドのほとんどはそれぞれに対応するクラスを実装しているので，コマンドに新たなサブコマンドを実装する際は，そのクラスにサブコマンド名と同名のメソッドを追加するだけで実装が完了する場合がほとんどです．

実装としてはいくつか重複する処理が記述されていることと，エラー処理についても独自例外を作成した方がコードの見通しが良くなると思いますので，リファクタリング，実装の余地が多々残っていることが反省点です．

`wordchecker`コマンドは任意に検閲して削除するワードを設定できますが，誰でも追加/削除できるので禍根の残るようなワード(`vim`や`emacs`等々)の設定はお控えください．
また，botからのメッセージは検閲対象から外れているので，`translate`コマンドを使用する際には特に注意が必要となります．
友人をなくすような使い方が出来てしまいますが，それさえ注意すれば楽しくチャットできるのではないでしょうか．
