# Cline Skills 機能の整理レポート

> 参照元: https://docs.cline.bot/customization/skills  
> 作成日: 2026/4/10

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

## 6. 本プロジェクトでの実験結果

### 検出されたスキル配置場所

| ディレクトリ | スキル | Clineで検出 | 備考 |
|------------|--------|-----------|------|
| `.claude/skills/` | `test-claude-skill` | ✅ 検出済 | Claude Code互換パス |
| `.agents/skills/` | `design-analyzer`, `excel-parse`, `md-design-generator` | ✅ 検出済 | **公式ドキュメントに記載なし** |
| `.cline/skills/` | `my-skill` | ✅ 検出済 | 公式推奨パス |

### 発見事項
- Clineは公式ドキュメントに記載されている `.cline/skills/`, `.clinerules/skills/`, `.claude/skills/` に加え、**`.agents/skills/` も自動検出**する
- これは公式ドキュメントに記載されていない非公式の互換挙動

---

## 7. 他のLLMツールとのSkills構造互換性に関する課題

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

Clineの Skills は**オンデマンドローディングによるトークン効率の最適化**が最大の特徴です。ただし、この仕組みはCline固有のものであり、他のLLMコーディングツールとの互換性は限定的です。`.claude/skills/` パスの読み取りは可能ですが、スキルの発動メカニズム（description マッチング → use_skill ツール）自体が異なるため、マルチツール環境では設計上の配慮が必要です。