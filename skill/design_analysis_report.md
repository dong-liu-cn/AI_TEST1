# 設計分析レポート：在庫一覧（U-IM-020-P）

## 1. ソースコード構成サマリ

### クラス一覧

| No | 分類 | クラスID | クラス名 | 役割 |
|----|------|---------|---------|------|
| 1 | JavaScript | `StockList.js` | 在庫一覧.画面制御 | 画面イベント制御（検索、ページング、画面遷移、リンク処理） |
| 2 | Resource | `StockListResource.java` | 在庫一覧リソース | REST APIエンドポイント（検索、Excel出力、在庫日報出力） |
| 3 | 検索Logic | `StockListSelectLogic.java` | 在庫一覧検索ロジック | 在庫データ検索処理（通常/内訳モード） |
| 4 | チェックLogic | `StockListLogic.java` | 在庫一覧入力チェック | 検索条件バリデーション |
| 5 | Excel出力Logic | `StockListExcelLogic.java` | 在庫一覧Excel出力ロジック | 検索結果Excel出力処理 |
| 6 | 在庫日報Logic | `StockDailyReportLogic.java` | 在庫日報出力ロジック | 在庫日報Excel出力処理 |

### DTO一覧

| No | DTO名 | 用途 | 主要フィールド |
|----|-------|------|---------------|
| 1 | `StockListDto` | 画面データ受け渡し | 検索条件DTO + 集計DTO + 明細DTOリスト |
| 2 | `StockListSearchConditionDto` | 検索条件用 | 検索モード, 組織CD, 取引先CD, 品目CD, 基準日等 |
| 3 | `StockListSummaryDto` | 集計情報用 | 実績済在庫数, 出庫可能数, 予定在庫数 |
| 4 | `StockListDetailNormalDto` | 通常明細用 | 組織CD, 取引先CD, 品目CD, 各在庫数, 在庫優先表示 |
| 5 | `StockListDetailBreakdownDto` | 内訳明細用 | 通常明細 + ランク別数量（未選別～基準外） |
| 6 | `StockDailyReportDto` | 在庫日報出力用 | 取引先CD, 選別数集計基準日 |

### HTML/CSS

| No | ファイル名 | 用途 |
|----|-----------|------|
| 1 | `stockList.html` | 在庫一覧画面テンプレート |
| 2 | `stockList.css` | 在庫一覧画面スタイル |

## 2. 処理フロー構成

| 処理No | 処理名 | クラス | メソッド | 層 | トリガー |
|--------|-------|--------|---------|-----|---------|
| 1 | JS初期表示処理 | `StockList.js` | `initScreen` | Frontend | 画面起動 |
| 2 | Resource初期処理 | `StockListResource.java` | `init` | Backend | 処理1から呼出 |
| 3 | 検索処理（JS） | `StockList.js` | `onClickSearch` | Frontend | 検索ボタン押下 |
| 4 | 検索条件チェック | `StockListLogic.java` | `validateSearchCondition` | Backend | 処理3から呼出 |
| 5 | 検索処理（Resource） | `StockListResource.java` | `search` | Backend | 処理3から呼出 |
| 6 | 在庫データ検索 | `StockListSelectLogic.java` | `selectStockList` | Backend | 処理5から呼出 |
| 7 | Excel出力処理（JS） | `StockList.js` | `onClickExcel` | Frontend | Excelボタン押下 |
| 8 | Excel出力処理（Resource） | `StockListResource.java` | `exportExcel` | Backend | 処理7から呼出 |
| 9 | Excel出力処理（Logic） | `StockListExcelLogic.java` | `exportExcel` | Backend | 処理8から呼出 |
| 10 | ページング処理 | `StockList.js` | `onClickPaging` | Frontend | ページングボタン押下 |
| 11 | 在庫詳細遷移処理 | `StockList.js` | `onClickSelect` | Frontend | 選択ボタン押下 |
| 12 | 在庫振替遷移処理 | `StockList.js` | `onClickTransfer` | Frontend | 振替ボタン押下 |
| 13 | 取引先コードリンク処理 | `StockList.js` | `onClickCustomerLink` | Frontend | 取引先コードリンク押下 |
| 14 | 品目コードリンク処理 | `StockList.js` | `onClickProductLink` | Frontend | 品目コードリンク押下 |
| 15 | ロストフォーカス処理（組織） | `StockList.js` | `onBlurOrganization` | Frontend | 組織コード ロストフォーカス |
| 16 | ロストフォーカス処理（在庫グループ） | `StockList.js` | `onBlurStockGroup` | Frontend | 在庫グループコード ロストフォーカス |
| 17 | ロストフォーカス処理（取引先） | `StockList.js` | `onBlurCustomer` | Frontend | 取引先コード ロストフォーカス |
| 18 | ロストフォーカス処理（品目） | `StockList.js` | `onBlurProduct` | Frontend | 品目コード ロストフォーカス |
| 19 | 在庫日報Excel出力（JS） | `StockList.js` | `onClickDailyReport` | Frontend | 在庫日報Excel出力ボタン押下 |
| 20 | 在庫日報Excel出力（Resource） | `StockListResource.java` | `exportDailyReport` | Backend | 処理19から呼出 |
| 21 | 在庫日報Excel出力（Logic） | `StockDailyReportLogic.java` | `exportDailyReport` | Backend | 処理20から呼出 |

## 3. 潜在的な問題

| 重大度 | 対象 | 問題説明 | 提案 |
|--------|------|---------|------|
| 中 | 検索処理 | 品目コード（単一）と品目コード（複数）のAND/OR組み合わせロジックが複雑。品目コード入力時に品目コード（複数）を無視する仕様のため、フロントエンド側で排他制御が必要 | JSで品目コード入力時に品目コード（複数）フィールドを非活性化するUI制御を追加 |
| 中 | 在庫計算 | 実績済在庫数の算出が「現在在庫 - 基準日翌日～業務日付の入出庫実績」と複雑なサブクエリが必要。パフォーマンスリスクあり | 在庫スナップショットテーブルの利用を検討、またはインデックス最適化 |
| 低 | 画面状態 | 通常モードで「未承認の実績を含む」がチェックなし固定、内訳モードで入力可能。モード切替時の値リセットが未定義 | モード切替時にチェックボックスの値をリセットするロジックを明記 |
| 低 | 在庫日報 | 在庫日報Excel出力は内訳モードのみ表示だが、必須チェック（取引先コード・選別数集計基準日）がモード固有の条件と組み合わさる | 在庫日報ボタン表示条件と必須チェックのモード依存を明記 |
| 情報 | 優先表示 | 優先表示組織（1300、1303）がコードマスタで管理されるが、ハードコーディングのリスクあり | コードマスタから動的取得する実装を確認 |
| 情報 | 画面遷移 | レンタルオーダーからの遷移時、出庫元コードの有無で組織コード/取引先コードの引き継ぎロジックが分岐 | 遷移パラメータの組み合わせパターンのテストケースを作成 |

## 4. DTO構造

### StockListDto（画面メインDTO）
| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| searchCondition | StockListSearchConditionDto | ○ | 検索条件 |
| summary | StockListSummaryDto | - | 集計情報 |
| detailNormalList | List&lt;StockListDetailNormalDto&gt; | - | 通常明細リスト |
| detailBreakdownList | List&lt;StockListDetailBreakdownDto&gt; | - | 内訳明細リスト |

### StockListSearchConditionDto（検索条件DTO）
| フィールド | 型 | 必須 | 画面項目 |
|-----------|---|------|---------|
| searchMode | String | ○ | 検索モード（通常/内訳） |
| organizationCd | String | - | 組織コード |
| stockGroupCd | String | - | 在庫グループコード |
| customerType | String | ○ | 取引先種別（デポ/仕入先） |
| searchRange | String | - | 検索範囲（全社/国内/海外） |
| customerCd | String | - | 取引先コード |
| customerName | String | - | 取引先名（検索条件） |
| productCd | String | - | 品目コード |
| stockStatus | String | - | 在庫状況 |
| includeUnapproved | Boolean | - | 未承認の実績を含む |
| productCdMulti1 | String | - | 品目コード（複数）1 |
| productCdMulti2 | String | - | 品目コード（複数）2 |
| productCdMulti3 | String | - | 品目コード（複数）3 |
| productCdMulti4 | String | - | 品目コード（複数）4 |
| actualStockBaseDate | Date | ○ | 実績済在庫基準日 |
| plannedStockBaseDate | Date | ○ | 予定在庫基準日 |
| sortingAggregationType | String | - | 選別数集計基準日 |
| specifiedDate | Date | △ | 指定年月日 |
| productType | String | - | 区分（木・プラ・鉄）品目種別 |

### StockListSummaryDto（集計DTO）
| フィールド | 型 | 説明 |
|-----------|---|------|
| actualStockQty | BigDecimal | 実績済在庫数 |
| availableStockQty | BigDecimal | 出庫可能数 |
| plannedStockQty | BigDecimal | 予定在庫数 |

### StockListDetailNormalDto（通常明細DTO）
| フィールド | 型 | 画面項目 | DBカラム |
|-----------|---|---------|---------|
| organizationCd | String | 組織コード | 取引先基本マスタ.主管組織コード |
| organizationName | String | 組織名 | 取引先_共通.取引先名 |
| customerCd | String | 取引先コード | 現在在庫.取引先コード |
| customerName | String | 取引先名 | 取引先会計.予備項目08 |
| productCd | String | 品目コード | 現在在庫.品目コード |
| productName | String | 品目名 | 品目マスタ.品目名 |
| productType | String | 品目種別 | 品目マスタ.区分（木・プラ・鉄） |
| actualStockQty | BigDecimal | 実績済在庫数 | 計算値 |
| availableStockQty | BigDecimal | 出庫可能数 | 計算値 |
| plannedStockQty | BigDecimal | 予定在庫数 | 計算値 |
| priorityDisplay | String | 在庫優先表示 | 判定値（○/空白） |

### StockListDetailBreakdownDto（内訳明細DTO）
| フィールド | 型 | 画面項目 | 説明 |
|-----------|---|---------|------|
| （StockListDetailNormalDtoを継承） | | | 通常明細の全フィールド |
| unsortedQty | BigDecimal | 未選別 | ランク「未選別」の基準日在庫＋未承認入出庫 |
| generalQty | BigDecimal | 一般品 | ランク「一般品」の基準日在庫＋未承認入出庫 |
| limitedQty | BigDecimal | 限定品 | ランク「限定品」の基準日在庫＋未承認入出庫 |
| maintenanceQty | BigDecimal | メンテ待ち | ランク「メンテ待ち」の基準日在庫＋未承認入出庫 |
| dryingQty | BigDecimal | 乾燥待ち | ランク「乾燥待ち」の基準日在庫＋未承認入出庫 |
| otherQty | BigDecimal | その他 | ランク「その他」の基準日在庫＋未承認入出庫 |
| holdQty | BigDecimal | 保留 | ランク「保留」の基準日在庫＋未承認入出庫 |
| outOfStandardQty | BigDecimal | 基準外 | ランク「基準外」の基準日在庫＋未承認入出庫 |

## 5. 共通機能利用一覧

| No | 共通機能名 | 利用箇所（処理No） | 用途 |
|----|-----------|-------------------|------|
| 1 | 組織コード検索モーダル | 処理15 / 検索ボタン（組織） | 組織コード検索・選択 |
| 2 | 在庫グループ検索モーダル | 処理16 / 検索ボタン（在庫グループ） | 在庫グループ検索・選択 |
| 3 | 取引先検索モーダル | 処理17 / 検索ボタン（デポ/仕入先） | 取引先検索・選択 |
| 4 | 品目検索モーダル | 処理18 / 検索ボタン（品目） | 品目検索・選択 |
| 5 | コードマスタ取得 | 処理1, 処理6 | 優先表示組織の取得 |
| 6 | ページング共通コンポーネント | 処理10 | 一覧のページ切替 |
| 7 | Excel出力共通コンポーネント | 処理9 | 検索結果のExcelダウンロード |
| 8 | カレンダーコンポーネント | ヘッダ部 | 日付入力支援（注1） |
| 9 | ロストフォーカス入力チェック | 処理15-18 | 入力タイプチェック（注2） |

## 6. 設計判断記録

| 判断ポイント | 判断 | 理由 |
|------------|------|------|
| 検索モード切替 | 同一画面でモード切替（通常/内訳） | 業務要件として同一画面で2つの表示モードを提供 |
| 在庫数算出方法 | 外出しSQL（サブクエリ） | 基準日時点在庫の逆算が必要であり、複雑なサブクエリが不可避 |
| 優先表示組織 | コードマスタから動的取得 | ハードコーディング回避、運用時の変更容易性確保 |
| 品目コード検索 | AND/OR混在ロジック | 業務要件として単一/複数品目検索の使い分けが必要 |
| 在庫日報出力 | 会社コード=100、ロケール=ja固定 | Webデポとの互換性維持 |
| DB操作方法 | DB Flute + 外出しSQL | 単純な取得はDB Flute、複雑な在庫計算は外出しSQL |
| 画面遷移パラメータ | 遷移元ごとに異なる初期値設定 | レンタルオーダー/移動オーダー/紛失オーダーからの遷移パターンに対応 |