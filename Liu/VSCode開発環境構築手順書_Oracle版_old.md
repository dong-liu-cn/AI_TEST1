# VSCode開発環境構築手順書（Oracle版）

## 目次

- [資料作成時のバージョン情報](#資料作成時のバージョン情報)
- [前提条件](#前提条件)
- [既存プロジェクトVSCode対応](#既存プロジェクトVSCode対応)
- [起動後～拡張機能インストール](#起動後～拡張機能インストール)
- [DB定義にかんするTSVファイルの出力](#DB定義にかんするTSVファイルの出力)
- [テーブル定義の生成](#テーブル定義の生成)
- [DB構築](#DB構築)
- [dbfluteのjarファイルの生成](#dbfluteのjarファイルの生成)
- [プロジェクト(フォルダ)を開く](#プロジェクト(フォルダ)を開く)
- [DB接続情報設定](#DB接続情報設定)
- [環境構築](#環境構築)
- [Tomcat調整](#Tomcat調整)
- [デバッグ](#デバッグ)
- [成功確認](#成功確認)
- [環境削除](#環境削除)
- [VSCodeアンインストール](#VSCodeアンインストール)
- [トラブルＱＡ](#トラブルＱＡ)

---

## 資料作成時のバージョン情報

- 資料作成時の主要（本体・拡張機能）なバージョンを記載しておく。
- ※参考情報として掲載しているだけであり、原則最新版の利用を推奨
- VS Code　：　1.105.1
- Japanese Language Pack for Visual Studio Code　：　v1.105.2025101509
- Extension Pack for Java　：　v0.30.3

---

## 前提条件

- 開発に必要となる以下ソフトはディスク上に展開済である事を前提としている。
- ※ソフトとの紐付けは別途行う為、OSにインストールされている（環境変数に登録されている）必要はない
    - VSCode
    - Java
    - Tomcat
- VS Codeから利用可能なEclipseのJavaプロジェクトを前提としている。
- VS Codeから利用可能にする方法は「既存プロジェクトVSCode対応」シートを参照し対応する事。

---

## 既存プロジェクトVSCode対応

- EclipseとVS Code、両方で動作する環境を作成する場合
- 【.classpath】に設定される内容を調整する必要があります。
- ※既に実施済であれば、本作業はスキップしてください
- 具体的には以下の手順で【.classpath】を調整します。
#### ①【プロジェクト＞プロパティ】を開き【Javaのビルド・パス＞ライブラリ】の定義を全て除去

#### ②【ライブラリの追加】を押下、【JREシステム・ライブラリ】を選択し【次へ】を押下

#### ③【実行環境】を選択し「該当バージョンのJava」を選択し【完了】を押下

#### ④【JARの追加】を押下、「該当プロジェクトフォルダ」を選択し「libフォルダ（例：WebContents\WEB-INF\lib）」内のJARファイルを全て選択し【OK】を押下

- またVS Codeでプロジェクトを開くと【.project】が更新されますが、Eclipse側には影響しない為、そのまま利用してください。

---

## 起動後～拡張機能インストール

日本語インストール
![起動後_拡張機能インストール_1.png][起動後_拡張機能インストール_1.png]

VS Code再起動
![起動後_拡張機能インストール_2.png][起動後_拡張機能インストール_2.png]

Java関連インストール
![起動後_拡張機能インストール_3.png][起動後_拡張機能インストール_3.png]

---

## DB定義にかんするTSVファイルの出力

DB定義にかんするTSVファイルの出力

### １．DataManageToolの設定ファイルをOracle用に設定変更

#### ①　「最新ソースの格納フォルダ」\dbflute\database\DataManageTool\conf 内の設定ファイルを、以下の内容に従い変更

    - ・[DataManageTool.xlsx]を変更
    - 前)　DataOutputFolder = ..\..\dbflute_dfclient_mysql\playsql\data\common\tsv\UTF-8
    - 後)　DataOutputFolder = ..\..\dbflute_dfclient_oracle\playsql\data\common\tsv\UTF-8
![DB定義にかんするTSVファイルの出力_3.png][DB定義にかんするTSVファイルの出力_3.png]

    - ・[DBFluteDfpropOutput.xlsx]を変更
    - 前)　DataOutputFolder = ..\..\dbflute_dfclient_mysql\dfprop
    - 後)　DataOutputFolder = ..\..\dbflute_dfclient_oracle\dfprop
![DB定義にかんするTSVファイルの出力_4.png][DB定義にかんするTSVファイルの出力_4.png]

### ２．データ管理ツールのバッチを実行し、DB定義にかんするTSVファイル出力する
#### ①　バッチの実行

    - 下記のbatを実行
    - 「最新ソースの格納フォルダ」\dbflute\database\DataManageTool\bat\DataManageTool_Exec_00All.bat
![DB定義にかんするTSVファイルの出力_1.png][DB定義にかんするTSVファイルの出力_1.png]
![DB定義にかんするTSVファイルの出力_2.png][DB定義にかんするTSVファイルの出力_2.png]

#### ②　TSVファイルをただしく生成するか確認

    - 「最新ソースの格納フォルダ\dbflute_dfclient_oracle\playsql\data\common\tsv\UTF-8」ファイルに、TSVファイルを生成するか、更新日時が最新の日時するか確認

![DB定義にかんするTSVファイルの出力_5.png][DB定義にかんするTSVファイルの出力_5.png]

---

## テーブル定義の生成

テーブル定義の生成

### １．A5:SQL Mk2のインストール

    - https://a5m2.mmatsubara.com/　にてダウンロード
![テーブル定義の生成_1.png][テーブル定義の生成_1.png]
![テーブル定義の生成_2.png][テーブル定義の生成_2.png]

### ２．DB定義を生成する

#### ①　下記のファイルをダブルクリックし、A5:SQL Mk2でER図を開ける

    - 「最新ソースの格納フォルダ」\dbflute\database\ER図.a5er
![テーブル定義の生成_3.png][テーブル定義の生成_3.png]

#### ②　ドメインを更新する

    - ナビゲーションバーの「ER図」→「ドメインを編集する」をクリックして、ドメイン編集ウインドウをあけて、各データ型の内容を変更

    - 前)
![テーブル定義の生成_4.png][テーブル定義の生成_4.png]
    - 後)
![テーブル定義の生成_5.png][テーブル定義の生成_5.png]
    - ドメイン定義
![テーブル定義の生成_6.png][テーブル定義の生成_6.png]
- ➂　DDLを生成する
    - ナビゲーションバーの「ER図」→「DDLを作成する」を選択、「RDBMS種類」を「Oracle」に変更し「DDL作成」をクリック
#### ④　出力されたDDL文を「最新ソースの格納フォルダ\dbflute\dbflute_dfclient_oracle\playsql\replace-schema-01-table.sql.txt」の内容を空にして反映


![テーブル定義の生成_7.png][テーブル定義の生成_7.png]


![テーブル定義の生成_8.png][テーブル定義の生成_8.png]


---

## DB構築

DB構築

### １．前提：

- Orcale　DBとschemaを作成済み
    - ※　Oracle サーバーのインストールおよびスキーマの作成については、別途記述する予定
    - Orcaleバージョン：　19C
    - 文字コード：　UTF-8
### ２．　構築手順：

#### ①dbfulteにDB接続情報を設定

    - ・修正ファイル：
    - 「最新ソースの格納フォルダ」\dbflute\dbflute_dfclient_oracle\dfprop\databaseInfoMap.dfprop
![DB構築_1.png][DB構築_1.png]

#### ②DBを作成する

    - 下記のbatを実行
    - 「最新ソースの格納フォルダ\dbflute\dbflute_dfclient_oracle\manage.bat」
    - “1”を入力し、【Enter】
    - “y”を入力し、【Enter】
    - BUILD　SUCCESSFULで終了したら、【Enter】
    - （BUILD　FAILDの場合、エラーメッセージを確認した上で再実行）




![DB構築_2.png][DB構築_2.png]


![DB構築_3.png][DB構築_3.png]


![DB構築_4.png][DB構築_4.png]


![DB構築_5.png][DB構築_5.png]


---

## dbfluteのjarファイルの生成

dbfluteのjarファイルの生成

### １． Gradleのインストール

#### ①　JAVA_HOMEの設定

    - ・　「最新ソースの格納フォルダ\dbflute\Gradle.env」を開ける
    - ・　JAVA HOMEを設定する
![dbfluteのjarファイルの生成_2.png][dbfluteのjarファイルの生成_2.png]
![dbfluteのjarファイルの生成_1.png][dbfluteのjarファイルの生成_1.png]

#### ②　GradleのZIPファイルをダウンロード

    - ZIPは以下URLにアクセスすればダウンロードできる
    - https://services.gradle.org/distributions/gradle-%GRADLE_VERSION%-bin.zip
- ➂　ZIPファイルの配置
    - ダウンロードしたZIPファイルは以下フォルダを作成し配置
    - C:\ONEsLOGI\Tools\gradle\gradle-%GRADLE_VERSION%-bin.zip
#### ④　インストール用バッチを実行

    - 下記のbatを実行
    - 「最新ソースの格納フォルダ\dbflute\GradleInstall.bat」
    - 何かキーを押下

![dbfluteのjarファイルの生成_4.png][dbfluteのjarファイルの生成_4.png]

### ２． dbfluteのjarファイルの生成

#### ①　バッチを実行

    - 下記のbatを実行
    - 「最新ソースの格納フォルダ\dbflute\GradleBuild.bat」
    - 何かキーを押下
#### ②　jarファイルただしく生成するか確認

    - 「最新ソースの格納フォルダ\wms\WebContents\WEB-INF\lib」ファイルに、jarファイルを生成するか、更新日時が最新の日時するか確認







![dbfluteのjarファイルの生成_3.png][dbfluteのjarファイルの生成_3.png]


![dbfluteのjarファイルの生成_5.png][dbfluteのjarファイルの生成_5.png]


![dbfluteのjarファイルの生成_6.png][dbfluteのjarファイルの生成_6.png]


![dbfluteのjarファイルの生成_7.png][dbfluteのjarファイルの生成_7.png]


---

## プロジェクト(フォルダ)を開く

VSCodeでフォルダを開き、環境作成

### 1.フォルダ―を開く
![プロジェクト_フォルダ_を開く_3.png][プロジェクト_フォルダ_を開く_3.png]


### 2.プロジェクトフォルダを選択する

- Gitでプルしてきたプロジェクトフォルダを参照する。
- フォルダは「wms」
- となる。
- ※Angular環境では「wms-ui」を別で開く必要がある。
![プロジェクト_フォルダ_を開く_4.png][プロジェクト_フォルダ_を開く_4.png]

### 3.作成者を信頼する画面が出たなら、チェックボックスをONにして「はい、作成者を信頼します。」を押下する。
![プロジェクト_フォルダ_を開く_1.png][プロジェクト_フォルダ_を開く_1.png]

Gitの紐付け要否
![プロジェクト_フォルダ_を開く_2.png][プロジェクト_フォルダ_を開く_2.png]

---

## DB接続情報設定

#### ①プロンプトに、DB接続情報を設定する

・プロジェクト内の“wms”→ “resources”→“dbcp.properties”を選択

- \wms\resources\dbcp.properties

![DB接続情報設定_1.png][DB接続情報設定_1.png]


---

## 環境構築

VSCode上でのTomcat起動の設定、およびコンテキスト追加

### 1."TomcatDebugConfig.bat"を実行

- C:\[Gitからプルしたフォルダ]\wms\TomcatDebugConfig.batをダブルクリックする。
![環境構築_5.png][環境構築_5.png]

### 2.バッチが起動したら、「1」を入力する。
![環境構築_1.png][環境構築_1.png]

### 3.Tomcat10のフォルダを設定する。

- インストールしているTomcatフォルダ、またはpleiades以下のTomcatフォルダを設定する。
![環境構築_2.png][環境構築_2.png]
### 4.デフォルトでEnter
![環境構築_3.png][環境構築_3.png]

### 5.プロジェクト指定

- コンテキストファイルを作成する。
- 1でEnter
- コンテキスト名はデフォルトのままなので、入力せずEnter
![環境構築_6.png][環境構築_6.png]
![環境構築_7.png][環境構築_7.png]

### 6.設定完了
![環境構築_8.png][環境構築_8.png]

### 7.settings.json編集

- ユーザーのSettings.jsonを編集する。
- パスはC:\[ユーザー名]\AppData\Roaming\Code\User\settings.jsonとなる

![環境構築_4.png][環境構築_4.png]

---

## Tomcat調整

TomcatのShutdownポート変更対応

- 最近のWindows環境ではポート【8005】が予約されている事があり、Tomcat起動時にエラーになる事がある為
- ポートを変更しVS CodeからTomcatの終了操作を行えるようにする。
- ※VS CodeではTomcatの強制終了に対応していない為、Shutdownポートには【-1】以外の有効なポートを設定する事が望ましい
- C:\[pleadesのフォルダ]\tomcat\10\conf\server.xml
- 旧)　<Server port="8005" shutdown="SHUTDOWN">
- 例)　<Server port="58005" shutdown="SHUTDOWN">

![Tomcat調整_1.png][Tomcat調整_1.png]


---

## デバッグ

### 1.Tomcatをデバッグ起動

- VSCodeの実行とデバッグのプルダウンからDebug(Launch) - Tomcatを選択してF5、または起動ボタンを押下
![デバッグ_5.png][デバッグ_5.png]

### 2.Tomcat起動完了

- ポップアップが表示され、デバッグコンソールにエラーが発生していないことを確認
![デバッグ_4.png][デバッグ_4.png]

### 3.デバッガによるブレイクポイント停止状態

- ポップアップがデバッグ状態に変更され、ステップイン、ステップオーバーなどのコマンドに変化する
![デバッグ_3.png][デバッグ_3.png]

### 4.Tomcat停止

- ポップアップの停止ボタンを押下
![デバッグ_2.png][デバッグ_2.png]

### 5.Tomcat停止完了

- ポップアップが消えてコールスタックがクリアされていること


![デバッグ_1.png][デバッグ_1.png]


---

## 成功確認

成功確認

- 下記の URL をブラウザに入力し、メニュー画面が開くかどうか確認する
    - http://localhost:ポート/コンテキスト/　（例：http://localhost:8080/wms/）
    - ※ポート：デフォルトは 8080 です。修正する場合は、URL も合わせて修正する
    - ※コンテキスト：環境構築に設定したコンテキスト、デフォルトはwms

![成功確認_1.png][成功確認_1.png]


---

## 環境削除

デプロイ設定を削除

- SD作業でServers Connecterのエクステンションを入れている場合、環境削除を行う場合は以下を参照する。
- ※Angular開発ではServers Connecterエクステンションを使用しないのでSERVERSが現れない
![環境削除_1.png][環境削除_1.png]

- 状態を同期
![環境削除_2.png][環境削除_2.png]

- デプロイ設定の削除を確認
![環境削除_3.png][環境削除_3.png]


---

## VSCodeアンインストール

- 完全な初期化は、VSCodeフォルダを再作成し直すのに加え
- 以下フォルダも除去する必要があります。
    - %APPDATA%\Code
    - %USERPROFILE%\.vscode
    - %USERPROFILE%\.rsp

---

## トラブルＱＡ

- (1)　Ｑ：　特定の操作で右下にエラーが出ます。
    - Ａ：　基本的には意味のあるエラーなので、エラー内容を読んで対応してください。
    - ただ【Community Server Connector】の【Edit Server】は一時ファイルを作成する為か
    - 実行しても無視される事がある為、その場合はVS Codeを再起動してください。
- (2)　Ｑ：　出力ウィンドウの日本語が文字化けします。
    - Ａ：　VS Codeの【出力】ウィンドウは、UTF-8を前提にしていると考えられます。
    - また他ウィンドウも含め、文字コードは以下のようになっていると推測されます。
    - ＜各ウィンドウの文字コード＞

| 対象ウィンドウ | 文字コード |
|---|---|
| 出力 | UTF-8 |
| デバッグコンソール | UTF-8 |
| ターミナル | MS932 |

    - ※Javaアプリを起動する際に【"console": "internalConsole"】を指定すると
    - 標準出力はデバッグコンソールに出力されるようになるが
    - Java側からJava起動オプションを確認したところ
    - 指定していない【-Dfile.encoding=UTF-8】が設定される事で
    - 文字化けしないようにするような考慮が存在する事を確認している
    - 上記、文字コードと異なる文字コードで該当ウィンドウにマルチバイト文字列が出力された場合
    - 文字列が文字化けする可能性がある為、各ウィンドウの文字コードを踏まえ、対応する必要があります。
    - ※通常であれば、特別に何か設定しなくても、標準の設定であれば文字化けしない筈

---

