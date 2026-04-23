# ONEsLOGI-Web バックエンド開発 AIルール

## プロジェクト概要

- **システム名**: ONEsLOGI-Web（倉庫管理システム）
- **バックエンド技術**: Java / Spring Framework / DBFlute（ORM）
- **DBサポート**: MySQL / Oracle
- **アプリケーションサーバ**: Apache Tomcat
- **役割**: 倉庫業務向けWebシステムのサーバサイド処理。REST APIを提供してフロントエンド（AngularJS）と連携する。

---

## 1. アーキテクチャ概要

### レイヤー構成

```
Controller（API エンドポイント）
    ↓
Service（ビジネスロジック）
    ↓
Behavior / Mapper（DBFlute / MyBatis）
    ↓
DB（MySQL / Oracle）
```

- **Controller**: リクエスト受付・レスポンス返却のみ。ビジネスロジックを書かない。
- **Service**: ビジネスロジックの中核。トランザクション境界もここで管理される。
- **Behavior**: DBFlute の自動生成クラス。CRUD 操作を担当。
- **外だし SQL**: 複雑なクエリは SQL ファイルに外部化する（DBFlute の OutsideSql 機能）。

---

## 2. 命名規則（ネーミング基準）

### クラス名

| 種別 | 命名規則 | 例 |
|------|----------|-----|
| Controller | `{機能名}Controller` | `StockListController` |
| Service | `{機能名}Service` | `StockListService` |
| DTO（リクエスト） | `{機能名}Form` または `{機能名}RequestDto` | `StockListForm` |
| DTO（レスポンス） | `{機能名}ResultDto` または `{機能名}ResponseDto` | `StockListResultDto` |
| SQL ファイル | `{機能名}_{用途}.sql` | `StockList_selectList.sql` |

### メソッド名

| 操作 | 命名規則 | 例 |
|------|----------|-----|
| 一覧取得 | `selectList` / `findList` | `selectStockList()` |
| 1件取得 | `selectOne` / `findOne` | `selectStockOne()` |
| 登録 | `insert` | `insertStock()` |
| 更新 | `update` | `updateStock()` |
| 削除 | `delete` | `deleteStock()` |

### 変数・フィールド名

- キャメルケースで記述する。
- boolean 型は `is` / `has` プレフィックスを付ける（例: `isValid`, `hasError`）。
- 定数は大文字スネークケース（例: `MAX_COUNT`, `DEFAULT_PAGE_SIZE`）。

---

## 3. Spring トランザクション管理

### ロールバック条件（重要）

```
■ Rollback 発生条件
・RuntimeException のサブクラスが throw された場合 → ロールバックされる
・Exception のサブクラス（検査例外）が throw された場合 → ロールバックされない

■ 明示的にロールバックさせたい場合
RuntimeException（またはそのサブクラス）を throw する。
```

```java
// ロールバックを発生させる場合（RuntimeException を使用）
throw new RuntimeException("業務エラーが発生しました");

// 独自の RuntimeException サブクラスを使用する場合
throw new BizRuntimeException("MSG_0001");

// 検査例外（Exception）はロールバックされないため注意
// throw new Exception("これはロールバックされない");  // NG
```

### `@Transactional` の仕様

- `@Transactional` アノテーションは **Service クラスの public メソッドに AOP で自動付与** される（基盤の設定による）。
- 個別に `@Transactional` を付与する必要はない（基盤設定が自動適用）。
- ただし、トランザクション境界を明示したい場合や特殊な設定が必要な場合は個別に付与する。

```java
// Service クラスの public メソッドには自動的に @Transactional が適用される
@Service
public class StockUpdateService {

    public void updateStock(StockUpdateForm form) {
        // このメソッドは自動的にトランザクション管理される
        // RuntimeException が発生するとロールバックされる
        stockBhv.update(entity);
    }
}
```

---

## 4. DBFlute 実装規約

### 4.1 外だし SQL（OutsideSql）の基本方針

- 検索系の複雑な SQL は外だし SQL（`.sql` ファイル）で実装する。
- 外だし SQL ファイルはメンテナンス性を重視してシンプルに保つ。

### 4.2 COUNT SQL の最適化（必須）

件数取得用の SQL では、**件数取得に必要なテーブル・カラムのみに限定する**。

```sql
-- NG: 全カラムを SELECT している COUNT SQL（パフォーマンス劣化）
SELECT COUNT(*)
FROM   STOCK_MAST S
INNER JOIN ITEM_MAST I ON S.ITEM_ID = I.ITEM_ID
INNER JOIN LOCATION_MAST L ON S.LOCATION_ID = L.LOCATION_ID  -- 件数取得に不要
WHERE  S.WAREHOUSE_ID = /*warehouseId*/'001'

-- OK: 件数取得に必要なテーブル・カラムのみに限定
SELECT COUNT(*)
FROM   STOCK_MAST S
WHERE  S.WAREHOUSE_ID = /*warehouseId*/'001'
```

- ORDER BY 句は COUNT SQL に不要。必ず除外する。
- 不要な JOIN は件数取得時に除外できないか検討する。

### 4.3 SQL が複雑な場合は Java 側に処理を移す

外だし SQL が複雑になりすぎる場合（条件によって JOIN テーブルが変わる等）は、**SQL を分割して Java 側でループ処理**する方針を取る。

```java
// 変更前：1本の複雑な SQL → 保守性が低い
// List<ResultDto> resultList = mapper.selectComplexQuery(condition);

// 変更後：SQL を分割して Java 側でループ処理 → 保守性が高い
List<String> keyList = getKeyList(condition);
List<ResultDto> mergedResult = new ArrayList<>();

for (String key : keyList) {
    List<ResultDto> resultList = mapper.selectByKey(key);
    mergedResult.addAll(resultList);
}
```

### 4.4 抽出系 SQL の実行回数を最小化する

- ループ内で抽出系 SQL を発行する**N+1 問題**を避ける。
- 必要なデータは可能な限り1回の SQL で取得する。
- ループ前にまとめてデータを取得し、Java 側で振り分ける。

```java
// NG: N+1 問題（ループ内で SQL 実行）
for (StockEntity stock : stockList) {
    ItemEntity item = itemBhv.selectByPK(stock.getItemId()); // ループ内でSQL発行 → NG
}

// OK: まとめて取得してから処理
List<String> itemIdList = stockList.stream()
    .map(StockEntity::getItemId)
    .collect(Collectors.toList());
List<ItemEntity> itemList = itemBhv.selectList(cb -> {
    cb.query().setItemId_InScope(itemIdList); // IN句でまとめて取得
});
Map<String, ItemEntity> itemMap = itemList.stream()
    .collect(Collectors.toMap(ItemEntity::getItemId, e -> e));

for (StockEntity stock : stockList) {
    ItemEntity item = itemMap.get(stock.getItemId()); // Map から取得（SQL 不要）
}
```

### 4.5 親子テーブルの登録はバルクインサートを使用する

親子関係のテーブルを登録する場合、**親テーブルもバルクインサートで実装する**。

```java
// NG: 1件ずつ INSERT（大量データの場合にパフォーマンス劣化）
for (ParentEntity parent : parentList) {
    parentBhv.insert(parent); // 1件ずつ → NG
}

// OK: バルクインサート（まとめて INSERT）
parentBhv.batchInsert(parentList); // バルクインサート → OK

// 子テーブルも同様にバルクインサート
childBhv.batchInsert(childList);
```

---

## 5. パフォーマンス規約（性能関連）

### 5.1 SQL パフォーマンス

- 大量データを扱う処理では必ずインデックスが使用されることを確認する。
- `SELECT *` は使用せず、必要なカラムのみ取得する。
- 遅い SQL は `EXPLAIN` で実行計画を確認してからリリースする。
- DB 接続は必要以上に長く保持しない。

### 5.2 Java パフォーマンス

- コレクション操作（ソート、検索）は Stream API を活用する。
- 大量データの処理はページング（件数制限付き取得）を行う。
- 不要なオブジェクト生成（ループ内 `new`）を避ける。
- ログ出力のフォーマット処理はログレベルで分岐してから行う：

```java
// NG: ログレベルに関係なく文字列結合が実行される
logger.debug("処理結果: " + result.toString()); // NG

// OK: デバッグログは有効な場合のみ処理
if (logger.isDebugEnabled()) {
    logger.debug("処理結果: {}", result.toString()); // OK
}
```

---

## 6. 排他制御

- 更新系の処理では、必要に応じて楽観的ロックまたは悲観的ロックを実装する。
- DBFlute を使用した楽観的ロックはバージョンカラム（`VERSION_NO` 等）で管理する。
- 排他制御が必要な業務フローは設計時に明確にし、実装方針を統一する。

```java
// DBFlute による楽観的ロックの例（バージョンNo使用）
entity.setVersionNo(form.getVersionNo()); // 画面から受け取ったバージョンNo をセット
stockBhv.update(entity); // バージョン不一致の場合は例外がスローされる
```

---

## 7. エラー制御・例外処理

- 業務エラーは専用の例外クラス（`BizException` 等）で表現する。
- システムエラー（DB接続エラー等）は `RuntimeException` 系でロールバックを発生させる。
- **検査例外（`Exception` のサブクラス）を catch して再 throw する場合は `RuntimeException` でラップする**（ロールバックを確実にするため）。

```java
// 検査例外を RuntimeException でラップしてロールバックを保証する
try {
    someExternalProcess();
} catch (IOException e) {
    throw new RuntimeException("外部処理でエラーが発生しました", e); // RuntimeException でラップ
}
```

- Controller 層での例外ハンドリングは `@ExceptionHandler` または共通の AOP で統一処理する。
- ログには例外スタックトレースを必ず出力する（`logger.error("メッセージ", e)`）。

---

## 8. コーディング基準

### 8.1 一般ルール

- メソッドは単一責任原則に従い、1つのメソッドが1つのことだけを行うように設計する。
- メソッドの行数は目安として50行以内に抑える。超える場合はメソッド分割を検討する。
- マジックナンバー・マジック文字列は定数で定義する。
- `null` チェックは適切に行い、`NullPointerException` を防止する（Java 8以降は `Optional` を活用）。

### 8.2 DTO 設計

- Controller と Service 間のデータ受け渡しは DTO を使用する。Entity を直接 Controller に露出させない。
- DTO には業務上必要なフィールドのみ定義する。
- 画面への返却データは ResponseDto、画面からの受取データは Form または RequestDto として区別する。

### 8.3 ログ出力基準

| レベル | 用途 |
|--------|------|
| `ERROR` | システムエラー、予期しない例外 |
| `WARN` | 業務上の警告（処理は継続可能）|
| `INFO` | 業務の重要な処理開始・終了 |
| `DEBUG` | デバッグ用の詳細情報（本番では OFF）|

---

## 9. データベース規約

### 9.1 MySQL 固有

- トランケートが必要な場合は `TRUNCATE TABLE` を使用するが、ロールバック不可のため慎重に扱う。
- 遅いクエリが発生した場合は `SHOW PROCESSLIST` で確認し、必要に応じて `KILL` コマンドで切断する。

### 9.2 Oracle 固有

- テーブル定義の確認は `ALL_COLUMNS` / `USER_COLUMNS` ビューを使用する。
- シーケンスは DBFlute の設定に従い管理する。

### 9.3 共通

- テーブル・カラムの命名はスネークケース（大文字）で統一する（例: `STOCK_MAST`, `ITEM_ID`）。
- 主キーは自動採番（DBFlute の Sequence / Identity）を使用する。
- 共通カラム（作成日時、更新日時、バージョンNo等）は全テーブルに持たせる。

---

## 10. DBFlute 固有の注意事項

- **Inject でインスタンスが null になる場合**: `@Inject` アノテーションが正しく付与されているか、対象クラスが DI コンテナ管理下にあるかを確認する（`@Service`, `@Component` 等の付与漏れが多い）。
- **`load-data-reverse` がメモリ不足エラーになる場合**: JVM のヒープサイズを拡張する（`-Xmx` オプション）。
- **`manage.bat` の `regenerate` に時間がかかる場合**: 対象スキーマのテーブル数が多い場合は正常。待機するか、不要なテーブルをスキップ設定する。

---

## 11. セキュリティ

- SQL インジェクション対策として、ユーザ入力値は必ずバインド変数（PreparedStatement / DBFlute のバインド変数）で処理する。
- 権限チェックは Controller または AOP で実施し、Service 層でも必要に応じて二重チェックする。
- パスワード等の機密情報はログに出力しない。
- API リクエストの入力値バリデーションは Controller / Form 層で実施する（`@Valid` アノテーション活用）。

---

## 12. コードレビューチェックリスト

実装完了時に以下を確認すること：

- [ ] ロールバックが必要な箇所で `RuntimeException` を使用しているか
- [ ] N+1 問題（ループ内 SQL 発行）が発生していないか
- [ ] COUNT SQL で不要なテーブル・カラムを含んでいないか
- [ ] バルクインサートが必要な箇所で1件ずつ INSERT していないか
- [ ] SQL が複雑すぎる場合、Java 側に処理を移す検討をしたか
- [ ] DTO が適切に定義されているか（Entity を直接 Controller に露出していないか）
- [ ] `null` チェックが適切に実装されているか
- [ ] ログに機密情報を含めていないか
- [ ] 入力バリデーションが実装されているか
- [ ] 排他制御が必要な処理に実装されているか