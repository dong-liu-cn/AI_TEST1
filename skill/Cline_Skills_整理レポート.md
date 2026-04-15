# Cline Skills 機能の整理レポート

> 参照元: https://docs.cline.bot/customization/skills  
> 作成日: 2026/4/10  
> 更新日: 2026/4/15（使用シーン・メリット・注意点・公式ドキュメント最新情報を追加）

---

## 1. Skills とは

**Cline の能力を特定タスク向けに拡張するモジュール式の指示セット**です。各スキルには詳細なガイダンス、ワークフロー、オプションのリソースがパッケージ化されており、リクエストに関連する場合のみロードされます。

### Rules（ルール）との違い

| 比較項目 | Rules | Skills |
|---------|-------|--------|
| ロードタイミング | **常時アクティブ** | **オンデマンド（必要時のみ）** |
| コンテキスト消費 | 常に消費 | 必要時のみ消費 |
| 用途 | コーディング規約、一般方針 | 特定タスクの専門知識 |

> ⚠️ Skills は**実験的機能**です。`Settings → Features → Enable Skills` で有効化が必要。

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
description: スキルの説明（最大1024文字）。いつ使うかを明記する。
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
- `description`: Clineがいつこのスキルを使うか判断するための説明（最大1024文字）

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
| md/データ分析 | `data-analyzer` | データセットの探索、統計生成、可視化 |
| ドキュメント変換 | `md-design-generator` | 構造化データをMarkdown形式の設計書に変換 |


### 6.2 コード品質・レビュー

コード品質・レビュー階段skillを利用する例

| シーン | スキル例 | 説明 |
|--------|---------|------|
| UIレビュー | `web-design-guidelines` | Webインターフェースガイドラインに基づくUI/UXコードレビュー |
| パフォーマンス最適化 | `vercel-react-best-practices` | React/Next.jsのパフォーマンス最適化パターンの適用 |
| コンポーネント設計 | `vercel-composition-patterns` | boolean prop増殖の解消、柔軟なコンポーネントAPI設計 |

**実際のdescription例（`web-design-guidelines`）:**
```yaml
description: Review UI code for Web Interface Guidelines compliance. Use when asked 
  to "review my UI", "check accessibility", "audit design", "review UX", 
  or "check my site against best practices".
```

### 6.3 設計・アーキテクチャ


| シーン | スキル例 | 説明 |
|--------|---------|------|
| 設計分析 | `design-analyzer` | 設計データの分析、パターン識別、最適化提案 |
| DB マイグレーション | `database-migration` | データベーススキーマの変更管理 |
| API設計 | `api-design` | RESTful/GraphQL APIの設計ガイドライン |

**実際のdescription例（公式ドキュメントより）:**
```yaml
description: Generate release notes from git commits. Use when preparing releases, 
  writing changelogs, or summarizing recent changes.
```

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

### 8.1 有効化が必要（実験的機能）

Skills はデフォルトで無効です。使用前に以下の設定を行う必要があります：

```
Settings → Features → Enable Skills ☑
```

> ⚠️ 実験的機能のため、将来のバージョンで仕様が変更される可能性があります。

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

### 8.4 SKILL.md の書き方のベストプラクティス

**公式ドキュメントの推奨事項:**

1. **重要な情報を先頭に配置する**
   - Clineはファイルを順番に読むため、よくある使用ケースを最初に記載する
   
2. **明確なセクションヘッダーを使う**
   - `## Error Handling` や `## Configuration` のようなヘッダーで、Clineが関連セクションをスキャンしやすくする

3. **具体的な例を含める**
   - 実行するコマンド、期待される出力、結果の見た目を示す
   - 抽象的な指示より具体的な例の方がClineは従いやすい

4. **description にアクション動詞を使う**
   ```yaml
   # 良い例: アクション動詞で始まる
   description: Deploy applications to AWS using CDK.
   description: Analyze CSV and Excel data files.
   description: Generate release notes from git commits.
   
   # 悪い例: 曖昧
   description: Helps with AWS stuff.
   description: Useful for releases.
   ```

5. **description にトリガーフレーズを含める**
   - ユーザーが言いそうなフレーズを想定して記載する
   - 異なる表現でリクエストしてスキルが発動するかテストする

### 8.5 SKILL.md のサイズ制限

- SKILL.md 本文は **5,000トークン以下** を推奨
- 長い指示は **docs/ フォルダ** に分割する
- 大量データの処理は **scripts/ フォルダ** のスクリプトに委譲する

```
推奨構成:
  SKILL.md        → 概要と主要ステップ（5k tokens未満）
  docs/detail.md  → 詳細な手順やリファレンス（必要時に read_file で読み込み）
  scripts/run.py  → データ処理（実行結果のみコンテキストに入る）
```

### 8.6 名前の一致に注意

ディレクトリ名と SKILL.md 内の `name` フィールドは**完全一致**が必要です。

```
✅ 正しい:
  my-skill/SKILL.md → name: my-skill

❌ 間違い:
  my-skill/SKILL.md → name: mySkill     ← 不一致
  my_skill/SKILL.md → name: my_skill    ← kebab-caseでない
```

### 8.7 グローバル vs プロジェクトスキルの優先順位

同名のスキルが両方に存在する場合、**グローバルスキルが優先**されます。

```
C:\Users\USERNAME\.cline\skills\my-skill\    ← グローバル（優先）
.cline\skills\my-skill\                       ← プロジェクト（上書きされる）
```

> 💡 チーム共有スキルはプロジェクトスキルに、個人カスタマイズはグローバルスキルに配置するのが推奨パターンです。

### 8.8 スキルの発動確認

スキルが正しく検出・発動されているか確認する方法：

1. **システムプロンプト確認**: Clineの `Available skills` セクションにスキル名が表示されているか
2. **テストスキル作成**: 簡単なテストスキルを作成して検出を確認（本プロジェクトの `test-claude-skill` の例）
3. **description テスト**: 想定するトリガーフレーズでリクエストし、スキルが発動するか確認

### 8.9 セキュリティに関する考慮

- scripts/ 内のスクリプトは **Clineが自動実行** する可能性があるため、信頼できるコードのみ配置する
- コミュニティスキルを利用する際は、scripts/ の内容を確認してからインストールする
- 機密情報（APIキー等）はスキルファイルに直接記載せず、環境変数を参照する設計にする

---

## 10. 他のLLMツールとのSkills構造互換性に関する課題

### 他のLLMコーディングツールとの比較

| ツール | スキル相当の仕組み | 配置場所 | フォーマット |
|--------|----------------|---------|------------|
| **Cline** | Skills (`SKILL.md`) | `.cline/skills/`, `.claude/skills/`, `.clinerules/skills/` | YAML frontmatter + Markdown |
| **Claude Code** | CLAUDE.md / Skills | `.claude/` | Markdown |
| **Cursor** | Rules for AI | `.cursor/rules/` | Markdown |
| **Windsurf** | Rules | `.windsurfrules` | Markdown |
| **GitHub Copilot** | Instructions | `.github/copilot-instructions.md` | Markdown |

### 主要な互換性課題

#### 1. `.claude/skills/` の互換性
Cline は Claude Code のスキルディレクトリ `.claude/skills/` を読み取り可能。**同じ SKILL.md フォーマット**でClineとClaude Code両方で動作する可能性があるが、Claude Codeのスキル仕様はClineとは別物のため**完全互換ではない**。

#### 2. `.agents/skills/` の非公式対応
本プロジェクトでは `.agents/skills/` に配置したスキルもClineが自動検出した。これは公式ドキュメントに記載されていない挙動で、Clineが複数の慣例パスを広く探索していることを示す。

---

## まとめ

Clineの Skills は**オンデマンドローディングによるトークン効率の最適化**が最大の特徴です。

> 公式ドキュメント原文: *"Skills transform Cline from a general-purpose assistant into a specialist that knows your domain."*

| 観点 | ポイント |
|------|---------|
| **使用シーン** | デプロイ、コードレビュー、データ処理、設計書管理、リリース管理、フレームワーク固有知識など、専門知識が必要な繰り返しタスク |
| **最大のメリット** | トークン効率（~98%節約）、チーム共有、専門知識のカプセル化、スキルチェーン、トグルによる柔軟な管理 |
| **最大の注意点** | description の品質がマッチング精度に直結。実験的機能のため設定で有効化が必要。SKILL.md は5kトークン以下を推奨 |
| **互換性** | `.claude/skills/` パスの読み取りは可能だが、マルチツール環境では設計上の配慮が必要 |

Skills を効果的に活用するための4つの鍵：
1. **良いdescription** — 具体的でアクション指向、トリガーワードを含む。異なる表現でテストする
2. **適切なサイズ** — SKILL.md は5k tokens以下、大きい処理はscripts/docs/に分離
3. **重要な情報を先頭に** — Clineは順番に読むため、よくあるケースを先に配置
4. **チーム共有** — `.cline/skills/` をGitにコミットし、チームで改善サイクルを回す