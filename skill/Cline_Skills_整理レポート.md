# Cline Skills 機能の整理レポート

> 参照元: https://docs.cline.bot/customization/skills

---

## 1. Skills とは

**Cline の能力を特定タスク向けに拡張するモジュール式の指示セット**です。各スキルには詳細なガイダンス、ワークフロー、オプションのリソースがパッケージ化されており、リクエストに関連する場合のみロードされます。

### Rules（ルール）との違い

| 比較項目 | Rules | Skills |
|---------|-------|--------|
| ロードタイミング | **常時アクティブ** | **オンデマンド（必要時のみ）** |
| コンテキスト消費 | 常に消費 | 必要時のみ消費 |
| 用途 | コーディング規約、一般方針 | 特定タスクの専門知識 |


---

## 2. プログレッシブローディング（段階的読み込み）

| レベル | ロードタイミング | トークンコスト | 内容 |
|--------|--------------|-------------|------|
| **Metadata** | 常時（起動時） | ~100 tokens/スキル | YAML frontmatter の `name` と `description` |
| **Instructions** | スキル発動時 | 5k tokens未満 | SKILL.md 本文 |
| **Resources** | 必要に応じて | 実質無制限 | バンドルファイル（`read_file` またはスクリプト実行） |

ユーザーがメッセージを送ると、Clineはスキルの `description` を基にマッチングし、`use_skill` ツールで発動します。

---

## 3. スキルの構造

```
my-skill/
├── SKILL.md          # 必須: メイン指示ファイル
├── docs/             # 任意: 追加ドキュメント
│   └── advanced.md
├── templates/        # 任意: テンプレートファイル
│   └── config.yaml
└── scripts/          # 任意: ユーティリティスクリプト
    └── helper.sh
```

### SKILL.md のフォーマット

```markdown
---
name: my-skill
description: スキルの説明。いつ使うかを明記する。具体的・アクション指向で。
---

# スキル名

Clineが従うべき詳細な指示。

## Steps
1. まず、これを行う
2. 次に、これを行う
3. 高度な使い方は [advanced.md](docs/advanced.md) を参照
```

**必須フィールド:**
- `name`: ディレクトリ名と**完全一致**する必要あり
- `description`: Clineがいつこのスキルを使うか判断するための説明

### 効果的な description の書き方

**良い例（具体的・アクション指向）:**
```yaml
description: Deploy applications to AWS using CDK. Use when deploying, updating infrastructure, or managing AWS resources.
description: Analyze CSV and Excel data files. Use when exploring datasets, generating statistics, or creating visualizations from tabular data.
```

**悪い例（曖昧すぎる）:**
```yaml
description: Helps with AWS stuff.
description: Data analysis helper.
```

### 命名規則
- **kebab-case**（小文字＋ハイフン）を使用
- 良い例: `aws-cdk-deploy`, `pr-review-checklist`, `database-migration`
- 悪い例: `aws`（曖昧）, `my_skill`（アンダースコア）, `DeployToAWS`（PascalCase）

---

## 4. スキルの配置場所

### プロジェクトスキル（ワークスペース内）
- `.cline/skills/`（**公式推奨**）
- `.clinerules/skills/`
- `.claude/skills/`
- `.agents/skills/`（非公式だがClineが検出。実機確認済み）

### グローバルスキル
- `~/.cline/skills/`（macOS/Linux）
- `C:\Users\USERNAME\.cline\skills\`（Windows）

**優先順位**: グローバルスキルとプロジェクトスキルが同名の場合、**グローバルが優先**。

**チーム共有**: `.cline/skills/` をバージョン管理にコミットすることで、チーム全体でスキルを共有・レビュー・改善可能。

---

## 5. バンドルファイルの活用

### docs/ — 追加ドキュメント
- 詳細な設定オプション、トラブルシューティング、プラットフォーム別手順など
- 例: `docs/aws.md`, `docs/gcp.md`, `docs/azure.md`

### templates/ — テンプレートファイル
- 設定ファイル（Terraform, Docker Compose, CI/CDパイプライン）
- コードスキャフォールディング（コンポーネントテンプレート、テストフィクスチャ）

### scripts/ — ユーティリティスクリプト
- バリデーション、データ処理、複雑な計算、APIインタラクション
- **トークン効率が高い**: スクリプトの出力のみがコンテキストに入り、コード自体は消費しない

| Scripts の用途 | Instructions の用途 |
|-------------|-----------------|
| 決定論的操作（バリデーション、フォーマット） | コンテキストに応じた柔軟なガイダンス |
| 複雑な計算 | 意思決定ワークフロー |
| 信頼性が必要な操作 | 状況により変わるステップ |
| トークン消費を避けたい処理 | ベストプラクティスとパターン |

---

## 6. Skills の使用シーン

Skills は「特定のタスクに対して専門的な知識やワークフローが必要なとき」に最適です。以下に代表的な使用シーンを分類して紹介します。

### 6.1 データ処理・分析

今回の作業Excel->md化のため、skillを利用して試した（未完全検証、知識を把握するため）

| シーン | スキル例 | 説明 |
|--------|---------|------|
| Excel解析 | `excel-parse` | Excelファイルから設計データ（処理フロー、クラス定義、画面項目等）を抽出 |

<details>
<summary>📖 SKILL.md の例（design-analyzer）</summary>

```markdown
---
name: design-analyzer
description: 解析後の設計データを分析し、設計パターン、潜在的な問題、最適化提案を識別し、
  設計判断記録を生成します。アーキテクチャ設計レビューと技術方針策定に適しています。
---

# 業務機能設計分析スキル

## 概要
excel-parseスキルで抽出された構造化設計データを分析し、ソースコードレベルの設計品質を評価するスキルです。
Javaクラス構成、JavaScript画面制御、DTO設計、DB操作、共通機能利用の観点から分析を行います。

## 分析観点

### 1. ソースコード構成分析
#### Java層（サーバサイド）
- Resourceクラス分析、Logicクラス分析、DTO分析、DB操作分析

#### JavaScript層（フロントエンド）
- 画面制御分析、イベントハンドラ分析、バリデーション分析

#### HTML/CSS層（画面）
- 画面レイアウト分析、スタイル分析

### 2. 処理フロー分析
- 処理間の関連分析、エラーハンドリング分析、画面モード別分析、ステータス遷移分析

### 3. テーブル設計分析
- マッピング整合性、予定/実績の整合性、登録/更新の網羅性、テーブル間結合

### 4. 共通機能利用分析
- 共通コンポーネント参照、マスタデータ取得、採番ロジック、認証/権限

### 5. クラス一覧の導出（自動導出）
| 分類 | クラスID例 | 役割 |
|------|-----------|------|
| JavaScript | {FunctionName}.js | 画面制御 |
| Resource | {FunctionName}Resource.java | REST API エンドポイント |
| Logic | {FunctionName}SelectLogic.java 等 | 業務ロジック |
| DTO | {FunctionName}Dto | データ受け渡し用 |

### 6. DTO構造の導出
- 画面DTO：ヘッダ部 + 明細部（リスト）の構成
- 各フィールドの型、必須/任意、バリデーション条件

## 出力形式（抜粋）
- ソースコード構成サマリ、処理フロー構成、潜在的な問題、DTO構造、共通機能利用一覧、設計判断記録
```

</details>

---

## 7. Skills のメリット

### 7.1 トークン効率の最適化

Skills の最大の利点は**オンデマンドローディング**です。

```
通常のRulesの場合:
  全ルール → 常にコンテキストに含まれる → トークン消費が増大

Skillsの場合:
  メタデータのみ（~100 tokens/スキル） → 必要時にのみ本文をロード
```

**具体的な節約例:**
- 10個のスキルを登録した場合、待機時のトークンコストは **~1,000 tokens**
- 同じ内容をRulesに記載すると、常時 **~50,000 tokens** を消費
- **約98%のトークン節約**が可能

### 7.2 チーム共有とナレッジの標準化

```
.cline/skills/              ← Gitにコミット
├── deploy-to-staging/      ← デプロイ手順を標準化
├── pr-review-checklist/    ← レビュー基準を統一
└── coding-standards/       ← コーディング規約を共有
```

- プロジェクトの `.cline/skills/` をGitにコミットすることで、**チーム全員が同じスキルセットを利用可能**
- 新メンバーのオンボーディングが容易に
- スキルのバージョン管理・レビュー・改善がGitワークフローに統合

### 7.3 専門知識のカプセル化

複雑なドメイン知識を**再利用可能なモジュール**としてパッケージ化できます：

- **業務ロジック**: 特定業界の業務フロー、ビジネスルール
- **技術スタック**: フレームワーク固有のベストプラクティス
- **運用手順**: デプロイ、障害対応、メンテナンス手順

### 7.4 スキルチェーン（複数スキルの連携）

複数のスキルを順番に発動させることで、複雑なワークフローを実現できます：

```
本プロジェクトの例:
  excel-parse → design-analyzer → md-design-generator
  （Excel解析）  （設計分析）      （Markdown設計書生成）
```

各スキルが独立しているため、**単体でも連携でも使用可能**です。

---

## 8. 注意点・ベストプラクティス

### 8.1 標準機能に昇格済み
> ✅ **Cline v3.x（3.0以降）では、Skills は標準機能として組み込まれています。**  
> `use_skill` ツールがシステムに標準搭載されており、`Settings → Features → Enable Skills` のトグルは**廃止（UIから削除）**されました。  
> したがって、**現在は特別な有効化設定は不要**で、`.cline/skills/` 等にスキルを配置すれば自動的に検出・利用可能です。  
> （2026-04 実機確認済み）

### 8.2 スキルのトグル（有効/無効の切り替え）

公式ドキュメントによると、すべてのスキルには**有効/無効を切り替えるトグル**があります。

```
スキルのトグル機能:
  - 各スキルに個別のトグルがある
  - スキルは発見時にデフォルトで有効
  - ディレクトリを削除せずに無効化可能
```

**活用例:**
- **CI/CDスキル** → ローカル開発中は無効化、デプロイ時のみ有効化
- **クライアント固有スキル** → 特定クライアントのプロジェクト作業時のみ有効化
- **テストスキル** → 検証が終わったら無効化して他のスキルとの干渉を防ぐ

### 8.3 description の品質がマッチング精度に直結

Clineはユーザーのリクエストとスキルの `description` を比較してマッチングを行います。**description が曖昧だとスキルが発動しない、または誤って発動する**可能性があります。

**効果的なdescription作成のポイント:**

| ポイント | 良い例 | 悪い例 |
|---------|--------|--------|
| 具体的なアクションを記述 | `Deploy applications to AWS using CDK` | `Helps with AWS stuff` |
| トリガーワードを含める | `Use when deploying, updating infrastructure` | （記載なし） |
| ユーザーの自然な発言を想定 | `"deploy my app", "push this live"` | （記載なし） |
| 対象を明確にする | `Analyze CSV and Excel data files` | `Data analysis helper` |

### 8.4 名前の一致に注意

ディレクトリ名と SKILL.md 内の `name` フィールドは**完全一致**が必要です。

```
✅ 正しい:
  my-skill/SKILL.md → name: my-skill

❌ 間違い:
  my-skill/SKILL.md → name: mySkill     ← 不一致
  my_skill/SKILL.md → name: my_skill    ← kebab-caseでない
```

### 8.5 グローバル vs プロジェクトスキルの優先順位

同名のスキルが両方に存在する場合、**グローバルスキルが優先**されます。

```
C:\Users\USERNAME\.cline\skills\my-skill\    ← グローバル（優先）
.cline\skills\my-skill\                       ← プロジェクト（上書きされる）
```

> 💡 チーム共有スキルはプロジェクトスキルに、個人カスタマイズはグローバルスキルに配置するのが推奨パターンです。

---

## まとめ

Clineの Skills は**オンデマンドローディングによるトークン効率の最適化**が最大の特徴です。

> 公式ドキュメント原文: *"Skills transform Cline from a general-purpose assistant into a specialist that knows your domain."*

| 観点 | ポイント |
|------|---------|
| **使用シーン** | デプロイ、コードレビュー、データ処理、設計書管理、リリース管理、フレームワーク固有知識など、専門知識が必要な繰り返しタスク |
| **最大のメリット** | トークン効率（~98%節約）、チーム共有、専門知識のカプセル化、スキルチェーン、トグルによる柔軟な管理 |
| **最大の注意点** | description の品質がマッチング精度に直結。 |
| **互換性** | `.claude/skills/` パスの読み取りは可能だが、マルチツール環境では設計上の配慮が必要 |