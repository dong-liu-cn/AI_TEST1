# ONEsLOGI-Web フロントエンド開発 AIルール

## プロジェクト概要

- **システム名**: ONEsLOGI-Web（倉庫管理システム）
- **フロントエンド技術**: AngularJS（クライアント基盤）
- **役割**: 倉庫業務向けWebクライアント。PC画面とHT（ハンディターミナル）画面の2種類が存在する。
- **アーキテクチャ**: フロントエンドとバックエンドの分離構成。REST API経由でサーバと通信する。

---

## 1. ディレクトリ・ファイル構成

- AngularJSのコントローラ、サービス、ディレクティブはそれぞれ役割ごとにフォルダを分けて配置する。
- 画面ごとにコントローラとHTMLテンプレートをセットで管理する。
- 共通コンポーネントは共通フォルダに集約し、各画面から参照する。

---

## 2. 命名規則（ネーミング基準）

- **コントローラ名**: `{機能名}Ctrl`（例: `StockListCtrl`）
- **サービス名**: `{機能名}Service`（例: `StockListService`）
- **ファイル名**: キャメルケースまたはケバブケースで統一する（プロジェクト内の既存ルールに従う）
- **変数・関数名**: 英語で記述し、意味が明確な名前を使用する
- **定数**: 大文字スネークケース（例: `MAX_RECORD_COUNT`）

---

## 3. AngularJS コーディング規約

### 3.1 コントローラ

- コントローラにはビジネスロジックを書かない。ロジックはServiceに委譲する。
- `$scope` の肥大化を防ぐため、必要最小限のプロパティのみ定義する。
- 初期化処理は `init()` 関数にまとめ、コントローラ末尾で呼び出す。

```javascript
// 良い例
angular.module('app').controller('StockListCtrl', function($scope, StockListService) {
    // 初期化
    function init() {
        $scope.searchCondition = {};
        $scope.gridData = [];
    }

    // 検索実行
    $scope.search = function() {
        StockListService.search($scope.searchCondition).then(function(result) {
            $scope.gridData = result.data;
        });
    };

    init();
});
```

### 3.2 テキストの空値判定

AngularJS でテキスト入力値の空値チェックを行う場合は以下のように判定する：

```javascript
// 空値チェック（null、undefined、空文字のいずれも対応）
if (!$scope.value || $scope.value.trim() === '') {
    // 空値の処理
}

// または angular の組み込みチェック
if (angular.isUndefined($scope.value) || $scope.value === null || $scope.value === '') {
    // 空値の処理
}
```

### 3.3 同期処理（Promise チェーン）

AngularJS での非同期処理を同期的に実行する場合は Promise チェーンを使用する：

```javascript
// 同期処理のサンプル（順番に実行したい場合）
ServiceA.process()
    .then(function(resultA) {
        return ServiceB.process(resultA);
    })
    .then(function(resultB) {
        return ServiceC.process(resultB);
    })
    .then(function(resultC) {
        $scope.result = resultC;
    })
    .catch(function(error) {
        // エラーハンドリング
        console.error(error);
    });
```

### 3.4 明細グリッド実装

- 明細グリッドに何も表示されない場合、データバインディングのタイミングを確認する（`$scope.$apply()` の必要性を検討）。
- グリッドの初期化は画面ロード完了後（`$timeout` や `$scope.$on('$viewContentLoaded', ...)` 等）に行う。
- 明細行選択時のイベント処理：

```javascript
// 明細行選択イベントの実装例
$scope.onRowSelected = function(row) {
    $scope.selectedRow = row;
    // 選択時の処理を実行
    processSelectedRow(row);
};
```

### 3.5 検索条件のアコーディオン制御

検索条件パネルのアコーディオンを任意のタイミングで閉じる場合：

```javascript
// アコーディオンを閉じる
$scope.closeSearchCondition = function() {
    $scope.isSearchConditionOpen = false;
    // または UI コンポーネントの API を使用
};

// 検索実行時に自動的に閉じる
$scope.search = function() {
    $scope.closeSearchCondition();
    // 検索処理...
};
```

---

## 4. メッセージ表示基準

クライアント機能でのメッセージ表示は以下の基準に従う：

| 種別 | 用途 | 表示方式 |
|------|------|----------|
| エラー | 処理続行不可のエラー | ダイアログ表示 |
| 警告 | 処理続行可能だが注意が必要 | ダイアログ表示（確認あり）|
| 情報 | 処理完了通知など | トースト/インライン表示 |
| 入力エラー | バリデーションエラー | 項目近傍にインライン表示 |

- エラーメッセージはメッセージIDで管理し、ハードコードしない。
- サーバからのエラーレスポンスは共通のエラーハンドリング処理で統一的に処理する。

---

## 5. 共通エラー制御

サーバとの通信エラーは共通ロジックで処理する：

```javascript
// HTTP エラーのインターセプタ（共通設定）
// - 401: 未認証 → ログイン画面へリダイレクト
// - 403: 権限なし → エラーメッセージ表示
// - 500: サーバエラー → 共通エラーダイアログ表示
// - その他: 個別にハンドリング
```

- 個別の API 呼び出しでは、共通ハンドラで処理されない業務エラーのみを個別に処理する。

---

## 6. デバッグ手順

AngularJS のデバッグを行う際は以下の手順で実施：

1. ブラウザの開発者ツール（F12）を開く
2. Console タブでエラー・警告を確認する
3. Network タブで API 通信の内容（リクエスト/レスポンス）を確認する
4. AngularJS の `$scope` 状態を確認する場合は、要素を選択して Console で `angular.element($0).scope()` を実行する
5. ブレークポイントは Sources タブで設定する

---

## 7. HT（ハンディターミナル）画面固有ルール

HT画面（ハンディターミナル向け）を実装する際の注意事項：

- **initscreen の設定を必ず行うこと**。設定していない場合、異常終了する。
- HT 画面は PC 画面とは異なるテンプレートを使用する。
- 新規機能作成時は `initscreen` の設定漏れに特に注意する。
- 入力文字制御を変更する場合は `b_func`、`b_arg` テーブルへの登録も必要。

---

## 8. パフォーマンス規約

- ループ内で DOM 操作や API 呼び出しを行わない。
- `$watch` の多用を避ける。特に deep watch（`true` フラグ）は最小限にする。
- 一覧データは必要な件数のみ取得し、大量データの一括取得は避ける。
- ページネーションまたは無限スクロールを適切に実装する。

---

## 9. セキュリティ

- XSS 対策として、ユーザ入力値を HTML として直接バインドしない（`ng-bind-html` は sanitize 済みのデータのみ使用）。
- 認証トークンは localStorage または sessionStorage で安全に管理する。
- API 通信は HTTPS を使用する。

---

## 10. コードレビューチェックリスト

実装完了時に以下を確認すること：

- [ ] 命名規則に従っているか
- [ ] 空値チェックが適切に実装されているか
- [ ] エラーハンドリングが実装されているか
- [ ] HT画面の場合、`initscreen` が設定されているか
- [ ] パフォーマンスに問題がないか（ループ内 API 呼び出し等がないか）
- [ ] メッセージはメッセージID経由で表示しているか
- [ ] `$scope` に不要なプロパティを追加していないか