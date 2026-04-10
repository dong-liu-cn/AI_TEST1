---
name: design-analyzer
description: 解析後の設計データを分析し、設計パターン、潜在的な問題、最適化提案を識別し、設計判断記録を生成します。アーキテクチャ設計レビューと技術方針策定に適しています。
---

# 業務機能設計分析スキル

## 概要
excel-parseスキルで抽出された構造化設計データを分析し、ソースコードレベルの設計品質を評価するスキルです。
Javaクラス構成、JavaScript画面制御、DTO設計、DB操作、共通機能利用の観点から分析を行います。

## 分析観点

### 1. ソースコード構成分析

#### Java層（サーバサイド）
- **Resourceクラス分析**：`*Resource.java` のAPI定義、メソッド構成、パラメータ設計
- **Logicクラス分析**：`*Logic.java` の業務ロジック構成、トランザクション境界
- **DTO分析**：画面用DTO、検索条件DTO、API間受け渡しDTOの構成
- **DB操作分析**：DB Flute / 外出しSQL の使い分け、検索条件の妥当性

#### JavaScript層（フロントエンド）
- **画面制御分析**：初期表示処理、活性/非活性制御の網羅性
- **イベントハンドラ分析**：ボタン押下、ロストフォーカス、モーダル連携の整合性
- **バリデーション分析**：入力チェックの網羅性、エラーメッセージの統一性

#### HTML/CSS層（画面）
- **画面レイアウト分析**：ヘッダ/明細/フッタの構成、入力項目の配置
- **スタイル分析**：共通CSSの適用、レスポンシブ対応

### 2. 処理フロー分析
- **処理間の関連分析**：後続処理の追跡、処理呼び出しチェーン
- **エラーハンドリング分析**：異常系処理の網羅性、メッセージ定義の統一性
- **画面モード別分析**：新規/更新/参照モードごとの処理差分
- **ステータス遷移分析**：業務ステータスに応じた画面制御・処理分岐の妥当性

### 3. テーブル設計分析
- **マッピング整合性**：画面項目とDBカラムの対応漏れチェック
- **予定/実績の整合性**：予定項目と実績項目に同値セットが必要な項目の確認
- **登録/更新の網羅性**：必須カラムの設定漏れ、デフォルト値の妥当性
- **テーブル間結合**：結合条件の妥当性、外部キー整合性

### 4. 共通機能利用分析
- **共通コンポーネント参照**：`owsCommon`系関数の利用パターン
- **マスタデータ取得**：区分値マスタ、コードマスタの取得方法の統一性
- **採番ロジック**：番号採番（`numberingLogic.getNumbering`）の利用パターン
- **認証/権限**：ログイン情報の参照、参照権限マスタの利用

### 5. クラス一覧の導出
解析データから以下のクラス一覧を自動導出する：

| 分類 | クラスID例 | 役割 |
|------|-----------|------|
| JavaScript | `{FunctionName}.js` | 画面制御（イベントハンドラ、画面遷移） |
| Resource | `{FunctionName}Resource.java` | REST API エンドポイント |
| 検索Logic | `{FunctionName}SelectLogic.java` | データ検索処理 |
| 登録Logic | `{FunctionName}InsertLogic.java` | データ登録処理 |
| 更新Logic | `{FunctionName}UpdateLogic.java` | データ更新処理 |
| 入力チェックLogic | `{FunctionName}Logic.java` | 入力チェック処理 |
| 画面DTO | `{FunctionName}Dto` | 画面データ受け渡し用 |
| 検索条件DTO | `{SearchName}Dto` | 検索条件用 |
| HTML | `{functionName}.html` | 画面テンプレート |
| CSS | `{functionName}.css` | 画面スタイル |

### 6. DTO構造の導出
処理フローとテーブル項目マッピングからDTO構造を導出する：
- 画面DTO：ヘッダ部 + 明細部（リスト）の構成
- 各フィールドの型、必須/任意、バリデーション条件

## 出力形式

```markdown
## 設計分析レポート

### 1. ソースコード構成サマリ

| 分類 | ファイル数 | クラス一覧 |
|------|----------|-----------|
| JavaScript | 1 | RentalOrderInput.js |
| Resource | 1 | RentalOrderInputResource.java |
| Logic | 4 | SelectLogic, InsertLogic, UpdateLogic, InputCheckLogic |
| DTO | 2 | RentalOrderInputDto, PlanStockDto |

### 2. 処理フロー構成

| 処理No | 処理名 | クラス | メソッド | 層 | トリガー |
|--------|-------|--------|---------|-----|---------|
| 1 | js初期処理 | RentalOrderInput.js | initScreen | Frontend | 画面起動 |
| 2 | Resource初期処理（新規） | RentalOrderInputResource.java | initNew | Backend | 処理1から呼出 |

### 3. 潜在的な問題

| 重大度 | 対象 | 問題説明 | 提案 |
|--------|------|---------|------|
| 高 | 処理22 | 入力チェックにトランザクション境界が不明確 | Logic内でのトランザクション管理を明記 |

### 4. DTO構造

#### RentalOrderInputDto
| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| headerDto | RentalOrderInputHeaderDto | ○ | ヘッダ情報 |
| detailList | List<RentalOrderInputDetailDto> | ○ | 明細情報リスト |

### 5. 共通機能利用一覧

| 共通機能名 | 利用箇所 | 用途 |
|-----------|---------|------|
| owsCommon.getDataCacheable | 処理1 | 区分値マスタ取得 |
| numberingLogic.getNumbering | 処理23 | レンタルオーダー番号採番 |

### 6. 設計判断記録

| 判断ポイント | 判断 | 理由 |
|------------|------|------|
| DB操作方法 | DB Flute | フレームワーク標準 |
| 予定在庫算出 | 外出しSQL | 複雑なサブクエリが必要 |
```

## 依存スキル
- excel-parse（入力データ元）