# バックエンド + 共通規約（Java / DB / 帳票 / インフラ / EDI）

---

## 1. 共通規約（全レイヤー共通）

### 1.1 プロジェクト概要

- 本プロジェクトは ONEsLOGI-Web基盤（WMS）である
- バックエンド: Java（RESTEasy/JAX-RS + CDI + DBFlute）
- フロントエンド: Angular（TypeScript/SCSS）/ AngularJS（JavaScript/CSS・旧世代）
- モバイル: Flutter/Dart
- DB: Oracle（本番）/ MySQL（開発）
- 帳票: JasperReports / ExcelCreator（Excel帳票用：ExcelCreator→LibreOffice→PDFBox→PDF.js）
- APサーバ: Tomcat（標準）/ WildFly（一部環境）、Webサーバ: Apache

### 1.2 アーキテクチャ基本ルール

- Webサーバ（Apache）→ APサーバ（Tomcat）→ DB（Oracle/MySQL）の3層構成を前提とする
- Apache は `mod_proxy_ajp` で `/resources/*` パターンをAPサーバへプロキシ転送する
- 静的リソース（HTML/JS/CSS/画像）はApacheが直接配信する
- クライアントはSPA（Single Page Application）構成とする
- サーバ通信はRESTEasy（JAX-RS）ベースのRESTful APIで行う
- ブラウザ↔サーバ間の通信データは **JSON形式** を使用する
- HTTPセッションは **原則使用しない**（APサーバスケールアウトに悪影響のため）
- データ構造はDBテーブル構造に準拠する: `Resource → Dto(JSON) → クライアント`
- JSON構造の標準セクション: `status`, `output`, `paging`, `data`（`head`/`body`サブセクション）
- Dto Javaファイルが「容器」としてJSON構造を定義し、Dtoのフィールドが画面フィールドに自動マッピング（双方向バインディング）

#### JSON標準構造

```json
{
  "status": { "statusCd": 0, "messageList": [] },
  "output": {
    "data": { "head": {}, "body": [] },
    "paging": { "page": 1, "numPerPage": 100, "allRecordCount": 500 }
  }
}
```

#### StatusCdによる制御フロー

| StatusCd | 意味 | 処理 |
|----------|------|------|
| 0 | 正常 | 処理続行 |
| 1 | 警告（確認あり） | 確認ダイアログ表示→ユーザ承認で続行 |
| 2 | エラー | エラーメッセージ表示、処理中止 |

#### サーバ側クラス分類

- **Resource**: WebAPIエンドポイント（JAX-RS）
- **Logic**: 業務ロジック（必ずインタフェースを作成する）
- **Dto**: データ通信用（データのみ保持、処理を実装しない）
- 粒度: **1画面 = 1 Resource = 1 Dto**
- LogicはResourceまたは他のLogicから実行する。クライアントから直接実行しない
- DBアクセスは **原則DBFlute経由** で行う
- トランザクション管理はCDI Interceptorによる宣言的トランザクションを使用する

#### サブシステム構成

| サブシステム | 概要 |
|-------------|------|
| receive | 入荷系 |
| stock | 在庫系 |
| shipping | 出荷系 |
| master | マスタ系 |
| common | 共通部品 |
| system | システム管理 |

### 1.3 ネーミング規約

#### 機能ID
- 役割を表す名詞を連ねたキャメルケースで命名する（英字表記、ローマ字不可）
- ID連番は原則禁止
- 30文字超の場合は意味が通じるレベルで略す
- 例: `SlipNoReceiveList`

#### 帳票ID
- 役割を表す名詞を連ねた名称（名詞毎のキャメルケース）
- 例: `InventoryWorkList`（棚卸作業リスト）

#### メッセージCD
- 「実態」+「現象」+「条件・理由」+「分類」の先頭小文字キャメルケース
- 例: `locationNotInputError`

#### メッセージ種別
- `error`（エラー）, `warn`（警告）, `confirm`（確認）, `info`（情報通知）の4種から選択する

#### 区分値コード / 採番コード
- 全て大文字のスネークケースで記述する
- 採番コードは基本的にテーブルの列名と一致させる
- 例: `DEL_FLG`, `CONTROL_NO`

### 1.4 DB/テーブル設計規約

#### テーブル名
- **25文字以内**、全て大文字のスネークケース
- 接頭辞ルール: `B_`(基盤), `P_`(帳票基盤), `M_`(マスタ), `T_`(トランザクション), `H_`(履歴), `W_`(ワーク), `V_`(VIEW)
- 例: `T_RECEIVE_PLAN_H`（入荷予定ヘッダ）

#### カラム名
- **25文字以内**、全て大文字のスネークケース

#### 標準略語（必ず使用する）

| 正式名 | 略語 |
|--------|------|
| IDENTITY | ID |
| NUMBER | NO |
| CODE | CD |
| NAME | NM |
| DATE | DT |
| UPDATE | UPD |
| DELETE | DEL |
| HEAD | H |
| BODY | B |
| GROUP | GRP |
| DETAIL | DTL |

#### 共通カラム（全テーブル必須）
- `DEL_FLG` — 論理削除フラグ（`'0'`=有効, `'1'`=削除）
- `VERSION_NO` — バージョン番号（楽観ロック用）
- `ADD_DT`, `ADD_USER_CD`, `ADD_PGM_CD` — 登録日時・ユーザ・プログラム
- `UPD_DT`, `UPD_USER_CD`, `UPD_PGM_CD` — 更新日時・ユーザ・プログラム

#### 論理削除
- SELECTの条件に `DEL_FLG = '0'` を必ず含める

#### エンティティ名（論理ER図）
- 修飾語＋主要語の形で命名する（原則送り仮名は付与しない）
- 例: `入荷ステータス`

### 1.5 排他制御規約

- **楽観ロック**を使用する
- 排他制御カラム: `UPD_FUNC_ID`, `UPD_PROCESS_ID`, `UPD_OPE_USER_ID`, `UPD_OPE_DT`
- データ取得時に上記4列を取得し、更新時に `UPD_OPE_DT` を比較。変更されていればエラーとする
- VERSION_NO による楽観ロックも併用（DBFlute標準機能）

### 1.6 エラー処理規約

- 不必要に try-catch 句を作成しない
- `catch (Exception e)` をメソッド毎に定型処理として書くのは **禁止**
- 業務エラー以外のエラーはフレームワーク側（RESTEasy）に委譲する
- TryCatch句によるエラーのもみ消しやエラー内容の改竄は **原則禁止**
- 業務独自の例外クラスは作成しない
- エラー制御フロー: JS → Resource → Logic(1つの統合メソッド) → Manager
- StatusCdで段階的に確認ダイアログを制御する
- 入力チェックエラーはstatusセクションのmessageListに格納して返却する

### 1.7 メッセージ表示基準

| ダイアログ種別 | 用途 |
|--------------|------|
| エラー | 処理継続上、致命的な問題がある場合 |
| 警告 | 処理継続可能だが確認事項がある場合 |
| 情報 | 処理結果を通知する場合 |
| 確認 | ユーザに処理の実行要否を確認する場合 |

### 1.8 グローバル対応規約

#### Java（帳票）
- フォント: IPAフォント固定（中国語はNotoSansHans）
- フォントの追加・マッピングは可能だが、マスタ管理による動的切替は不可

### 1.9 セキュリティ規約

- 全てのユーザ入力値に対してバリデーションを実施する
- SQLインジェクション対策: **パラメータバインドを必ず使用する**（リテラル直接埋め込み禁止）
- XSS対策: 出力時にエスケープ処理を行う
- 認証方式: SAML認証（IdP連携SSO）、簡易認証（独自ログイン画面）、Google Authenticator（TOTP方式2要素認証）
- HTTPセッションは原則使用しない

---

## 2. バックエンド規約（Java）

### 2.1 Javaコーディング基準

#### ファイル構成（CODE01）
- 1ファイルに1つのpublicクラスを定義する
- ファイル名はpublicクラス名と一致させる
- パッケージ宣言は必ずファイル先頭に記述する

#### 命名規約（CODE02）
- クラス名: 先頭大文字キャメルケース（例: `ReceivePlanInput`）
- メソッド名: 先頭小文字キャメルケース（例: `searchReceivePlan`）
- 定数: 全て大文字のスネークケース（例: `MAX_RETRY_COUNT`）
- 変数名: 先頭小文字キャメルケース、役割を表す名称
- ブーリアン変数: `is` / `has` / `can` 等の接頭辞を推奨

#### コメント（CODE03）
- 全publicクラス・メソッドにJavadocを記述する
- 複雑な処理ロジックにはインラインコメントを付与する
- TODO / FIXME コメントは解決後に必ず削除する

#### インデント・フォーマット（CODE04）
- インデント: スペース4つ（タブ使用禁止）
- 可読性を維持する範囲で1行の文字数を制御する
- 開き中括弧 `{` は宣言行の最後に記述する
- 閉じ中括弧 `}` は宣言文の先頭とインデントを合わせる

#### 変数宣言（CODE05）
- 変数は**使用する箇所で宣言する**（メソッド先頭でまとめて宣言しない）
- 上位スコープの変数を下位スコープで上書きしない
- 1つの宣言を1行に書く（`int level, size;` は禁止）
- 単純な変数初期化は宣言時に行う

#### クラスとインタフェースの宣言
- メソッド名と `(` の間にスペースを入れない
- 開き中括弧 `{` は宣言行の最後に記述する
- 閉じ中括弧 `}` は宣言文の先頭とインデントを合わせる
- メソッドは空行で区切る
- クラス変数とメソッド引数が同名にならないようにする

#### 制御文ルール（CODE06）
- 1行に1つの文のみ記述する（`i++; j++;` は禁止）
- **1文だけでも必ず中括弧 `{}` を使用する**（if/for/while/try-catch全て）
- return文は返り値に条件式がある場合を除き小括弧を使用しない
- switch文では全caseにbreak/returnを付与し、全switchにdefault節を定義する

#### スコープ（CODE07）
- 変数のスコープは必要最小限にする
- クラス変数は極力避け、ローカル変数を優先する
- メソッドの引数とクラス変数が同名にならないよう極力避ける

#### エラー処理（Java固有）（CODE08）
- 不必要にtry-catch句を作成しない
- `catch (Exception e)` をメソッド毎に定型処理として書くのは**禁止**
- 業務エラー以外はRESTEasy側に委譲する
- 業務独自の例外クラスは作らない

#### 制御フロー（CODE09）
- 深いネストは避ける（早期returnパターンを活用）
- 複雑な条件式は変数に分解する

#### 品質（効率性）（CODE10）
- 不要なオブジェクト生成を避ける
- ループ内でのDB呼び出しは最小化する
- 文字列連結にはStringBuilderを使用する

#### 品質（保守性）（CODE11）
- マジックナンバーを使用しない（定数化する）
- メソッドの行数は適切な長さに保つ
- 重複コードは共通化する

#### 品質（信頼性）（CODE12）
- NullPointerExceptionを防ぐ防御的プログラミング
- リソース（ストリーム等）は必ずclose/try-with-resourcesで解放する

#### 品質（移植性）（CODE13）
- OS依存のパス区切り文字を直接使用しない
- 文字エンコーディングを明示する（UTF-8を標準とする）

### 2.2 Java命名規約

#### パッケージ名
- すべて小文字、システムや役割で階層を分ける
- 例: `com.oneslogi.wms.resources.receive`

#### クラスパス（Resource）
- `@Path("/[サブシステム名]/[役割名]")`
- HTMLやJavaScriptの画面系と名称を一致させる
- 例: `@Path("/receive/receivePlanInput")`

#### クラス名（Resource）
- `[役割名]Resource.java`（例: `ReceiveListResource.java`）

#### クラス名（Logic）
- `[役割名]Logic.java`（例: `ReceiveListLogic.java`）
- 1テーブル共通処理: `[テーブル名（接頭辞除く）]Logic.java`

#### メソッドパス（Resource）
- `@Path("/[動詞+名詞]")`（先頭小文字キャメルケース）

#### メソッド名
- `[動詞] + [対象名詞]`（先頭小文字キャメルケース）

#### 変数名
- **定数**: 全て大文字のスネークケース（例: `MAX_VALUE`）
- **メンバ変数**: クラス名の頭を小文字にした名称（例: `private Bsystem bSystem;`）
- **ローカル変数**: 役割を表す名称
- **ループカウンタ**: `i/j/k` の順
- **例外変数**: `e`

### 2.3 Service/Logic/Resource層 実装規約

- **CODE01**: 業務ロジック（Service層/Helper層）にはインタフェースを作成する
- **CODE02**: テーブル（ビュー）の利用方法に従う — DBFluteのBehaviorSelect/BehaviorCommandを使用
- **CODE03**: 画面上のクエリー利用方法に従う — ConditionBean基本、複雑時は外だしSQL
- **CODE04**: SQL上のリテラル利用は禁止（パラメータバインドを使用する）
- **CODE05**: DBFluteの自動生成Entityを利用する
- **CODE06**: Entity以外のSELECT結果は外だしSQLのCustomize Entityで受け取る
- **CODE07**: ログの利用方法に従う — SLF4J/LogBack使用、業務エラーはログ出力しない
- **CODE08**: 業務日付はシステムから統一的に取得する（SystemHelper等の共通部品使用）
- **CODE09**: 区分値マスタの利用方法に従う — DBFluteのClassification機能使用
- **CODE10**: Excelファイルダウンロードの実装規約に従う — 大量データはSXSSFWorkbook
- **CODE11**: CSVファイルダウンロードの実装規約に従う — UTF-8（BOM付き）標準
- **CODE12**: 外だしSQL（DBFlute）の利用規約に従う — sql2entityで自動生成
- **CODE13**: ファイルアップロードの実装規約に従う — マルチパート、サイズ上限バリデーション
- **CODE14**: 宣言的トランザクション管理を使用する — CDI Interceptor
- **CODE15**: 非同期処理の実装規約に従う — CDIイベント/ExecutorService
- **CODE16**: サーバ側入力チェックの実装規約に従う — Bean Validation + Logic層チェック
- **CODE17**: メール送信の実装規約に従う — JavaMail使用

### 2.4 Javadoc記述基準
- 全publicクラス・メソッドにJavadocを記述する
- @param, @return, @throws を適切に記述する
- Javadoc出力VMオプション: `-J-Xmx1024m -encoding "utf-8" -charset "utf-8" -noqualifier all`

---

## 3. DB/SQL/DBFlute規約

### 3.1 SQL開発規約

- `SELECT *` は使用しない。必要な項目だけを記述する
- `DISTINCT` は使用しない。使わなくて済むように設計する
- ソート不要であれば `ORDER BY` を外す
- 複合インデックスを使う場合、WHERE句にインデックスと同じ順番で条件指定する
- 結合条件はインデックスが有効になるよう記述する
- カーソルは使用しない（不可避の場合は処理が冗長にならないよう注意）
- `LIKE '%xxx%'` のような前方一致でない曖昧検索は使用しない（使用時は性能検証必須）
- SQL上のリテラル利用は**禁止**（パラメータバインドを必ず使用する）

### 3.2 DBFlute利用規約

- O/RマッパーとしてDBFluteを使用する
- DBFluteの自動生成Entityを利用する（CODE05）
- Entity以外のSELECT結果は外だしSQLで受け取る（CODE06）
- 外だしSQLが複雑な場合、一部の処理をJava側に移す検討をする
- 外だしSQLのCOUNTでは件数取得に必要なテーブル・カラムに限定する
- 親子関係のテーブル登録では親テーブルもバルクインサートで実装する
- 抽出系SQLの実行回数を意識してコーディングする

### 3.3 DBFlute固有の利用規約

| 規約 | 内容 |
|------|------|
| ConditionBean | 基本的な検索はConditionBeanを使用する |
| 外だしSQL | 複雑なSQLは外だしSQL機能を使用する |
| sql2entity | 外だしSQLのEntity/パラメータBeanは `manage.bat` の sql2entity で自動生成 |
| regenerate | テーブル変更後は `manage.bat` の regenerate で再生成 |
| 共通カラム自動設定 | ADD_DT/UPD_DT等の共通カラムはDBFluteの自動設定機能を使用 |
| 楽観ロック | VERSION_NOによる楽観ロックはDBFlute標準機能を使用 |
| load-data-reverse | テストデータ作成時に使用（メモリ不足に注意） |

### 3.4 DBFlute Tips（主要17件）

| # | Tips | 対処法 |
|---|------|--------|
| 1 | Injectでインスタンスがnullになる | `beans.xml` の確認、スコープ設定の確認 |
| 2 | load-data-reverseがメモリ不足エラー | `_project.bat` 内のJVMヒープサイズを増加 |
| 3 | manage.batのregenerateに時間がかかる | 不要テーブルの除外設定 |
| 4 | manage.batのsql2entityでエラー | SQLファイルの構文確認、パラメータコメントの書式確認 |
| 5 | VersionNoの更新を止めたい | 楽観ロック無効化設定 |
| 6 | テーブル間のリレーションを追加したい | additionalForeignKeyMap設定 |
| 7 | 外だしSQLが実行時エラーになる | SQL構文確認、型マッピング確認 |
| 8 | 外だしSQLの引数の型を手動設定したい | ParameterBean型指定方法 |
| 9 | 外だしSQLの検索結果の型を手動設定したい | CustomizeEntity型指定方法 |
| 10 | 共通カラムの自動更新を停止したい | CommonColumnAutoSetupper設定 |
| 11 | 区分値マスタとテーブルのリレーションを追加したい | Classification設定 |
| 12 | 区分値明細を画面から追加した場合にDBFluteに反映したい | 区分値再生成手順 |
| 13 | 大量データの一括登録をしたい | バルクインサート実装 |
| 14 | ConditionBeanで外部結合をしたい | LeftOuterJoin設定 |
| 15 | 排他制御（楽観ロック）の実装 | VERSION_NO利用方法 |
| 16 | DBFluteでページング処理をしたい | PagingResultBean使用方法 |
| 17 | テスト用データの作成方法 | load-data-reverse活用 |

### 3.5 実装サンプル索引

| サンプルファイル | 内容 |
|----------------|------|
| 外だしSQLが複雑な場合、一部の処理をJava側に移す検討をする事.txt | SQLをJava側に移すサンプルコード |
| 外だしSQLのCOUNTでは件数取得に必要なテーブル、カラムに限定する事.txt | COUNT文の最適化サンプル |
| 親子関係のテーブル登録で、親テーブルもバルクインサートで実装する事.txt | 親テーブルのバルクインサートサンプル |
| 抽出系SQLの実行回数を意識してコーディングを行う事.txt | SQL実行回数の最適化サンプル |

---

## 4. 帳票規約（JasperReports / ExcelCreator）

### 4.1 帳票ツール

- レイアウト作成: **Jaspersoft Studio**
- 帳票出力制御: **JasperReports**
- 式言語: **Java**

### 4.2 基本フォント

- **IPAexフォント（ゴシック）** を使用する（フリーフォント）
- OS依存フォントは使用しない（マルチOS対応・PDF/印刷の一貫性のため）
- 中国語: NotoSansHans

### 4.3 レイアウト規約

#### マージン
- 全方向: **20ピクセル**

#### フォント設定

| 区分 | フォント名 | サイズ |
|------|----------|--------|
| タイトル部 | IPAexゴシック | 24 |
| その他全般 | IPAexゴシック | 10 |

#### 行の高さ

| 区分 | 高さ |
|------|------|
| ヘッダ行 | 20ピクセル |
| データ行 | 15ピクセル |

#### 罫線
- 太さ: **0.5ポイント**
- 色: **黒(#000000)**

#### バーコード
- バーコードサイズを一定にする場合の設定方法あり
- バーコード値がNULLの場合の異常終了対策が必要

#### QRコード
- QRコード対応あり（専用jarが必要）

### 4.4 ExcelCreator帳票（Excel帳票出力）

#### 概要
- JasperReportsとは別の帳票出力方式として **ExcelCreator** が存在する
- Excelテンプレートをベースに帳票データを埋め込み、Excel/PDF形式で出力する

#### 処理フロー
```
ExcelCreator → Excelファイル生成 → LibreOffice → PDF変換 → PDFBox → PDF加工 → PDF.js → ブラウザ表示
```

#### 利用シーン
- Excel形式のレイアウトが必要な帳票
- 既存のExcelテンプレートを活用する帳票
- JasperReportsでは表現しにくい複雑なExcelレイアウト

#### 注意事項
- LibreOfficeのサーバインストールが必要
- PDF変換時のフォント埋め込みに注意
- サーバ側でのExcel操作はメモリ使用量に注意

### 4.5 Jaspersoft Studio Tips

| Tips | 内容 |
|------|------|
| リプレーススキーマ活用 | デザイン変更時の効率化 |
| PDFプレビュー余白問題 | 印刷時の余白設定対策 |
| フィールド定義自動生成 | SQLからのフィールド自動取込 |
| プレビュー表示されない | フォント設定の確認 |
| バーコード生成 | barcode4j設定 |
| QRコード生成 | qrcode.jar設定 |

---

## 5. 性能規約

### 5.1 性能目標

| 処理種別 | 性能目標 |
|---------|---------|
| サーバサイド処理 | **3秒以内** |
| 画面描画 | **3秒以内** |
| Excel出力（最大件数） | **30秒以内** |
| 帳票出力（最大件数） | **30秒以内** |

- サーバサイド処理とクライアントサイド処理（画面描画）の性能は切り離して考える
- サーバサイド: 検索処理を行い検索結果を返すまでの時間
- 画面描画: 検索結果データを受信しウィジェットにデータ設定が完了するまでの時間

### 5.2 SQL開発時の注意事項

- 検索結果データは**3000件以下**になるようにする（Excel/帳票出力は対象外）
- `SELECT *` は使用しない。必要な項目だけを記述する
- `DISTINCT` は使用しない
- ソート不要であれば `ORDER BY` を外す
- 複合インデックスを使う場合、WHERE句にインデックスと同じ順番で条件指定する
- 結合条件はインデックスが有効になるよう記述する
- カーソルは使用しない
- `LIKE '%xxx%'` のような前方一致でない曖昧検索は使用しない（使用時は性能検証必須）

### 5.3 画面描画のポイント

- `ng-repeat` は**1000行**を超えないようにする
- `$watch` の不要な作成を避ける
- `ng-if` と `ng-show`/`ng-hide` の使い分けを検討する（DOMを削除する方がパフォーマンスが良い場合は `ng-if`）
- 大量データの表示にはページングを活用する
- 画像やアイコンの遅延ロードは行わない（初期ロード方針に従う）

### 5.4 ER図設計のポイント

- 非正規化テーブルや冗長カラムの利用をパフォーマンス観点で検討する
- インデックス設計はクエリパターンに基づいて行う
- 検索頻度の高いカラムにはインデックスを設定する

---

## 6. インフラ・サーバ環境構築規約

### 6.1 サーバ環境構成

#### 推奨構成

| コンポーネント | 推奨バージョン | 備考 |
|--------------|--------------|------|
| OS | CentOS 6.x / 7.x (64bit) | 本番環境 |
| JDK | OpenJDK 1.7 / 1.8 | 64bit版 |
| Apache HTTP Server | 2.2.x / 2.4.x | CentOS標準 |
| Tomcat | 7.x / 8.x | WildFly/JBossも一部環境で使用 |
| Oracle DB | 11g / 12c | 本番環境 |
| MySQL | 5.6 / 5.7 | 開発環境 |
| メモリ | 4GB以上 | 最低要件 |

#### ディレクトリ構成（標準）

```
/opt/tomcat/                    # Tomcatインストールディレクトリ
/opt/tomcat/webapps/            # Webアプリケーションデプロイ先
/var/www/html/                  # Apache静的コンテンツ配信ルート
/etc/httpd/conf/                # Apache設定ファイル
/etc/httpd/conf.d/              # Apache追加設定
```

### 6.2 Apache設定

#### 基本設定
- `Listen 80`
- `DocumentRoot "/var/www/html"`
- `DirectoryIndex index.html`
- `mod_proxy_ajp` を使用してTomcatへプロキシ転送

#### プロキシ設定例
```apache
ProxyPass /resources/ ajp://localhost:8009/[app-context]/resources/
ProxyPassReverse /resources/ ajp://localhost:8009/[app-context]/resources/
```

### 6.3 Tomcat設定

#### 基本設定
- HTTP ポート: `8080`
- AJP ポート: `8009`（Apache連携用）
- シャットダウンポート: `8005`
- WAR ファイルデプロイ方式

#### JVM設定
- ヒープサイズ: `-Xms512m -Xmx2048m`（環境に応じて調整）
- メタスペース: `-XX:MaxMetaspaceSize=512m`
- 文字エンコーディング: `-Dfile.encoding=UTF-8`

### 6.4 データベース設定

#### Oracle（本番）
- キャラクタセット: `AL32UTF8`
- 接続プール: コネクションプーリングを使用する

#### MySQL（開発）
- キャラクタセット: `utf8mb4`
- 照合順序: `utf8mb4_general_ci`
- `lower_case_table_names=1`（テーブル名の大文字小文字を区別しない）

### 6.5 デプロイ手順

1. ビルド（Maven/Gradle）でWARファイルを生成
2. 既存WARファイルのバックアップ
3. Tomcat停止
4. WARファイルを `webapps/` に配置
5. 静的コンテンツをApacheのDocumentRootに配置
6. Tomcat起動
7. 動作確認

### 6.6 自動印刷

#### 概要
- サーバサイドから帳票を自動的にプリンターへ出力する機能
- 業務処理の一環として、ユーザ操作なしで帳票印刷を実行する

#### 処理フロー
```
[業務処理] → [帳票生成（JasperReports）] → [PDF生成] → [印刷キュー登録] → [プリンター出力]
```

#### 印刷設定
- プリンター設定はマスタで管理する
- プリンター割り当て: 倉庫/センター単位で設定可能
- 用紙サイズ・向き・部数の設定

#### エラー処理
- プリンター接続エラー時のリトライ処理
- 印刷失敗時のログ出力と通知
- 印刷キューの状態管理

---

## 7. EDI・汎用データ入出力規約

### 7.1 EDI連携概要

#### EDI（Electronic Data Interchange）機能
- 外部システムとの電子データ交換を行う機能
- 受信（インバウンド）・送信（アウトバウンド）・データ変換の3機能を提供

#### EDI処理フロー
```
[外部システム] → [EDI受信] → [データ変換] → [WMS取込]
[WMS出力] → [データ変換] → [EDI送信] → [外部システム]
```

#### EDIデータフォーマット
- 固定長フォーマット
- CSVフォーマット
- XMLフォーマット
- フォーマット定義はマスタで管理する

### 7.2 汎用データ入出力

#### 概要
- マスタデータ・トランザクションデータの一括取込/出力機能
- Excel / CSV 形式に対応
- 取込テンプレートを使用したデータ入力支援

#### 取込処理
- ファイルアップロード → バリデーション → データ登録 の3ステップ
- バリデーションエラーは行番号・カラム名とともにエラーリストを返却
- 大量データの取込はバッチ処理として実行可能

#### 出力処理
- 検索条件を指定してデータ抽出
- Excel / CSV 形式で出力
- 大量データはストリーミング出力を使用

---

## 8. 実装サンプル・Tips索引

### 8.1 開発規約Tips

| ID | 内容 |
|----|------|
| TIPS01 | ConditionBean使用時のTips |
| TIPS02 | 外だしSQL記述時のTips |
| TIPS03 | Logic間の依存関係のTips |
| TIPS04 | Dtoフィールド設計のTips |
| TIPS05 | 画面-サーバ間データ連携のTips |
| TIPS06 | エラーメッセージ管理のTips |
| TIPS07 | 楽観ロック実装のTips |
| TIPS08 | バルクインサート実装のTips |
| TIPS09 | ページング実装のTips |
| TIPS10 | ファイルアップロード実装のTips |
| TIPS11 | Excel出力実装のTips |
| TIPS12 | 帳票出力実装のTips |

### 8.2 画面プログラムTips

| ファイル | 内容 |
|---------|------|
| 画面プログラム_Tips.xlsx | カラム定義動的変更、DB操作メソッド、ログインユーザ情報取得、更新ログ出力 |
| OPAL画面プログラム_Tips.xlsx | ER設計、共通部品、JSP/JS/Java/SQL/Entity/Logic記述方法、Excelデータフロー |
| マスタメンテプログラム作成方法.xlsx | 単一テーブル・単一キーのマスタメンテ作成手順 |
| コードマスタメンテプログラム作成方法.xlsx | コードマスタメンテ作成手順 |

### 8.3 各技術別Tips一覧

#### Java Tips
| Tips | 内容 |
|------|------|
| 日付操作Tips | LocalDate/LocalDateTime活用 |
| 文字列操作Tips | StringUtils活用 |
| コレクション操作Tips | Stream API活用 |
| ファイル操作Tips | NIO.2活用 |

#### SQL Tips
| Tips | 内容 |
|------|------|
| Oracle固有関数Tips | NVL, DECODE, ROWNUM等 |
| MySQL固有関数Tips | IFNULL, IF, LIMIT等 |
| パフォーマンスTips | EXPLAIN活用、インデックス最適化 |

#### サーバ基盤 Tips
| Tips | 内容 |
|------|------|
| Tomcat設定Tips | server.xml、context.xml設定 |
| Apache設定Tips | httpd.conf、ProxyPass設定 |
| ログ設定Tips | logback.xml設定 |
| デプロイTips | WAR配置手順 |

#### テーブル定義 Tips
| Tips | 内容 |
|------|------|
| ER図作成 | A5:SQL Mk-2活用 |
| テーブル定義書出力 | DBFluteのSchemaHTML |

#### 機能開発 Tips
| Tips | 内容 |
|------|------|
| マスタメンテ作成 | 標準パターンに基づく作成手順 |
| 検索一覧画面作成 | 画面雛形の活用 |
| 登録・更新画面作成 | バリデーション込みの実装パターン |
| Excel取込機能作成 | ファイルアップロード+バリデーション |