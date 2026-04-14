# Angular 環境構築手順

---

## ⓪ Nodejs アンインストール

Voltaを使う為、既存のNodejsは削除する。

---

## ① Volta インストール

VoltaはNode.jsをプロジェクト毎に切り替えて利用可能とするツール。

以下から、VOLTAのインストールを行う。

- `\\172.25.11.190\share\開発者向けソフト関連\Node.js`
- `volta-2.0.1-windows-x86_64.msi`

ダウンロード後インストール手順は、全て次へで問題ない。

![Voltaインストール][image6.png]

---

## ② Node.js インストール

### バージョン要件

コマンドプロンプトから以下コマンドによりNode.jsをインストール。

```
volta install node@バージョン番号
volta install node@24.11.0
```

![Node.jsインストール][image7.png]

#### プロキシエラーになる場合

上記コマンド実行前に下記のコマンドを実行しプロキシ設定する。

実行時にFetchErrorが発生した場合、以下コマンドで環境変数にプロキシの設定が入っているか確認し、入っていない場合環境変数を追加後、再実行する。

```
set | find /i "proxy"
HTTPS_PROXY=http://172.31.1.36:8080
HTTP_PROXY=http://172.31.1.36:8080
no_proxy=localhost,127.0.0.1,::1, 10.0.0.0/8
```

- ※環境変数追加後はコマンドプロンプトの再起動を行うこと
- ※Node.jsのバージョンについては後日変更となる可能性があります

> **!!! 注意 !!!**
>
> Windowsの環境変数にプロキシ設定を行うと、tortoise git がプロキシを参照するようになります。
>
> tortoise git にはプロキシ例外を指定することで回避可能です。
>
> エクスプローラーで右クリック → tortoiseGit → 設定 → Git → このユーザの設定を編集
>
> 以下を追記：
> ```
> [http "http://172.25.21.208:9980/"]
>     proxy =
> ```

---

## ③ VSCode がインストールされていない場合はインストール

常に最新版の使用を推奨。

※Copilotを利用する場合、認証時にVSCodeのバージョンを下げる必要がある為、可能であれば先にGitHubのユーザ作成を推奨。

- 以下から最新版ダウンロード
  - [Visual Studio Code - Code Editing. Redefined](https://code.visualstudio.com/)
- インストール時は特に注意点なし
- デフォルトは英語の為、日本語化したい場合は **"Japanese Language Pack"** の拡張機能を入れる
- インストール手順は、全て次へで問題ない

既にインストール済の場合以下手順により更新の確認を行う。

![VSCode更新確認][image3.png]

---

## ④ VSCode に拡張機能インストール

### Angular Language Service

![Angular Language Service][image1.png]

### Eslint

![Eslint][image2.png]

### Dprint Code Formatter

![Dprint Code Formatter][image4.png]

※情報収集の許可・拒否の選択についてはどちらでも可。

---

## ⑤ Angular CLIをインストール

コマンドプロンプトを開き、下記コマンドでインストール。

```
npm install -g @angular/cli
```

上記の設定を行った場合、gitへのアクセスエラーが発生する場合がある。  
その場合、gitconfigに以下を設定する：

```
[http]
    proxy = "http://172.31.1.36:8080"
    sslVerify = false
[http "http://172.25.21.208:9980/"]
```

※設定後、コマンド再実施前にVSCodeを再起動する。

### サードパーティ製ミラーの確認

※ サードパーティ製ミラーを使用すると npm のダウンロードが失敗する可能性があるため、コマンド実行前にダウンロード元が公式リポジトリであることを確認する。

VS CODEのターミナルに下記の命令を入力する。

> ※もしターミナルウィンドウが表示されていない場合、ナビゲーションバーの「ターミナル」→「新しいターミナル」をクリックして、ターミナルウィンドウを開ける。

![VSCodeターミナル][image12.png]

実行コマンド：

```
npm config get registry
```

![npm config get registry][image13.png]

もし、戻る情報は `https://registry.npmjs.org/` の場合、npm のダウンロード元が公式リポジトリである。

![公式リポジトリ確認][image14.png]

上記以外の場合、下記のコマンドにより、ダウンロード元を公式リポジトリへ設定する：

```
npm config set registry https://registry.npmjs.org/
```

![npm config set registry][image15.png]

---

## ⑥ GIT クローン

対象プロジェクトのクローンを実施。

---

## ⑦ VSCodeでGITフォルダを開く

`ONEsLOGI-WMS\wms-ui`

gitフォルダを開いた際に以下が出てくる場合は親フォルダ込みで信頼済とする。

![フォルダ信頼ダイアログ][image8.png]

---

## ⑧ VSCode でターミナルを開いてパッケージインストール

下記コマンドを実行：

```
npm install
```

![npm install][image9.png]

---

## ⑨ バックエンドのコンテキストを確認

プロジェクトに、下記のファイルをあける：

`\projects\wms\src\assets\settings\base\app-config.json`

![app-config.json][image16.png]

---

## ⑩ 画面の起動確認

起動確認については **"VSCode開発環境構築手順書.xlsx"** により、Tomcatサーバの起動を確認した上で実施を行う。

左側のバーで「実行とデバッグ」をクリックし、プルダウンから「ng serve」を選択した状態で、再生ボタンを押して起動。

![実行とデバッグ][image10.png]

下記が表示された後、ブラウザが自動で起動する。

![ビルド完了][image5.png]

自動的にブラウザを開けて、メインメニュー画面が表示する。

![メインメニュー画面][image17.png]