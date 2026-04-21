# フロントエンド + 共通規約

---

## 1. 共通規約（全レイヤー共通）

### 1.1 プロジェクト概要

| 項目 | 技術スタック |
|------|------------|
| 開発ツール | VSCode（フロントエンド・バックエンド共通） |
| バックエンド言語 | Java |
| フロントエンド言語 | TypeScript (Angular) / JavaScript (AngularJS・旧世代) |
| スタイルシート | SCSS / CSS |
| データベース | Oracle（本番）/ MySQL（推奨開発用） |
| O/Rマッパー | DBFlute |
| Webサーバ | Apache HTTP Server |
| APサーバ | Apache Tomcat（WildFly/JBoss も一部環境で使用） |
| JAX-RS実装 | RESTEasy |
| 帳票エンジン | JasperReports / ExcelCreator（Excel帳票用：ExcelCreator→LibreOffice→PDFBox→PDF.js） |
| ブラウザ | Microsoft Edge |
| クライアントFW | AngularJS（SPA）/ Angular（新世代） |
| モバイル | Flutter/Dart |
| バッチ | JavaベースのCDIバッチ |

#### ソフトウェア機能区分
- **WEB画面**: SPA方式のオンライン業務画面
- **バッチ**: サーバサイドバッチ処理
- **帳票**: JasperReportsベースの帳票出力 / ExcelCreator+LibreOffice+PDFBox+PDF.jsによるExcel帳票出力
- **Excel/CSVインポート・エクスポート**: ファイル入出力機能
- **EDI連携**: 外部システムとのデータ連携（受信・送信・変換）
- **汎用データ入出力**: マスタ・トランザクションデータの一括取込/出力
- **自動印刷**: サーバサイドからの自動帳票印刷

### 1.2 アーキテクチャ基本ルール

```
[ブラウザ] → [Apache HTTP Server (port 80)] → [Tomcat/WildFly (port 8080, AJP 8009)] → [Oracle DB / MySQL]
                  ↓                                   ↓
           静的コンテンツ配信              RESTful API処理
           (HTML/JS/CSS/画像)             (JAX-RS + CDI + DBFlute)
```

- Webサーバ（Apache）→ APサーバ（Tomcat）→ DB（Oracle/MySQL）の**3層構成**を前提とする
- Apache は `mod_proxy_ajp` で `/resources/*` パターンをAPサーバへプロキシ転送する
- 静的リソース（HTML/JS/CSS/画像）はApacheが直接配信する
- クライアントはSPA（Single Page Application）構成とする
- サーバ通信はRESTEasy（JAX-RS）ベースのRESTful APIで行う
- ブラウザ↔サーバ間の通信データは **JSON形式** を使用する
- HTTPセッションは **原則使用しない**（APサーバスケールアウトに悪影響のため）
- CDI（Dependency Injection + Interceptor/AOP）を軸に拡張機能を提供する

#### クライアント側処理方式

| 規定 | 内容 |
|------|------|
| SPA構成 | 画面はAngularJSベースのSPAで制御する |
| 初期ロード | 初期ロードのみJSP（動的）、以降はHTML（静的） |
| JS/CSSロード | 初期ロード時に全てロードし、遅延ロードしない |
| 画面項目初期化 | 拡張部品を使い、サーバのDB管理定義情報で初期化する |
| サーバ通信 | 原則、AngularJSベースの非同期通信のみ |
| データ構造 | `$scope`上のデータ構造はサーバからDBのTable構造を軸に取得・利用する（クライアント側で独自管理しない） |
| 画面遷移 | メニュー画面から各業務画面への遷移はAngularJSのルーティングで制御する |
| モーダル遷移 | 別画面遷移は「モーダル」形式のみ（URLが変わらない） |
| URL直接アクセス | 各業務画面でURLを直接入力してのアクセスは原則考慮しない |
| HTTPセッション | 原則使用しない（APサーバスケールアウトに悪影響のため） |
| データ引き継ぎ | Resource → Dto(JSON) → クライアントの$scopeで管理する |

#### サーバ側クラス分類

```
Resource (JAX-RS エンドポイント)
  ├── @Path("/[サブシステム]/[画面名]")
  ├── @POST / @GET メソッド
  ├── Dto を引数・戻り値として使用
  └── Logic を @Inject で呼び出す

Logic (業務ロジック)
  ├── インタフェースを必ず作成する
  ├── DBFlute BehaviorSelect/BehaviorCommand を使用
  ├── 他のLogicを@Injectで呼び出し可能
  └── Manager（共通処理）を呼び出し可能

Dto (データ転送オブジェクト)
  ├── JSON構造を定義する「容器」
  ├── フィールドのみ保持（ロジック実装禁止）
  └── 画面フィールドとの自動マッピング（双方向バインディング）
```

- 粒度: **1画面 = 1 Resource = 1 Dto**
- LogicはResourceまたは他のLogicから実行する。クライアントから直接実行しない
- DBアクセスは **原則DBFlute経由** で行う
- トランザクション管理はCDI Interceptorによる宣言的トランザクションを使用する

#### データ受け渡し方式

- データ構造はDBテーブル構造に準拠: `Resource → Dto(JSON) → クライアント$scope`
- JSON構造の標準セクション: `status`, `output`, `paging`, `data`（`head`/`body`サブセクション）
- Dto Javaファイルが「容器」としてJSON構造を定義し、Dtoのフィールドが画面フィールドに自動マッピング（双方向バインディング）

```json
{
  "status": { "statusCd": 0, "messageList": [] },
  "output": {
    "data": {
      "head": { /* ヘッダ情報 */ },
      "body": [ /* 明細行データ配列 */ ]
    },
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
- 例: `SlipNoReceiveList`（伝票別入荷一覧）

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

| タイミング | 処理内容 |
|-----------|---------|
| データ取得時 | 排他制御対象テーブルから排他制御カラム4列を取得する |
| データ更新時 | `UPD_OPE_DT` の値を比較し、変更されていればエラー表示して更新を中止する |

- 排他制御テーブルに定義されたテーブルが対象
- VERSION_NO による楽観ロックも併用（DBFlute標準機能）

### 1.6 エラー処理規約

- 不必要に try-catch 句を作成しない
- `catch (Exception e)` をメソッド毎に定型処理として書くのは **禁止**
- 業務エラー以外のエラーはフレームワーク側（RESTEasy）に委譲する
- TryCatch句によるエラーのもみ消しやエラー内容の改竄は **原則禁止**
- 業務独自の例外クラスは作成しない

| 規定 | 内容 |
|------|------|
| システムエラー | ログ出力 ＋ ユーザへメッセージ表示 |
| 業務エラー | ログ出力せず、メッセージのみ表示 |
| もみ消し禁止 | TryCatch句によるエラーのもみ消しやエラー内容の改竄は原則禁止 |

#### エラー制御フロー（新設計）
- JS → Resource → Logic(1つの統合メソッド) → Manager の構造を採用
- StatusCdで段階的に確認ダイアログを制御する
- Logicは1つのメソッドで複数チェックを順次実行し、エラー発生時にManagerでメッセージ登録する
- 旧設計（StatusCd毎にLogicメソッドを分割する方式）は使用しない

#### 入力チェックの実装
- クライアント側: Angular/AngularJS のフォームバリデーション
- サーバ側: Resource/Logic層でバリデーション実施
- 入力チェックエラーはstatusセクションのmessageListに格納して返却する

### 1.7 メッセージ表示基準

| 重要度 | ダイアログ種別 | 用途 |
|--------|--------------|------|
| 高 | エラーダイアログ | 処理継続上、致命的な問題がある場合 |
| 中 | 警告ダイアログ | 処理継続可能だが確認事項がある場合 |
| 低 | 情報ダイアログ | 処理結果を通知する場合 |
| ― | 確認ダイアログ | ユーザに処理の実行要否を確認する場合 |

#### メッセージ表示位置
- 画面上部: 画面全体に対するメッセージ（処理結果通知等）
- 項目横: 特定の入力項目に対するメッセージ（入力チェックエラー等）

#### メッセージ表示タイミング
- 入力チェックエラー: 登録・更新ボタン押下時
- 業務エラー: サーバ処理からの返却時
- 処理完了: 正常完了時に情報ダイアログで通知

### 1.8 グローバル対応規約

#### ブラウザ表示
- フォント: Bootstrap CSSでカスタマイズ可能
- 言語（見出し）: ユーザマスタのカルチャ設定に連動（言語と地域が結合）
- 書式（数値/日付/時間）: AngularJS `$locale` + `angular-dynamic-locale` で動的切替
- タイムゾーン: センターマスタのタイムゾーンで初期化、未設定時はブラウザのタイムゾーンにフォールバック

#### ブラウザ入力
- タイムゾーン: フレームワークでは対応しない。各プログラムでサーバ側でTimestampにタイムゾーン変換する

#### Java（帳票）
- フォント: IPAフォント固定（中国語はNotoSansHans）
- フォントの追加・マッピングは可能だが、マスタ管理による動的切替は不可

### 1.9 セキュリティ規約

- 全てのユーザ入力値に対してバリデーションを実施する
- SQLインジェクション対策: **パラメータバインドを必ず使用する**（リテラル直接埋め込み禁止）
- XSS対策: 出力時にエスケープ処理を行う
- HTTPセッションは原則使用しない（認証トークンベースの管理を推奨）

#### 認証方式

| 方式 | 概要 |
|------|------|
| SAML認証 | IdP（Identity Provider）との連携によるSSO認証 |
| 簡易認証 | 独自のログイン画面によるユーザID/パスワード認証 |
| Google Authenticator | TOTP方式の2要素認証（ログイン後に追加認証コード入力） |

### 1.10 性能規約（画面関連）

#### 性能目標

| 処理種別 | 性能目標 |
|---------|---------|
| 画面描画 | **3秒以内** |

#### 画面描画のポイント
- `ng-repeat` は**1000行**を超えないようにする
- `$watch` の不要な作成を避ける
- `ng-if` と `ng-show`/`ng-hide` の使い分けを検討する（DOMを削除する方がパフォーマンスが良い場合は `ng-if`）
- 大量データの表示にはページングを活用する
- 画像やアイコンの遅延ロードは行わない（初期ロード方針に従う）

#### 検索結果の制約
- 検索結果データは**3000件以下**になるようにする
- 3000件以上の表示が必要な場合は画面仕様を再検討する
- Excel出力・帳票出力は本制約の対象外

---

## 2. AngularJS（JavaScript）コーディング基準（旧世代）

### 2.1 フォルダ・ファイル構成
- JavaScriptファイルは画面単位で作成する
- ファイル名: `[役割名].js`（例: `ReceiveList.js`）

### 2.2 モジュール・ファクトリ・コントローラ定義
- モジュール名: `[システム名].[役割名]`（例: `oneslogiWms.ReceiveList`）
- WebAPI定義用サービス名: `[役割名]Api`（先頭小文字）（例: `receiveListApi`）
- コントローラ名: `[役割名]`（例: `ReceiveList`）

### 2.3 ngDocコメント
- AngularJSのコンポーネントにはngDoc形式でコメントを記述する

### 2.4 WebAPIパス
- 通常処理: `resources/[サブシステム名]/[画面名]/[動詞+名詞]`
  - 例: `resources/receive/receivePlanInput/initNew`
- 共通処理: `resources/[共通処理名]/[対象名]/[動詞+名詞]`
  - 例: `resources/common/product/record`

### 2.5 Modalパス
- Webアプリケーション・ルートからの相対パス表記
- 例: `templateUrl: 'wms/partials/common/ProductSearchSupport.html'`

### 2.6 アップロードパス
- `resources/[サブシステム名]/[画面名]/[動詞+名詞]`
- 例: `resources/master/locationMasterBulkInput/fileUpload`

---

## 3. Angular（TypeScript）コーディング基準（新世代）

> **⚠️ 注意**: 本ドキュメントセット内に **TypeScript/Angular専用のコーディング規約ファイルは確認できませんでした**。
> 現行ドキュメントにはAngularJS（JavaScript）向けのコーディング基準のみ存在します。
> **フロントエンドがAngular（TypeScript/SCSS）に移行済みの場合、TypeScript向けコーディング規約の新規策定が必要です。**

---

## 4. HTML/CSSコーディング基準

### 4.1 HTMLファイル
- ファイル名: `[役割名].html`（例: `ReceiveList.html`）
- Locationパス: Webアプリケーション・ルートからの相対パス
  - 例: `$location.path("wms/receive/ReceivePlanInput");`

#### HTMLコーディング基準（CODE14）
- セマンティックなHTML要素を使用する
- AngularJSディレクティブの命名はケバブケース（例: `ng-model`, `ng-click`）
- id属性は画面内で一意とする

### 4.2 CSS
- ファイル名: `[役割名].css`（例: `common.css`）
- Linkパス: Webアプリケーション・ルートからの相対パス
  - 例: `<link href="base/css/common.css" rel="stylesheet">`
- 定義名: 全て小文字、区切り文字は `-`（ハイフン）
  - 例: `wms-fieldset-well-legend`

#### CSSコーディング基準（CODE15）
- クラス名は全て小文字のケバブケース
- idセレクタよりクラスセレクタを優先する
- インラインスタイルは極力避ける

---

## 5. 画面制御規約

### 5.1 共通部品の活用
- 画面雛形を活用して新規画面を作成する
- 共通部品（検索サポート、ページング等）を積極的に利用する
- カスタムディレクティブの命名規則に従う

---

## 6. Flutter/Dartコーディング基準（モバイル向け）

### 6.1 フォーマット設定
- VSCodeの `.vscode/settings.json` で設定:
  - `dart.lineLength`: 80
  - `editor.formatOnSave`: true
  - `editor.formatOnType`: true
  - `editor.formatOnPaste`: true
  - `source.fixAll`, `source.organizeImports`, `source.addMissingImports`: explicit

### 6.2 高さ・幅・フォント指定
- `flutter_screenutil` を使用して指定する（数値直接指定は避ける）
  - height: `数値.h`、width: `数値.w`、フォント: `数値.sp`
- フォントサイズ最小値: `30.sp`
- 余白・高さ・幅指定はFlutterの自動調整に任せ、むやみに指定しない

### 6.3 色の指定
- `OfeColorScheme` を使用する
  - 例: `color: OfeColorScheme.primaryContainer.backColor`

### 6.4 桁区切りカンマ
- `CultureManager.getNumberFormatDisplay()` と `NumberFormat` を使用する

### 6.5 画面初期化時の変数削除
- `TextEditingController` や `FocusNode` で `addListener` を実施している場合、戻るボタンで戻った際に必ず初期化を行う

### 6.6 全画面の項目名事前取得
- 機能のロジック統括ファイルの初期化処理で `subScreenCdList` に全screenCdを追加して事前取得する

### 6.7 バーコードスキャン
- スキャン時に実行すべき処理を `streamController.stream.listen` 内に追加する

### 6.8 フォーカス制御
- スマホの場合、基本的にフォーカス移動は不要
- キーボードを表示したまま連続入力する箇所のみフォーカス移動を検討する

### 6.9 サーバ（Java）側制約
- `import com.oneslogi.ht.` が入っていないことを確認する（HT向けソースをimportしない）
- `src/com/oneslogi/sd` 以外のファイルは基本的に変更しない（変更が必要な場合はコピーして参照先変更）

### 6.10 継承関連
- 同じ画面やメソッドが複数機能で使われる場合は継承による共通化を検討する
- 共通化する場合、型パラメータを使用する
- 継承を想定しないメソッドはプライベートメソッド（`_` プレフィックス）にする

### 6.11 Flutter命名規約（CODE16）
- クラス名: UpperCamelCase（例: `ReceivePlanScreen`）
- ファイル名: snake_case（例: `receive_plan_screen.dart`）
- 変数・メソッド: lowerCamelCase
- 定数: lowerCamelCase（Dartの慣例に従う）
- プライベートメンバ: `_` プレフィックス

### 6.12 Flutterウィジェット規約（CODE17）
- StatelessWidget / StatefulWidget の使い分けを意識する
- buildメソッドの肥大化を避け、サブウィジェットに分割する
- constコンストラクタを活用してリビルドを最小化する