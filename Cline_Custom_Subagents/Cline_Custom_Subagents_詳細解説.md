# Cline カスタムサブエージェント（Custom Subagents）詳細解説

> **対象読者**: Cline中級者〜上級者  
> **最終更新**: 2026年4月  
> **公式ドキュメント**: https://docs.cline.bot  
> **参照**: https://docs.cline.bot/features/cline-rules, https://docs.cline.bot/cline-tools/new-task-tool

---

## 目次

1. [カスタムサブエージェントとは何か](#1-カスタムサブエージェントとは何か)
2. [サブエージェントを実現する4つの仕組み](#2-サブエージェントを実現する4つの仕組み)
3. [Custom Modes（カスタムモード）詳解](#3-custom-modesカスタムモード詳解)
4. [New Task Tool（サブタスク生成）詳解](#4-new-task-toolサブタスク生成詳解)
5. [Workflows（ワークフロー）詳解](#5-workflowsワークフロー詳解)
6. [.clinerules による行動制御](#6-clinerules-による行動制御)
7. [実践例①：コードレビューサブエージェント](#7-実践例コードレビューサブエージェント)
8. [実践例②：テスト自動生成サブエージェント](#8-実践例テスト自動生成サブエージェント)
9. [実践例③：マルチエージェントオーケストレーション](#9-実践例マルチエージェントオーケストレーション)
10. [実践例④：設計書→コード生成パイプライン](#10-実践例設計書コード生成パイプライン)
11. [サブエージェントの設定手順（Step-by-Step）](#11-サブエージェントの設定手順step-by-step)
12. [ベストプラクティスと注意点](#12-ベストプラクティスと注意点)
13. [トラブルシューティング](#13-トラブルシューティング)
14. [参考リンク集](#14-参考リンク集)

---

## 1. カスタムサブエージェントとは何か

### 概要

**カスタムサブエージェント**とは、Cline（AIコーディングエージェント）内で**特定の役割・専門性を持つ仮想的なAIアシスタント**を作成し、タスクごとに最適化されたエージェントとして動作させる仕組みです。

通常のClineは「汎用AIアシスタント」として動作しますが、カスタムサブエージェントを使うことで以下のような**専門エージェント**を定義できます：

- 🔍 **コードレビュー専門エージェント** - コード品質に特化した分析を行う
- 🧪 **テスト生成エージェント** - テストコードの作成に特化
- 📐 **アーキテクチャ設計エージェント** - 設計判断に特化
- 🐛 **デバッグ専門エージェント** - バグ調査と修正に特化
- 📝 **ドキュメント生成エージェント** - ドキュメント作成に特化
- 🔒 **セキュリティ監査エージェント** - セキュリティ脆弱性の検出に特化

### イメージ図

```
┌─────────────────────────────────────────────────────────────────┐
│                     Cline メインエージェント                       │
│                                                                 │
│  ユーザー: 「この機能を実装して、テストも書いて、レビューもして」      │
│                                                                 │
│         ↓ タスク分解・サブエージェント呼び出し                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ 🛠️ コーダー   │  │ 🧪 テスター   │  │ 🔍 レビュアー │           │
│  │ サブエージェント│  │ サブエージェント│  │ サブエージェント│           │
│  │              │  │              │  │              │           │
│  │ ・コード実装  │  │ ・テスト生成  │  │ ・品質チェック │           │
│  │ ・ファイル作成 │  │ ・テスト実行  │  │ ・改善提案    │           │
│  │ ・リファクタ  │  │ ・カバレッジ  │  │ ・セキュリティ │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────┐                │
│  │            最終成果物（統合結果）               │                │
│  └─────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

### なぜサブエージェントが必要か？

| 課題 | サブエージェントによる解決 |
|------|--------------------------|
| 1つのプロンプトが長くなりすぎる | 役割ごとに分離して最適化 |
| コンテキストウィンドウの制限 | サブタスクごとにコンテキストを最適化 |
| 汎用的な回答で精度が低い | 専門的な指示により精度向上 |
| 複雑なタスクの管理が困難 | パイプライン化で段階的に処理 |
| 品質のばらつき | 各段階で品質チェックを組み込み |

---

## 2. サブエージェントを実現する4つの仕組み

Clineでカスタムサブエージェントを実現するには、主に**4つの仕組み**を組み合わせます。

### 比較表

| 仕組み | 概要 | 難易度 | 適したユースケース |
|--------|------|--------|-------------------|
| **Custom Modes** | Clineの動作モードを定義 | ⭐ 簡単 | 役割ベースの切り替え |
| **New Task Tool** | サブタスクを動的に生成 | ⭐⭐ 中級 | タスク分解・委任 |
| **Workflows** | 事前定義されたタスクチェーン | ⭐⭐ 中級 | 繰り返しパターン |
| **.clinerules** | エージェントの行動ルール定義 | ⭐ 簡単 | プロジェクト固有ルール |

### 全体像

```
┌─────────────────────────────────────────────────────┐
│              カスタムサブエージェント                    │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │ .clinerules │  │ Custom      │  ← 行動ルール定義  │
│  │ ファイル     │  │ Modes       │  ← モード定義      │
│  └──────┬──────┘  └──────┬──────┘                   │
│         │                │                          │
│         ▼                ▼                          │
│  ┌──────────────────────────────┐                   │
│  │     Cline メインエージェント    │                   │
│  └──────────────┬───────────────┘                   │
│                 │                                   │
│         ┌───────┴───────┐                           │
│         ▼               ▼                           │
│  ┌─────────────┐ ┌─────────────┐                    │
│  │ New Task    │ │ Workflows   │  ← タスク実行      │
│  │ Tool        │ │             │  ← 自動パイプライン │
│  └─────────────┘ └─────────────┘                    │
└─────────────────────────────────────────────────────┘
```

---

## 3. Custom Modes（カスタムモード）詳解

### 概要

**Custom Modes**は、Clineに**異なるペルソナ・役割**を持たせる機能です。各モードに対して、使用可能なツール、行動指針、応答スタイルを個別に設定できます。

### モードの定義

Clineでは、以下の設定ファイルでカスタムモードを定義します：

**グローバル設定**（全プロジェクト共通）:
```
C:\Users\YJSNOTE14\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_custom_modes.json
```

**プロジェクト固有設定**:
```
プロジェクトルート/.roomodes
```

### モード定義のJSON構造

```json
{
  "customModes": [
    {
      "slug": "code-reviewer",
      "name": "🔍 Code Reviewer",
      "roleDefinition": "あなたはシニアコードレビュアーです。コードの品質、可読性、パフォーマンス、セキュリティを厳密にチェックします。問題を発見した場合は具体的な改善案を提示してください。",
      "groups": [
        "read",
        ["edit", {
          "fileRegex": "\\.md$",
          "description": "レビュー結果のMarkdownファイルのみ編集可能"
        }],
        "command"
      ],
      "customInstructions": "レビュー時は以下の観点を必ずチェックすること：\n1. エラーハンドリングの適切さ\n2. 命名規則の一貫性\n3. DRY原則の遵守\n4. セキュリティ脆弱性\n5. パフォーマンスの問題\n\nレビュー結果は必ず以下のフォーマットで出力：\n- 🔴 Critical: 必ず修正が必要\n- 🟡 Warning: 改善を推奨\n- 🟢 Info: 参考情報"
    },
    {
      "slug": "test-writer",
      "name": "🧪 Test Writer",
      "roleDefinition": "あなたはテストエンジニアです。与えられたコードに対して、包括的なユニットテスト、統合テスト、E2Eテストを作成します。テストカバレッジ100%を目指してください。",
      "groups": [
        "read",
        ["edit", {
          "fileRegex": "\\.(test|spec)\\.(ts|js|tsx|jsx)$",
          "description": "テストファイルのみ編集可能"
        }],
        "command"
      ],
      "customInstructions": "テスト作成時のルール：\n1. 正常系・異常系・境界値を網羅\n2. AAA（Arrange-Act-Assert）パターンを使用\n3. テスト名は日本語で分かりやすく\n4. モックは最小限に\n5. テスト実行後にカバレッジレポートを出力"
    },
    {
      "slug": "architect",
      "name": "📐 Architect",
      "roleDefinition": "あなたはソフトウェアアーキテクトです。システム設計、技術選定、ディレクトリ構造の設計を担当します。コードの実装は行わず、設計判断と設計ドキュメントの作成に集中します。",
      "groups": [
        "read",
        ["edit", {
          "fileRegex": "\\.(md|mmd|puml)$",
          "description": "設計ドキュメントのみ編集可能"
        }]
      ],
      "customInstructions": "設計時の指針：\n1. SOLID原則を遵守\n2. 設計パターンを適切に適用\n3. スケーラビリティを考慮\n4. 設計判断の理由を必ず記録\n5. Mermaid図で可視化"
    },
    {
      "slug": "debugger",
      "name": "🐛 Debugger",
      "roleDefinition": "あなたはデバッグの専門家です。バグの根本原因を特定し、最小限の修正で問題を解決します。修正の影響範囲を慎重に分析し、副作用のない修正を心がけてください。",
      "groups": [
        "read",
        "edit",
        "command",
        "browser"
      ],
      "customInstructions": "デバッグ手順：\n1. まずバグの再現手順を確認\n2. 関連するログ・エラーメッセージを分析\n3. 仮説を立てて検証\n4. 根本原因を特定（表面的な対処はNG）\n5. 修正後に回帰テストを実行\n6. 修正内容と原因の説明を記録"
    }
  ]
}
```

### ツールグループの説明

| グループ名 | 含まれるツール | 説明 |
|-----------|--------------|------|
| `read` | `read_file`, `search_files`, `list_files`, `list_code_definition_names` | ファイル読み取り系 |
| `edit` | `write_to_file`, `replace_in_file` | ファイル編集系 |
| `command` | `execute_command` | コマンド実行 |
| `browser` | `browser_action` | ブラウザ操作 |
| `mcp` | `use_mcp_tool`, `access_mcp_resource` | MCP連携 |

### ファイルパターンによる制限

`edit` グループにファイルパターンを設定することで、**サブエージェントが編集できるファイルを制限**できます：

```json
["edit", {
  "fileRegex": "\\.(test|spec)\\.(ts|js)$",
  "description": "テストファイルのみ編集可能"
}]
```

これにより、テストエージェントが本番コードを誤って変更するリスクを防げます。

---

## 4. New Task Tool（サブタスク生成）詳解

### 概要

**New Task Tool**は、Clineが現在のタスクから**新しいサブタスクを生成**するためのツールです。メインタスクの中で「この部分は別のサブタスクとして処理する」という委任を可能にします。

> **公式ドキュメント**: https://docs.cline.bot/cline-tools/new-task-tool

### 仕組み

```
┌─────────────────────────────────────────────┐
│          メインタスク（親エージェント）          │
│                                             │
│  1. ユーザーから指示を受ける                    │
│  2. タスクを分析・分解                         │
│  3. サブタスクを生成 ← new_task ツール          │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │       サブタスク（子エージェント）          │ │
│  │                                         │ │
│  │  ・独立したコンテキスト                    │ │
│  │  ・親から引き継いだ情報のみ                │ │
│  │  ・完了後、結果を親に返す                  │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  4. サブタスクの結果を統合                      │
│  5. 最終結果をユーザーに返す                    │
└─────────────────────────────────────────────┘
```

### New Task の呼び出し方

メインエージェントがサブタスクを生成する際、以下の形式で `new_task` ツールを使用します：

```xml
<new_task>
<context>
1. Current Work:
   ユーザー管理API（GET /api/users）のユニットテスト作成

2. Key Technical Concepts:
   - Express.js REST API
   - Jest テストフレームワーク
   - TypeScript

3. Relevant Files and Code:
   - src/controllers/userController.ts
      - getUsers() メソッドのテストが必要
      - DBからユーザー一覧を取得する関数
      ```typescript
      export async function getUsers(req: Request, res: Response) {
        const users = await UserModel.findAll();
        res.json(users);
      }
      ```
   - src/models/User.ts
      - UserModel の定義
      
4. Problem Solving:
   テストカバレッジが不足しているため、以下のテストケースを作成する：
   - 正常系：ユーザー一覧が返される
   - 異常系：DB接続エラー時の処理
   - 境界値：ユーザーが0件の場合

5. Pending Tasks and Next Steps:
   - Jest テストファイルの作成
   - テストの実行と結果確認
</context>
</new_task>
```

### コンテキスト引き継ぎの重要性

サブタスクは**新しいコンテキストウィンドウ**で開始されるため、必要な情報を明示的に渡す必要があります。

| 引き継ぐべき情報 | 説明 | 重要度 |
|----------------|------|--------|
| Current Work | 現在のタスクの状況 | ⭐⭐⭐ |
| Key Technical Concepts | 技術スタック・概念 | ⭐⭐⭐ |
| Relevant Files and Code | 関連ファイルと重要なコード断片 | ⭐⭐⭐ |
| Problem Solving | 問題の分析・解決方針 | ⭐⭐ |
| Pending Tasks | 残タスクと次のステップ | ⭐⭐ |

> **💡 ベストプラクティス**: コンテキストは**過不足なく**渡しましょう。多すぎるとトークンを浪費し、少なすぎるとサブエージェントが正しく動作しません。

---

## 5. Workflows（ワークフロー）詳解

### 概要

**Workflows**は、Clineに対して**事前に定義されたタスクの連鎖**を実行させる仕組みです。`.clinerules`ファイルやカスタムモードの指示に、ワークフローを記述することで実現できます。

> **公式ドキュメント**: https://docs.cline.bot/features/workflows

### ワークフローの定義方法

ワークフローは `.clinerules` ファイル内に**自然言語のステップ**として記述します：

```markdown
# 機能実装ワークフロー

以下のステップに従って機能を実装してください：

## Step 1: 要件分析
- ユーザーの要求を分析し、必要な機能を整理する
- 影響範囲を特定する
- 不明点があればユーザーに質問する

## Step 2: 設計
- ディレクトリ構造を確認する
- 既存コードとの整合性を確認する
- 設計方針をユーザーに提示する（Plan Mode）

## Step 3: 実装
- コードを作成する
- コーディング規約に従う
- 適切なエラーハンドリングを実装する

## Step 4: テスト作成
- ユニットテストを作成する
- 正常系・異常系・境界値を網羅する
- テストを実行して全てパスすることを確認する

## Step 5: レビュー
- 自身のコードをレビューする
- セキュリティ脆弱性がないか確認する
- パフォーマンスの問題がないか確認する

## Step 6: ドキュメント更新
- READMEを更新する（必要な場合）
- APIドキュメントを更新する（必要な場合）
- 変更履歴を記録する
```

### ワークフローとサブエージェントの組み合わせ

各ステップを**異なるカスタムモード**で実行することで、専門エージェントのパイプラインを構築できます：

```
Step 1: 要件分析    → 📐 Architect モード
Step 2: 設計       → 📐 Architect モード
Step 3: 実装       → 🛠️ Coder モード（デフォルト）
Step 4: テスト作成  → 🧪 Test Writer モード
Step 5: レビュー    → 🔍 Code Reviewer モード
Step 6: ドキュメント → 📝 Document Writer モード
```

---

## 6. .clinerules による行動制御

### 概要

`.clinerules` ファイルは、**Clineの行動ルールをプロジェクトごとに定義**するファイルです。サブエージェントの振る舞いを制御する基盤となります。

> **公式ドキュメント**: https://docs.cline.bot/features/cline-rules

### ファイル配置

```
プロジェクトルート/
├── .clinerules                    # 基本ルール（全モード共通）
├── .clinerules-code               # Code モード用ルール
├── .clinerules-architect           # Architect モード用ルール
├── .clinerules-code-reviewer       # Code Reviewer モード用ルール
├── .clinerules-test-writer         # Test Writer モード用ルール
├── .clinerules-debugger            # Debugger モード用ルール
└── src/
    └── ...
```

### ルールファイルの命名規則

| ファイル名 | 適用タイミング |
|-----------|--------------|
| `.clinerules` | 全モードで常に適用 |
| `.clinerules-{mode-slug}` | 特定モードのときのみ適用 |

### .clinerules の例（基本ルール）

```markdown
# プロジェクト基本ルール

## 技術スタック
- フロントエンド: React + TypeScript
- バックエンド: Node.js + Express
- データベース: MySQL 8.0
- テスト: Jest + React Testing Library
- パッケージマネージャ: npm

## コーディング規約
- インデント: スペース2つ
- セミコロン: あり
- クォート: シングルクォート
- 命名規則: camelCase（変数・関数）、PascalCase（クラス・コンポーネント）
- ファイル名: kebab-case

## コミットメッセージ規約
Conventional Commits形式を使用：
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント
- test: テスト
- refactor: リファクタリング

## セキュリティルール
- ハードコードされたパスワード・APIキーは禁止
- SQLインジェクション対策を必ず行うこと
- XSS対策を必ず行うこと
- 環境変数は .env ファイルで管理（.gitignore に追加済み）

## ディレクトリ構造
```
src/
├── controllers/     # APIコントローラー
├── models/          # データモデル
├── services/        # ビジネスロジック
├── middlewares/      # ミドルウェア
├── routes/          # ルーティング
├── utils/           # ユーティリティ
├── types/           # 型定義
└── __tests__/       # テストファイル
```
```

### .clinerules-code-reviewer の例

```markdown
# Code Reviewer モード専用ルール

## レビュー観点（優先度順）

### 🔴 Critical（必ず指摘）
1. セキュリティ脆弱性（SQLインジェクション、XSS、CSRF等）
2. データ破損の可能性があるバグ
3. 本番環境で障害を引き起こす可能性のあるコード
4. ハードコードされた秘密情報（パスワード、APIキー）

### 🟡 Warning（改善推奨）
1. エラーハンドリングの不足
2. パフォーマンスの問題（N+1クエリ等）
3. DRY原則の違反（重複コード）
4. 型安全性の不足

### 🟢 Info（参考情報）
1. 命名の改善提案
2. コメントの追加推奨箇所
3. テストカバレッジの改善提案
4. リファクタリングの提案

## 出力フォーマット

レビュー結果は以下の形式で出力すること：

```markdown
# コードレビュー結果

## 対象ファイル
- ファイル名: xxx
- レビュー日時: YYYY-MM-DD

## 指摘事項

### 🔴 Critical
| No. | ファイル | 行 | 内容 | 修正案 |
|-----|---------|-----|------|--------|
| 1   | xxx.ts  | 42  | ...  | ...    |

### 🟡 Warning
...

### 🟢 Info
...

## 総合評価
- 品質スコア: X/10
- マージ可否: 可/条件付き可/不可
```
```

### .clinerules-test-writer の例

```markdown
# Test Writer モード専用ルール

## テスト方針
- カバレッジ目標: 80%以上
- テストフレームワーク: Jest
- モック: jest.mock() を使用
- 非同期テスト: async/await を使用

## テストファイル配置
- テストファイルは `src/__tests__/` ディレクトリに配置
- ファイル名: `{対象ファイル名}.test.ts`

## テストケースの命名規則
describe/it の記述は日本語で記述すること：

```typescript
describe('UserService', () => {
  describe('getUsers', () => {
    it('正常系: ユーザー一覧が返されること', async () => { ... });
    it('異常系: DB接続エラー時にエラーを投げること', async () => { ... });
    it('境界値: ユーザーが0件の場合に空配列が返ること', async () => { ... });
  });
});
```

## 必須テストパターン
1. **正常系**: 期待通りの入力で期待通りの結果
2. **異常系**: 異常な入力、エラー時の挙動
3. **境界値**: 空配列、null、undefined、最大値
4. **副作用**: DB変更、ファイル変更が正しいか

## テスト実行コマンド
```bash
npx jest --coverage
```
```

---

## 7. 実践例：コードレビューサブエージェント

### ユースケース

プロジェクトのPR（Pull Request）やコード変更を自動的にレビューするサブエージェントを構築します。

### Step 1: カスタムモードを定義

`C:\Users\YJSNOTE14\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_custom_modes.json` に追加：

```json
{
  "customModes": [
    {
      "slug": "code-reviewer",
      "name": "🔍 Code Reviewer",
      "roleDefinition": "あなたは10年以上の経験を持つシニアコードレビュアーです。コードの品質、可読性、パフォーマンス、セキュリティを厳密にチェックします。具体的な改善案を提示し、コードの良い点も評価してください。レビュー結果はMarkdown形式でまとめます。",
      "groups": [
        "read",
        ["edit", {
          "fileRegex": "review-report.*\\.md$",
          "description": "レビューレポートのMarkdownファイルのみ作成・編集可能"
        }],
        "command"
      ],
      "customInstructions": "レビュー実施手順:\n1. 対象ファイルを全て読み込む\n2. 各ファイルを以下の観点でチェック:\n   - セキュリティ脆弱性\n   - エラーハンドリング\n   - パフォーマンス\n   - 可読性\n   - テスト可能性\n3. 指摘事項をCritical/Warning/Infoに分類\n4. review-report.md に結果を出力"
    }
  ]
}
```

### Step 2: レビューモード用のルールファイルを作成

プロジェクトルートに `.clinerules-code-reviewer` を作成：

```markdown
# Code Reviewer 専用ルール

## レビュー対象
- src/ ディレクトリ以下の .ts, .tsx ファイル
- 直近の git diff で変更されたファイル

## チェック項目
1. TypeScript の型安全性
2. React hooks のルール遵守
3. API呼び出しのエラーハンドリング
4. SQL インジェクション対策
5. 環境変数のハードコーディング
6. console.log の残存チェック
7. TODO/FIXME コメントの確認

## 出力
review-report.md に結果をまとめること
```

### Step 3: Clineでの使い方

```
1. VS Code サイドバーの Cline パネルを開く
2. モードセレクターから「🔍 Code Reviewer」を選択
3. チャットに以下のように入力:

   「src/controllers/userController.ts と
    src/services/userService.ts をレビューしてください」

4. Code Reviewer サブエージェントが以下を実行:
   - 対象ファイルを読み込み
   - 各観点でコードを分析
   - review-report.md にレビュー結果を出力
```

### レビュー結果の出力例

```markdown
# コードレビュー結果

## 対象ファイル
- src/controllers/userController.ts
- src/services/userService.ts
- レビュー日時: 2026-04-07

## 🔴 Critical（必ず修正）

| No. | ファイル | 行 | 内容 | 修正案 |
|-----|---------|-----|------|--------|
| 1 | userController.ts | 28 | SQLクエリに直接ユーザー入力を埋め込んでいる | パラメータバインディングを使用 |
| 2 | userService.ts | 15 | try-catch が無く、DB エラーが握りつぶされる | 適切なエラーハンドリングを追加 |

## 🟡 Warning（改善推奨）

| No. | ファイル | 行 | 内容 | 修正案 |
|-----|---------|-----|------|--------|
| 1 | userController.ts | 12 | レスポンスの型が any になっている | 適切な型定義を追加 |
| 2 | userService.ts | 30 | N+1 クエリが発生している | JOIN または一括取得に変更 |

## 🟢 Info（参考情報）

| No. | ファイル | 行 | 内容 |
|-----|---------|-----|------|
| 1 | userController.ts | 5 | バリデーションロジックの共通化を推奨 |

## 総合評価
- 品質スコア: 6/10
- マージ可否: 条件付き可（Critical 2件の修正後）
```

---

## 8. 実践例：テスト自動生成サブエージェント

### ユースケース

既存のソースコードに対して、自動的にテストコードを生成するサブエージェントを構築します。

### Step 1: カスタムモードを定義

```json
{
  "slug": "test-writer",
  "name": "🧪 Test Writer",
  "roleDefinition": "あなたはテストエンジニアです。与えられたソースコードに対して、Jest を使用した包括的なテストコードを作成します。正常系・異常系・境界値を網羅し、テストカバレッジの最大化を目指します。",
  "groups": [
    "read",
    ["edit", {
      "fileRegex": "\\.(test|spec)\\.(ts|js|tsx|jsx)$",
      "description": "テストファイルのみ編集可能"
    }],
    "command"
  ],
  "customInstructions": "テスト作成手順:\n1. 対象ファイルを読み込み、関数・クラスを特定\n2. 各関数の入出力を分析\n3. テストケースを設計（正常系・異常系・境界値）\n4. テストコードを作成\n5. npx jest で実行して確認\n6. 失敗するテストがあれば修正"
}
```

### Step 2: New Task Tool でテスト生成を委任

メインタスク内から、テスト生成をサブタスクとして委任する例：

```xml
<new_task>
<context>
1. Current Work:
   UserService クラスのユニットテストを作成する

2. Key Technical Concepts:
   - TypeScript + Jest
   - mysql2/promise でのDB操作
   - async/await パターン

3. Relevant Files and Code:
   - src/services/userService.ts
      - テスト対象のメインファイル
      ```typescript
      import { Pool } from 'mysql2/promise';

      export class UserService {
        constructor(private pool: Pool) {}

        async getUsers(): Promise<User[]> {
          const [rows] = await this.pool.execute('SELECT * FROM users');
          return rows as User[];
        }

        async getUserById(id: number): Promise<User | null> {
          const [rows] = await this.pool.execute(
            'SELECT * FROM users WHERE id = ?', [id]
          );
          const users = rows as User[];
          return users.length > 0 ? users[0] : null;
        }

        async createUser(name: string, email: string): Promise<User> {
          const [result] = await this.pool.execute(
            'INSERT INTO users (name, email) VALUES (?, ?)',
            [name, email]
          );
          return { id: (result as any).insertId, name, email };
        }
      }
      ```
   
   - src/types/user.ts
      ```typescript
      export interface User {
        id: number;
        name: string;
        email: string;
        created_at?: Date;
      }
      ```

4. Problem Solving:
   UserService の全メソッドに対してテストを作成する必要がある。
   DB操作はモック化し、実際のDB接続は不要にする。

5. Pending Tasks and Next Steps:
   - テストファイル src/__tests__/userService.test.ts を作成
   - 全テストがパスすることを確認
   - カバレッジレポートを出力
</context>
</new_task>
```

### Step 3: 生成されるテストコードの例

```typescript
// src/__tests__/userService.test.ts
import { UserService } from '../services/userService';
import { Pool } from 'mysql2/promise';

// MySQL Pool のモック
const mockPool = {
  execute: jest.fn(),
} as unknown as Pool;

describe('UserService', () => {
  let userService: UserService;

  beforeEach(() => {
    userService = new UserService(mockPool);
    jest.clearAllMocks();
  });

  describe('getUsers', () => {
    it('正常系: ユーザー一覧が返されること', async () => {
      // Arrange
      const mockUsers = [
        { id: 1, name: '田中太郎', email: 'tanaka@example.com' },
        { id: 2, name: '鈴木花子', email: 'suzuki@example.com' },
      ];
      (mockPool.execute as jest.Mock).mockResolvedValue([mockUsers]);

      // Act
      const result = await userService.getUsers();

      // Assert
      expect(result).toEqual(mockUsers);
      expect(mockPool.execute).toHaveBeenCalledWith('SELECT * FROM users');
    });

    it('境界値: ユーザーが0件の場合に空配列が返ること', async () => {
      (mockPool.execute as jest.Mock).mockResolvedValue([[]]);

      const result = await userService.getUsers();

      expect(result).toEqual([]);
    });

    it('異常系: DB接続エラー時にエラーが伝播すること', async () => {
      (mockPool.execute as jest.Mock).mockRejectedValue(
        new Error('Connection refused')
      );

      await expect(userService.getUsers()).rejects.toThrow('Connection refused');
    });
  });

  describe('getUserById', () => {
    it('正常系: 指定IDのユーザーが返されること', async () => {
      const mockUser = { id: 1, name: '田中太郎', email: 'tanaka@example.com' };
      (mockPool.execute as jest.Mock).mockResolvedValue([[mockUser]]);

      const result = await userService.getUserById(1);

      expect(result).toEqual(mockUser);
      expect(mockPool.execute).toHaveBeenCalledWith(
        'SELECT * FROM users WHERE id = ?',
        [1]
      );
    });

    it('正常系: 存在しないIDの場合にnullが返ること', async () => {
      (mockPool.execute as jest.Mock).mockResolvedValue([[]]);

      const result = await userService.getUserById(999);

      expect(result).toBeNull();
    });
  });

  describe('createUser', () => {
    it('正常系: 新規ユーザーが作成されること', async () => {
      (mockPool.execute as jest.Mock).mockResolvedValue([{ insertId: 3 }]);

      const result = await userService.createUser('新規ユーザー', 'new@example.com');

      expect(result).toEqual({
        id: 3,
        name: '新規ユーザー',
        email: 'new@example.com',
      });
    });
  });
});
```

---

## 9. 実践例：マルチエージェントオーケストレーション

### ユースケース

複数のサブエージェントを**パイプライン**として連携させ、1つの機能実装を完了する。

### アーキテクチャ

```
ユーザー: 「ユーザー管理APIを実装して」
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│                メインエージェント (Orchestrator)           │
│                                                         │
│  Step 1 ─────► 📐 Architect サブエージェント              │
│                 └→ API設計書・DB設計書を作成               │
│                    └→ design-docs/api-design.md          │
│                                                         │
│  Step 2 ─────► 🛠️ Coder サブエージェント                  │
│                 └→ 設計書に基づきコードを実装               │
│                    └→ src/controllers/                    │
│                    └→ src/services/                       │
│                    └→ src/models/                         │
│                                                         │
│  Step 3 ─────► 🧪 Test Writer サブエージェント             │
│                 └→ 実装コードに対するテストを作成            │
│                    └→ src/__tests__/                      │
│                                                         │
│  Step 4 ─────► 🔍 Code Reviewer サブエージェント           │
│                 └→ コード品質をレビュー                     │
│                    └→ review-report.md                    │
│                                                         │
│  Step 5 ─────► 🛠️ Coder サブエージェント（修正）           │
│                 └→ レビュー指摘に基づき修正                 │
│                                                         │
│  完了 ──────► ユーザーに結果を報告                          │
└─────────────────────────────────────────────────────────┘
```

### .clinerules でオーケストレーションを定義

```markdown
# マルチエージェント・オーケストレーション ワークフロー

新しい機能を実装する際は、以下のパイプラインに従ってください。
各ステップは、対応するカスタムモードに切り替えて実行してください。

## Step 1: 設計フェーズ（📐 Architect モードに切り替え）
1. 要件を分析し、API仕様を設計する
2. DB設計（テーブル定義）を作成する
3. 設計ドキュメントを `design-docs/` に出力する
4. 設計完了後、ユーザーにレビューを依頼する

## Step 2: 実装フェーズ（🛠️ Code モードに切り替え）
1. Step 1 の設計書を読み込む
2. コントローラー、サービス、モデルを実装する
3. ルーティングを設定する
4. エラーハンドリングを実装する

## Step 3: テストフェーズ（🧪 Test Writer モードに切り替え）
1. Step 2 で作成されたコードを読み込む
2. 全メソッドに対するユニットテストを作成する
3. テストを実行し、全てパスすることを確認する
4. カバレッジレポートを出力する

## Step 4: レビューフェーズ（🔍 Code Reviewer モードに切り替え）
1. Step 2-3 の成果物をレビューする
2. Critical/Warning/Info に分類して指摘する
3. review-report.md に結果を出力する

## Step 5: 修正フェーズ（🛠️ Code モードに切り替え）
1. Step 4 のレビュー指摘を読み込む
2. Critical と Warning を全て修正する
3. テストが全てパスすることを確認する
```

### Cline CLI を使ったオーケストレーション

Cline CLI のHeadless Modeを使って、スクリプトからオーケストレーションすることも可能です：

```bash
#!/bin/bash
# orchestrate.sh - マルチエージェントオーケストレーション

PROJECT_DIR="/path/to/project"

echo "=== Step 1: 設計 ==="
cline --headless \
  --model claude-sonnet-4-20250514 \
  "ユーザー管理APIの設計書を作成して。\
   API仕様とDB設計をdesign-docs/ディレクトリに出力して。" \
  --output "$PROJECT_DIR/design-docs/api-design.md"

echo "=== Step 2: 実装 ==="
cline --headless \
  --model claude-sonnet-4-20250514 \
  "@design-docs/api-design.md この設計書に基づいてAPIを実装して。\
   Express + TypeScript で実装すること。"

echo "=== Step 3: テスト ==="
cline --headless \
  --model claude-sonnet-4-20250514 \
  "src/controllers/ と src/services/ のコードに対して\
   Jestユニットテストを作成して実行して。"

echo "=== Step 4: レビュー ==="
cline --headless \
  --model claude-sonnet-4-20250514 \
  "src/ ディレクトリのコードをレビューして。\
   結果を review-report.md に出力して。" \
  --output "$PROJECT_DIR/review-report.md"

echo "=== 完了 ==="
echo "レビューレポート: $PROJECT_DIR/review-report.md"
```

---

## 10. 実践例：設計書→コード生成パイプライン

### ユースケース

Excel設計書をMCPサーバーで読み込み、カスタムサブエージェントで段階的にコードを生成する。

### パイプライン構成

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Excel   │────▶│ MCP Server   │────▶│ 📐 Architect │────▶│ 🛠️ Coder     │
│ 設計書   │     │ (読み込み)    │     │ (設計分析)    │     │ (コード生成)  │
└─────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                │
                                           ┌────────────────────┘
                                           ▼
                                    ┌──────────────┐     ┌──────────────┐
                                    │ 🧪 Tester    │────▶│ 🔍 Reviewer  │
                                    │ (テスト生成)   │     │ (品質確認)    │
                                    └──────────────┘     └──────────────┘
```

### 実行手順

```
1. ユーザー: 「設計書.xlsx を読んでAPIを実装して」

2. Cline（メインエージェント）:
   a. MCP ツールで設計書を読み込み
      → use_mcp_tool: design-doc-server / parse_api_spec
      → use_mcp_tool: design-doc-server / parse_db_spec
   
   b. 📐 Architect モードに切り替え（またはサブタスク生成）
      → 設計書の内容を分析
      → 実装方針を策定
   
   c. 🛠️ Coder モードに切り替え
      → DB マイグレーションファイル生成
      → Model 生成
      → Service 生成
      → Controller 生成
      → Router 生成
   
   d. 🧪 Test Writer モードに切り替え
      → 各コンポーネントのテスト生成
      → テスト実行

3. 完了報告
```

---

## 11. サブエージェントの設定手順（Step-by-Step）

以下の手順に従って、カスタムサブエージェントを一から設定できます。

### Step 1: カスタムモードの設定ファイルを開く

**方法A: VS Code の設定から開く**

```
1. VS Code を開く
2. Cline パネルを開く（サイドバー）
3. 設定アイコン（⚙️）をクリック
4. 「Custom Modes」セクションを探す
```

**方法B: 直接ファイルを編集する**

設定ファイルのパス（Windows）:
```
C:\Users\YJSNOTE14\AppData\Roaming\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_custom_modes.json
```

> **⚠️ 注意**: ファイルが存在しない場合は新規作成してください。

### Step 2: カスタムモードのJSON定義を作成

ファイルに以下の構造でモードを定義します：

```json
{
  "customModes": [
    {
      "slug": "my-agent-slug",
      "name": "🤖 My Custom Agent",
      "roleDefinition": "このエージェントの役割と専門性を詳細に記述する",
      "groups": [
        "read",
        "edit",
        "command"
      ],
      "customInstructions": "追加の指示やルールをここに記述"
    }
  ]
}
```

各フィールドの説明：

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `slug` | ✅ | モードの識別子（英数字・ハイフン、例: `code-reviewer`） |
| `name` | ✅ | モードの表示名（絵文字推奨、例: `🔍 Code Reviewer`） |
| `roleDefinition` | ✅ | エージェントの役割定義（詳細であるほど効果的） |
| `groups` | ✅ | 使用可能なツールグループの配列 |
| `customInstructions` | ❌ | 追加の指示（モード固有のルール） |

### Step 3: プロジェクト固有のモード定義（.roomodes）

プロジェクトルートに `.roomodes` ファイルを作成して、**プロジェクト固有のカスタムモード**を定義することもできます：

```json
// プロジェクトルート/.roomodes
{
  "customModes": [
    {
      "slug": "spring-boot-dev",
      "name": "☕ Spring Boot Developer",
      "roleDefinition": "あなたはSpring Boot の専門家です。Java 17 + Spring Boot 3.x + Gradle を使用したバックエンド開発を担当します。",
      "groups": [
        "read",
        ["edit", {
          "fileRegex": "\\.(java|gradle|properties|yml|yaml|xml)$",
          "description": "Java関連ファイルのみ編集可能"
        }],
        "command",
        "mcp"
      ],
      "customInstructions": "Spring Boot の規約:\n- @RestController でREST API実装\n- @Service でビジネスロジック\n- @Repository でデータアクセス\n- DTO パターンを使用\n- Lombok を活用"
    }
  ]
}
```

### Step 4: モード専用の .clinerules を作成

プロジェクトルートに `.clinerules-{slug}` ファイルを作成します：

```bash
# プロジェクトルートで実行
# 例: code-reviewer モード用
touch .clinerules-code-reviewer
```

`.clinerules-code-reviewer` の内容を記述：

```markdown
# Code Reviewer 専用ルール

## このモードの目的
コードの品質、セキュリティ、パフォーマンスを評価し、
改善点を report ファイルに出力する。

## レビューチェックリスト
- [ ] 型安全性の確認
- [ ] エラーハンドリングの確認
- [ ] セキュリティ脆弱性の確認
- [ ] パフォーマンスの確認
- [ ] テスタビリティの確認
- [ ] コーディング規約の遵守

## 出力先
review-report-YYYY-MM-DD.md に出力すること
```

### Step 5: VS Code でモードを切り替え

```
1. Cline パネルを開く
2. チャット入力欄の上にある モードセレクター をクリック
3. 作成したカスタムモード（例: 🔍 Code Reviewer）を選択
4. モードが切り替わり、そのモードのルールが適用される
5. タスクを入力して実行
```

モードセレクターのイメージ：

```
┌─────────────────────────────────────────┐
│  モード選択:                              │
│  ┌─────────────────────────────────────┐ │
│  │ 🔧 Code (default)              ✓  │ │
│  │ 📐 Architect                      │ │
│  │ 🔍 Code Reviewer                  │ │
│  │ 🧪 Test Writer                    │ │
│  │ 🐛 Debugger                       │ │
│  │ ☕ Spring Boot Developer           │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Step 6: ワークフローを定義（オプション）

複数のモードを順番に使うワークフローを `.clinerules` に定義：

```markdown
# ワークフロー定義

## 新機能実装ワークフロー
新機能の実装を依頼された場合は以下のフローで進めてください:

1. まず Plan Mode で設計を確認
2. 設計承認後、Act Mode で実装
3. 実装後、テストを作成して実行
4. 全テストがパスしたら完了報告
```

### Step 7: 動作確認

```
1. Cline パネルでモードを切り替え
2. テストタスクを入力:
   例: 「src/app.ts をレビューしてください」
3. エージェントが指定されたルールに従って動作することを確認
4. ツールの制限（editの制限等）が正しく機能していることを確認
5. 出力フォーマットが指定通りであることを確認
```

---

## 12. ベストプラクティスと注意点

### ✅ ベストプラクティス

#### 1. 役割定義は具体的かつ詳細に

```
❌ 悪い例:
"roleDefinition": "コードレビューをする"

✅ 良い例:
"roleDefinition": "あなたは10年以上の経験を持つシニアコードレビュアーです。
TypeScript、React、Node.js プロジェクトのコード品質を評価します。
セキュリティ脆弱性、パフォーマンスの問題、可読性の改善点を
具体的なコード例付きで指摘してください。
指摘は Critical/Warning/Info に分類し、
修正の優先度が明確にわかるようにしてください。"
```

#### 2. ツールグループは最小権限の原則で

```json
// レビュアーはコードを読むだけ、レポートのみ書ける
"groups": [
  "read",
  ["edit", { "fileRegex": "review-.*\\.md$" }]
]

// テスターはテストファイルのみ書ける
"groups": [
  "read",
  ["edit", { "fileRegex": "\\.(test|spec)\\." }],
  "command"
]
```

#### 3. サブタスクのコンテキストは過不足なく

```
❌ 悪い例（情報不足）:
"テストを書いて"

❌ 悪い例（情報過多）:
"全ファイルの内容を貼り付け..."

✅ 良い例:
"UserService.getUsers() メソッドのテストを書いて。
 メソッドのシグネチャは: async getUsers(): Promise<User[]>
 DB操作: mysql2/promise の Pool.execute() を使用
 テストフレームワーク: Jest
 モック方針: Pool をモック化"
```

#### 4. 出力フォーマットを明確に定義

```markdown
# レビュー結果は以下のフォーマットで出力すること

## フォーマット
| 重要度 | ファイル | 行 | 問題 | 修正案 |
|--------|---------|-----|------|--------|
| 🔴    | xxx.ts  | 42  | ...  | ...    |
```

#### 5. 段階的に構築する

```
レベル1: .clinerules だけで基本ルールを定義
    ↓
レベル2: カスタムモードを1-2個追加
    ↓
レベル3: モード専用の .clinerules-{slug} を追加
    ↓
レベル4: ワークフローを定義
    ↓
レベル5: New Task Tool でサブタスク分解を導入
    ↓
レベル6: MCP サーバーと組み合わせた高度な連携
```

### ⚠️ 注意点

| 注意点 | 詳細 |
|--------|------|
| **コンテキスト制限** | サブタスクは新しいコンテキストウィンドウで開始されるため、必要な情報を明示的に渡す |
| **モード切り替えのコスト** | モード切り替え時にコンテキストがリセットされる場合がある |
| **ファイル制限の正規表現** | `fileRegex` の正規表現が正確でないと、意図しないファイルが編集される |
| **ルールの競合** | `.clinerules` と `.clinerules-{slug}` の内容が矛盾しないように注意 |
| **トークン消費** | サブタスクを生成するたびにトークンを消費するため、不必要なサブタスク分割は避ける |
| **API コスト** | マルチエージェントパイプラインはAPI呼び出し回数が増えるため、コストに注意 |

---

## 13. トラブルシューティング

### 問題1: カスタムモードが表示されない

```
原因: JSON の構文エラー

対処法:
1. JSON ファイルの構文を確認（カンマの有無、括弧の対応等）
2. VS Code の拡張機能を再起動（Ctrl+Shift+P → "Developer: Reload Window"）
3. JSON バリデーターで構文チェック
```

### 問題2: ファイル制限が効かない

```
原因: fileRegex の正規表現が間違っている

対処法:
1. 正規表現をテスト（regex101.com 等で確認）
2. バックスラッシュはJSONでエスケープが必要（\\ → \\\\）
3. 例: \.test\.ts$ → \\.test\\.ts$
```

### 問題3: モード専用の .clinerules が適用されない

```
原因: ファイル名がモードの slug と一致しない

対処法:
1. ファイル名を確認: .clinerules-{slug} の {slug} がモード定義の slug と完全一致するか
2. ファイルがプロジェクトルートに配置されているか確認
3. 例: slug が "code-reviewer" なら .clinerules-code-reviewer
```

### 問題4: サブタスクが正しく動作しない

```
原因: コンテキストの引き継ぎが不十分

対処法:
1. new_task の context パラメータに必要な情報が全て含まれているか確認
2. 関連するコードの断片を含めているか確認
3. 技術スタックの情報を含めているか確認
4. 期待する出力フォーマットを明記しているか確認
```

### 問題5: ワークフローが途中で止まる

```
原因: Plan Mode と Act Mode の切り替えが必要

対処法:
1. ワークフローの各ステップで Act Mode であることを確認
2. 承認が必要な操作がないか確認
3. Auto Approve 設定を確認（信頼できるタスクの場合）
```

---

## 14. 参考リンク集

| リソース | URL |
|---------|-----|
| Cline 公式ドキュメント | https://docs.cline.bot |
| Custom Modes | https://docs.cline.bot/features/custom-modes |
| Cline Rules | https://docs.cline.bot/features/cline-rules |
| New Task Tool | https://docs.cline.bot/cline-tools/new-task-tool |
| Workflows | https://docs.cline.bot/features/workflows |
| Plan & Act Mode | https://docs.cline.bot/features/plan-and-act |
| Auto Approve | https://docs.cline.bot/features/auto-approve |
| MCP Overview | https://docs.cline.bot/mcp/overview |
| Cline CLI Overview | https://docs.cline.bot/cline-cli/overview |
| Cline GitHub | https://github.com/cline/cline |

---

## 📝 まとめ

### カスタムサブエージェントの構成要素

| 要素 | 目的 | 設定場所 |
|------|------|---------|
| **Custom Modes** | エージェントの役割・権限定義 | `cline_custom_modes.json` / `.roomodes` |
| **.clinerules** | プロジェクト固有の行動ルール | プロジェクトルート |
| **.clinerules-{slug}** | モード固有の行動ルール | プロジェクトルート |
| **New Task Tool** | サブタスクの動的生成 | タスク実行中に使用 |
| **Workflows** | 事前定義されたタスクチェーン | `.clinerules` に記述 |
| **MCP Server** | 外部システム連携 | `cline_mcp_settings.json` |

### 推奨する導入ステップ

```
初級者:
  1. .clinerules を作成してプロジェクトルールを定義
  2. 基本的なワークフローを記述

中級者:
  3. カスタムモードを2-3個定義（レビュアー、テスター等）
  4. モード専用の .clinerules-{slug} を作成
  5. モード切り替えによるサブエージェント運用

上級者:
  6. New Task Tool でサブタスク分解を導入
  7. MCP サーバーと連携した高度なワークフロー
  8. Cline CLI を使ったオーケストレーション自動化
```

> 💡 **ヒント**: まずは `.clinerules` と1つのカスタムモード（Code Reviewer 推奨）から始めて、徐々に拡張していくのが最も効果的です。いきなり全ての仕組みを導入しようとすると複雑になりすぎます。