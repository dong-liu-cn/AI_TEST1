---
name: excel-parse
description: Excelファイル内の基本設計データを解析し、処理フロー、クラス/メソッド定義、画面項目、テーブル項目マッピング、業務ルールなどを抽出します。WMS系業務機能設計書の解析に適しています。
---

# Excel業務機能設計書解析スキル

## 概要
WMS（倉庫管理システム）等の業務機能設計書（Excel）を解析し、ソースコードレベルの詳細設計に必要な情報を構造化データとして抽出するスキルです。

## 解析対象

### 1. 基本情報
- **業務ID/機能ID**：業務識別子、機能識別子
- **業務名称/機能名称**：業務名、機能名
- **作成者/審査者/承認者**：担当者情報
- **変更履歴**：変更年月日、変更シート、変更内容、種別

### 2. 処理詳細設計
- **処理一覧**：処理番号、処理名称、トリガー（初期表示、ボタン押下、ロストフォーカス等）
- **クラス/メソッド定義**：
  - クラスID（例：`RentalOrderInput.js`、`RentalOrderInputResource.java`）
  - クラス名（日本語名称）
  - メソッドID（例：`initScreen`、`register`）
  - メソッド名（日本語名称）
- **パラメータ定義**：入出力パラメータ、設定値、備考
- **処理フロー**：処理No、処理種別（処理/判定/繰り返し）、処理内容、後続処理、備考

### 3. 画面項目定義
- **ヘッダ部項目**：項目名、入力種別（テキスト/ドロップダウン/ボタン等）、取得元
- **明細部項目**：項目名、入力種別、取得元、活性/非活性条件
- **フッタ部項目**：ボタン定義、活性/非活性条件

### 4. テーブル項目マッピング
- **データ取得マッピング**：画面項目名 ↔ テーブル名（物理名）↔ カラム名（物理名）
- **データ登録マッピング**：カラム名 ↔ 設定値 ↔ 備考
- **データ更新マッピング**：カラム名 ↔ 設定値 ↔ 更新条件

### 5. DB操作情報
- **検索条件**：メインテーブル、結合テーブル、取得項目、検索条件、並び順
- **登録/更新テーブル**：対象テーブル物理名、更新方法（DB Flute等）
- **SQL参考イメージ**：外出しSQL、サブクエリ構成

### 6. 外部連携情報
- **モーダル画面連携**：呼び出し元、パラメータ受け渡し、戻り値
- **API呼び出し**：WebAPI名、パラメータ、レスポンス
- **共通機能参照**：共通コンポーネント名、用途

## 解析手順

1. Excelの全シートを読み込み、シート構成を把握
2. 「基本情報」シートから業務ID、機能ID、担当者情報を抽出
3. 「変更履歴」シートから履歴一覧を抽出
4. 「処理詳細設計」シートから以下を抽出：
   - 各処理のクラスID、メソッドID、パラメータ、処理フロー
   - JavaScript処理（画面制御）とJava処理（サーバサイド）を区別
5. 「画面設計」シートから画面項目定義を抽出
6. 「テーブル項目マッピング」シートからDB操作情報を抽出
7. 構造化JSONデータとして出力

## 出力形式

```json
{
  "basicInfo": {
    "businessId": "01",
    "businessName": "入荷管理",
    "functionId": "ZWRS20",
    "functionName": "レンタルオーダー入力",
    "authors": { "creator": "酒井", "reviewer": "中川", "approver": "松本" }
  },
  "changeHistory": [
    { "no": 1, "date": "2022-08-24", "sheet": "-", "content": "新規作成", "type": "新規", "author": "酒井" }
  ],
  "processes": [
    {
      "processNo": 1,
      "processName": "js初期処理",
      "trigger": "画面起動時",
      "classId": "RentalOrderInput.js",
      "className": "レンタルオーダー入力.画面起動時",
      "methodId": "initScreen",
      "methodName": "画面初期化",
      "layer": "frontend",
      "parameters": [
        { "no": 1, "name": "画面モード", "value": "Create(新規)/Update(更新)", "remarks": "" }
      ],
      "flow": [
        { "no": 1, "type": "処理", "content": "拠点分類の候補値を取得", "nextProcess": "", "remarks": "共通機能" }
      ]
    }
  ],
  "screenItems": {
    "header": [
      { "itemName": "拠点分類", "inputType": "dropdown", "source": "区分値マスタ", "remarks": "" }
    ],
    "detail": [
      { "itemName": "品目CD", "inputType": "text+button", "source": "入荷予定ボディ", "remarks": "" }
    ],
    "footer": [
      { "itemName": "行追加", "type": "button", "remarks": "" }
    ]
  },
  "tableMapping": {
    "dataRetrieval": [
      { "screenItem": "品目名称", "table": "M_PRODUCT", "column": "商品名称", "remarks": "" }
    ],
    "dataInsert": {
      "T_RECEIVE_PLAN_H": [
        { "column": "入荷予定ヘッダID", "value": "自動採番", "remarks": "" }
      ]
    },
    "dataUpdate": {
      "T_RECEIVE_PLAN_H": [
        { "column": "備考", "value": "画面入力.その他", "remarks": "" }
      ]
    }
  },
  "externalIntegration": {
    "modals": [
      { "name": "納品先検索", "trigger": "引取先デポボタン押下", "params": ["clientId", "customerCd"] }
    ],
    "apis": [
      { "name": "予定在庫取得API", "endpoint": "resources/common/stock/plan", "params": [] }
    ],
    "commonFunctions": [
      { "name": "owsCommon.getDataCacheable", "usage": "区分値マスタ取得" }
    ]
  }
}
```

## 対応するExcelシート構造パターン

### パターン1：WMS業務機能設計書
- シート「基本情報」「変更履歴」「処理詳細設計」「テーブル項目マッピング」

### パターン2：画面設計書
- シート「画面項目定義」「画面遷移」「イベント定義」

### パターン3：統合設計書
- 上記パターン1+2の複合形式

## 注意事項
- Excel内のセル結合がある場合は、結合セルの値を上位セルから継承する
- 処理フローの「後続処理」欄から処理間の関連を追跡する
- クラスIDのファイル拡張子（`.js`/`.java`）からフロントエンド/バックエンドを判別する
- テーブル名は物理名（英字）と論理名（日本語）の両方を抽出する