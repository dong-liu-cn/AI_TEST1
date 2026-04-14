## 目次

### 第1部：VSCode開発環境構築手順書（ORACLE版）

- [1. 資料作成時のバージョン情報](#1-資料作成時のバージョン情報)
- [2. 前提条件](#2-前提条件)
- [3. 既存プロジェクトVSCode対応](#3-既存プロジェクトvscode対応)
- [4. 起動後～拡張機能インストール](#4-起動後拡張機能インストール)
- [5. DB定義にかんするTSVファイルの出力](#5-db定義にかんするtsvファイルの出力)
- [6. テーブル定義の生成](#6-テーブル定義の生成)
- [7. DB構築](#7-db構築)
- [8. dbfluteのjarファイルの生成](#8-dbfluteのjarファイルの生成)
- [9. プロジェクト（フォルダ）を開く](#9-プロジェクトフォルダを開く)
- [10. DB接続情報設定](#10-db接続情報設定)
- [11. 環境構築（Tomcat設定）](#11-環境構築tomcat設定)
- [12. Tomcat調整](#12-tomcat調整)
- [13. デバッグ](#13-デバッグ)
- [14. 成功確認](#14-成功確認)
- [15. 環境削除](#15-環境削除)
- [16. VSCodeアンインストール](#16-vscodeアンインストール)
- [17. トラブルQA](#17-トラブルqa)

# 第1部：VSCode開発環境構築手順書（ORACLE版）

---

## 1. 資料作成時のバージョン情報

資料作成時の主要（本体・拡張機能）なバージョンを記載しておく。

> **※参考情報として掲載しているだけであり、原則最新版の利用を推奨**

| ソフトウェア | バージョン |
|---|---|
| VS Code | 1.105.1 |
| Japanese Language Pack for Visual Studio Code | v1.105.2025101509 |
| Extension Pack for Java | v0.30.3 |

---

## 2. 前提条件

開発に必要となる以下ソフトはディスク上に展開済である事を前提としている。

> **※ソフトとの紐付けは別途行う為、OSにインストールされている（環境変数に登録されている）必要はない**

- VSCode
- Java
- Tomcat

VS Codeから利用可能なEclipseのJavaプロジェクトを前提としている。  
VS Codeから利用可能にする方法は「[3. 既存プロジェクトVSCode対応](#3-既存プロジェクトvscode対応)」を参照し対応する事。

---

## 3. 既存プロジェクトVSCode対応

EclipseとVS Code、両方で動作する環境を作成する場合、**`.classpath`** に設定される内容を調整する必要があります。

> **※既に実施済であれば、本作業はスキップしてください**

具体的には以下の手順で `.classpath` を調整します。

1. **【プロジェクト＞プロパティ】** を開き **【Javaのビルド・パス＞ライブラリ】** の定義を全て除去
2. **【ライブラリの追加】** を押下、**【JREシステム・ライブラリ】** を選択し **【次へ】** を押下
3. **【実行環境】** を選択し「該当バージョンのJava」を選択し **【完了】** を押下
4. **【JARの追加】** を押下、「該当プロジェクトフォルダ」を選択し「libフォルダ（例：`WebContents\WEB-INF\lib`）」内のJARファイルを全て選択し **【OK】** を押下

> **補足：** VS Codeでプロジェクトを開くと `.project` が更新されますが、Eclipse側には影響しない為、そのまま利用してください。

---

## 4. 起動後～拡張機能インストール

VS Codeを起動した後、以下の手順で拡張機能をインストールする。

### 4.1 日本語インストール

VS Codeの拡張機能マーケットプレイスから **Japanese Language Pack for Visual Studio Code** をインストールする。

![日本語パックインストール][04_extensions_01_row2.png]

### 4.2 VS Code再起動

日本語パックインストール後、VS Codeを再起動して日本語化を適用する。

![VS Code再起動][04_extensions_02_row45.png]

### 4.3 Java関連インストール

拡張機能マーケットプレイスから **Extension Pack for Java** をインストールする。

![Java拡張機能インストール][04_extensions_03_row88.png]

---

## 5. DB定義にかんするTSVファイルの出力

### 5.1 DataManageToolの設定ファイルをOracle用に設定変更

① `「最新ソースの格納フォルダ」\dbflute\database\DataManageTool\conf` 内の設定ファイルを、以下の内容に従い変更

- **`DataManageTool.xlsx`** を変更

![DataManageTool.xlsx の変更][05_tsv_output_03_row13.png]

  | 変更前後 | 値 |
  |---|---|
  | 前) | `DataOutputFolder = ..\..\dbflute_dfclient_mysql\playsql\data\common\tsv\UTF-8` |
  | 後) | `DataOutputFolder = ..\..\dbflute_dfclient_oracle\playsql\data\common\tsv\UTF-8` |

- **`DBFluteDfpropOutput.xlsx`** を変更

![DBFluteDfpropOutput.xlsx の変更][05_tsv_output_04_row28.png]

  | 変更前後 | 値 |
  |---|---|
  | 前) | `DataOutputFolder = ..\..\dbflute_dfclient_mysql\dfprop` |
  | 後) | `DataOutputFolder = ..\..\dbflute_dfclient_oracle\dfprop` |

### 5.2 データ管理ツールのバッチを実行し、DB定義にかんするTSVファイルを出力する

① **バッチの実行**

下記のbatを実行：

```
「最新ソースの格納フォルダ」\dbflute\database\DataManageTool\bat\DataManageTool_Exec_00All.bat
```

![バッチ実行画面][05_tsv_output_01_row54.png]
![TSVファイル生成確認][05_tsv_output_02_row86.png]

② **TSVファイルを正しく生成するか確認**

以下のフォルダにTSVファイルが生成され、更新日時が最新であるか確認する：

```
「最新ソースの格納フォルダ\dbflute_dfclient_oracle\playsql\data\common\tsv\UTF-8」
```

![TSVファイル出力結果][05_tsv_output_05_row124.png]

---

## 6. テーブル定義の生成

### 6.1 A5:SQL Mk2のインストール

以下のURLからダウンロードする：

- [https://a5m2.mmatsubara.com/](https://a5m2.mmatsubara.com/)

![A5:SQL Mk2 ダウンロードサイト][06_table_gen_01_row7.png]

### 6.2 DB定義を生成する

① 下記のファイルをダブルクリックし、A5:SQL Mk2でER図を開く：

```
「最新ソースの格納フォルダ」\dbflute\database\ER図.a5er
```
![ドメイン編集ウインドウ][06_table_gen_03_row96.png]


② **ドメインを更新する**

ナビゲーションバーの **「ER図」→「ドメインを編集する」** をクリックして、ドメイン編集ウインドウを開き、各データ型の内容をOracle用に変更する。


変更前：

![ドメイン変更前][06_table_gen_04_row146.png]

変更後：

![ドメイン変更後][06_table_gen_05_row164.png]

ドメイン定義：

![ドメイン定義][06_table_gen_06_row183.png]

③ **DDLを生成する**

ナビゲーションバーの **「ER図」→「DDLを作成する」** を選択、**「RDBMS種類」** を **「Oracle」** に変更し **「DDL作成」** をクリック

![DDL生成画面][06_table_gen_07_row206.png]

④ 出力されたDDL文を以下のファイルの内容を空にして反映：

```
「最新ソースの格納フォルダ\dbflute\dbflute_dfclient_oracle\playsql\replace-schema-01-table.sql.txt」
```

![DDL出力結果][06_table_gen_08_row238.png]

---

## 7. DB構築

### 7.1 前提

Oracle DBとschemaを作成済みであること。

> **※ Oracle サーバーのインストールおよびスキーマの作成については、別途記述する予定**

| 項目 | 値 |
|---|---|
| Oracleバージョン | 19C |
| 文字コード | UTF-8 |


### 7.2 構築手順

① **dbfluteにDB接続情報を設定**

修正ファイル：

```
「最新ソースの格納フォルダ」\dbflute\dbflute_dfclient_oracle\dfprop\databaseInfoMap.dfprop
```
    - 接続先を作成したものに変更。例は仮接続先）  
    - ・DBサーバーの接続情報（IPアドレス、schemaなど）
    - ・ユーザー名 
    - ・パスワード

![DB構築 概要][07_db_build_01_row17.png]

② **DBを作成する**

下記のbatを実行：

```
「最新ソースの格納フォルダ\dbflute\dbflute_dfclient_oracle\manage.bat」
```
![DB接続情報設定ファイル][07_db_build_02_row62.png]

実行手順：
1. `1` を入力し、**【Enter】**

![manage.bat実行 - "1"を入力][07_db_build_03_row91.png]

2. `y` を入力し、**【Enter】**

![manage.bat実行 - "y"を入力][07_db_build_04_row120.png]

3. `BUILD SUCCESSFUL` で終了したら、**【Enter】**

![BUILD SUCCESSFUL 完了画面][07_db_build_05_row150.png]

> **※ `BUILD FAILD` の場合、エラーメッセージを確認した上で再実行**

---

## 8. dbfluteのjarファイルの生成

### 8.1 Gradleのインストール

① **JAVA_HOMEの設定**

- `「最新ソースの格納フォルダ\dbflute\Gradle.env」` を開く
![JAVA_HOME設定][08_dbflute_jar_02_row10.png]
- JAVA_HOMEを設定する
![Gradleダウンロード][08_dbflute_jar_01_row41.png]


② **GradleのZIPファイルをダウンロード**

ZIPは以下URLにアクセスすればダウンロードできる：

```
https://services.gradle.org/distributions/gradle-%GRADLE_VERSION%-bin.zip
```



③ **ZIPファイルの配置**

ダウンロードしたZIPファイルは以下フォルダを作成し配置：

```
C:\ONEsLOGI\Tools\gradle\gradle-%GRADLE_VERSION%-bin.zip
```


④ **インストール用バッチを実行**

下記のbatを実行：

```
「最新ソースの格納フォルダ\dbflute\GradleInstall.bat」
```
![ZIPファイル配置][08_dbflute_jar_03_row80.png]

→ 何かキーを押下

![Gradleインストールバッチ実行][08_dbflute_jar_04_row110.png]

### 8.2 dbfluteのjarファイルの生成

① **バッチを実行**

下記のbatを実行：

```
「最新ソースの格納フォルダ\dbflute\GradleBuild.bat」
```
![GradleBuildバッチ実行][08_dbflute_jar_05_row149.png]
→ 何かキーを押下

![バッチ実行結果][08_dbflute_jar_06_row179.png]

② **jarファイルを正しく生成するか確認**

以下のフォルダにjarファイルが生成され、更新日時が最新であるか確認する：

```
「最新ソースの格納フォルダ\wms\WebContents\WEB-INF\lib」
```

![jarファイル生成確認][08_dbflute_jar_07_row214.png]

---

## 9. プロジェクト（フォルダ）を開く

VSCodeでフォルダを開き、環境を作成する。

### 9.1 フォルダを開く

VSCodeのメニューから **「ファイル」→「フォルダーを開く」** を選択する。

![フォルダを開く][09_open_project_03_row5.png]

### 9.2 プロジェクトフォルダを選択する

Gitでプルしてきたプロジェクトフォルダを参照する。  
フォルダは **`wms`** となる。

> **※Angular環境では `wms-ui` を別で開く必要がある。**

![プロジェクトフォルダ選択][09_open_project_04_row57.png]

### 9.3 作成者を信頼する

作成者を信頼する画面が出たなら、チェックボックスをONにして **「はい、作成者を信頼します。」** を押下する。
```
    - ※社内のリソースであれば問題なし。
    - ※インターネットからサンプルをダウンロードしたとかであれば、安易に信頼するべきではない事は留意する事。
```    
    
![作成者を信頼する][09_open_project_01_row85.png]

### Gitの紐付け要否

Gitの紐付けが必要な場合は、適宜設定を行う。

![Gitの紐付け][09_open_project_02_row145.png]

---

## 10. DB接続情報設定

① プロジェクトに、DB接続情報を設定する。

プロジェクト内の `wms` → `resources` → `dbcp.properties` を選択：

```
\wms\resources\dbcp.properties
```

DB接続情報（接続先URL、ユーザー名、パスワード等）を環境に合わせて編集する。

![DB接続情報設定画面][10_db_config_01_row4.png]

---

## 11. 環境構築（Tomcat設定）

VSCode上でのTomcat起動の設定、およびコンテキスト追加を行う。
```
以下資材が対象プロジェクトに存在しない場合[TI推]にご連絡下さい。
TomcatDebugConfig.batTomcatDebugConfig.ps1
```

### 11.1 "TomcatDebugConfig.bat"を実行

```
C:\[Gitからプルしたフォルダ]\wms\TomcatDebugConfig.bat
```

をダブルクリックする。

![TomcatDebugConfig.bat実行][11_env_setup_05_row7.png]

### 11.2 バッチが起動したら、`1` を入力する

![バッチに「1」を入力][11_env_setup_01_row36.png]

### 11.3 Tomcat10のフォルダを設定する

インストールしているTomcatフォルダ、またはpleiades以下のTomcatフォルダを設定する。

![Tomcat10フォルダ設定][11_env_setup_02_row74.png]

### 11.4 デフォルトでEnter

![デフォルトでEnter][11_env_setup_03_row110.png]

### 11.5 プロジェクト指定

コンテキストファイルを作成する。
- `1` でEnter
![プロジェクト指定][11_env_setup_06_row150.png]

- コンテキスト名はデフォルトのままなので、入力せずEnter
![設定完了][11_env_setup_07_row185.png]

### 11.6 設定完了
![settings.json編集][11_env_setup_08_row220.png]

### 11.7 settings.json編集

ユーザーの `settings.json` を編集する。  
パス：

```
C:\[ユーザー名]\AppData\Roaming\Code\User\settings.json
```
サーバ起動後修正を即時反映させるようにhotCodeReplaceをautoにする。
> **※Hot Deployできない修正内容についてはサーバの再起動が必要**
```
    "java.debug.settings.hotCodeReplace": "auto",
    "java.configuration.runtimes": [
        {
          "name": "JavaSE-21",
          "path": "C:/[pleadesのパス]/java/21"
        }
  ]
```
Javaプロジェクトがビルド時に利用する
java.configuration.runtimesには各プロジェクトで使用するJavaを指定する。
nameにはEclipseで設定したJRE設定時の名称を指定しpathにはJavaHome（JDK Path）を指定する。

![settings.json編集内容][11_env_setup_04_row259.png]

---

## 12. Tomcat調整

### TomcatのShutdownポート変更対応

最近のWindows環境ではポート **8005** が予約されている事があり、Tomcat起動時にエラーになる事がある為、ポートを変更しVS CodeからTomcatの終了操作を行えるようにする。

> **※ VS CodeではTomcatの強制終了に対応していない為、Shutdownポートには `-1` 以外の有効なポートを設定する事が望ましい**

対象ファイル：

```
C:\[pleadesのフォルダ]\tomcat\10\conf\server.xml
```

| 変更前後 | 内容 |
|---|---|
| 旧) | `<Server port="8005" shutdown="SHUTDOWN">` |
| 例) | `<Server port="58005" shutdown="SHUTDOWN">` |

![Tomcat Shutdownポート変更][12_tomcat_adjust_01_row12.png]

---

## 13. デバッグ

### 13.1 Tomcatをデバッグ起動

VSCodeの **「実行とデバッグ」** のプルダウンから **「Debug(Launch) - Tomcat」** を選択して **F5**、または起動ボタンを押下

![Tomcatデバッグ起動][13_debug_05_row5.png]

### 13.2 Tomcat起動完了

ポップアップが表示され、デバッグコンソールにエラーが発生していないことを確認する。

![Tomcat起動完了][13_debug_04_row26.png]

### 13.3 デバッガによるブレイクポイント停止状態

ポップアップがデバッグ状態に変更され、ステップイン、ステップオーバーなどのコマンドに変化する。

![ブレイクポイント停止状態][13_debug_03_row74.png]

### 13.4 Tomcat停止

ポップアップの停止ボタンを押下する。

![Tomcat停止][13_debug_02_row121.png]

### 13.5 Tomcat停止完了

ポップアップが消えてコールスタックがクリアされていることを確認する。

![Tomcat停止完了][13_debug_01_row168.png]

---

## 14. 成功確認

下記の URL をブラウザに入力し、メニュー画面が開くかどうか確認する。

```
http://localhost:ポート/コンテキスト/
```

例：`http://localhost:8080/wms/`

> - **ポート：** デフォルトは `8080` です。修正する場合は、URL も合わせて修正する
> - **コンテキスト：** 環境構築に設定したコンテキスト、デフォルトは `wms`

![成功確認画面][14_success_01_row8.png]

---

## 15. 環境削除

### デプロイ設定を削除

SD作業で **Servers Connecter** のエクステンションを入れている場合、環境削除を行う場合は以下を参照する。

> **※Angular開発ではServers Connecterエクステンションを使用しないのでSERVERSが現れない**

1. 状態を同期する

![デプロイ設定削除][15_env_delete_01_row6.png]

![状態を同期][15_env_delete_02_row45.png]

2. デプロイ設定の削除を確認する

![デプロイ設定の削除確認][15_env_delete_03_row84.png]

---

## 16. VSCodeアンインストール

完全な初期化は、VSCodeフォルダを再作成し直すのに加え、以下フォルダも除去する必要があります。

```
%APPDATA%\Code
%USERPROFILE%\.vscode
%USERPROFILE%\.rsp
```

---

## 17. トラブルQA

### (1) Q: 特定の操作で右下にエラーが出ます。

**A:** 基本的には意味のあるエラーなので、エラー内容を読んで対応してください。

ただし **【Community Server Connector】** の **【Edit Server】** は一時ファイルを作成する為か、実行しても無視される事がある為、その場合はVS Codeを再起動してください。

### (2) Q: 出力ウィンドウの日本語が文字化けします。

**A:** VS Codeの **【出力】** ウィンドウは、UTF-8を前提にしていると考えられます。

また他ウィンドウも含め、文字コードは以下のようになっていると推測されます。

**＜各ウィンドウの文字コード＞**

| 対象ウィンドウ | 文字コード |
|---|---|
| 出力 | UTF-8 |
| デバッグコンソール | UTF-8 |
| ターミナル | MS932 |

> **※** Javaアプリを起動する際に `"console": "internalConsole"` を指定すると、標準出力はデバッグコンソールに出力されるようになるが、Java側からJava起動オプションを確認したところ、指定していない `-Dfile.encoding=UTF-8` が設定される事で文字化けしないようにするような考慮が存在する事を確認している。

上記、文字コードと異なる文字コードで該当ウィンドウにマルチバイト文字列が出力された場合、文字列が文字化けする可能性がある為、各ウィンドウの文字コードを踏まえ、対応する必要があります。

> **※通常であれば、特別に何か設定しなくても、標準の設定であれば文字化けしない筈**

---
