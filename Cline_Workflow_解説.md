# Cline Workflow（ワークフロー）完全ガイド

> バージョン: Cline v3.x 系  
> 最終更新: 2026-04-14  
> 参考: [Cline 公式ドキュメント](https://docs.cline.bot/features)

---

## 目次

1. [Workflowとは](#1-workflowとは)
2. [Workflowのメリット](#2-workflowのメリット)
3. [Workflowの基本構成](#3-workflowの基本構成)
4. [Workflowの作成方法](#4-workflowの作成方法)
5. [Workflowの実行方法](#5-workflowの実行方法)
6. [関連機能との比較・連携](#6-関連機能との比較連携)
7. [まとめ](#7-まとめ)

---

## 1. Workflowとは

### 概要

**Cline Workflow**は、繰り返し行うタスクを**再利用可能なテンプレート**として定義し、ワンクリックまたはスラッシュコマンドで実行できるようにする機能です。

通常のCline利用では、毎回タスクの指示をチャットに入力する必要がありますが、Workflowを使うと：

- あらかじめ定義した手順をそのまま再実行できる
- チーム全体で統一された作業手順を共有できる
- 複雑なマルチステップの作業を一つのコマンドで開始できる

### イメージ図

```
通常の利用:
  ユーザー → [毎回手動で指示を入力] → Cline が実行

Workflow利用:
  ユーザー → [Workflowを選択/実行] → 事前定義された指示 → Cline が実行
```

---

## 2. Workflowのメリット

| メリット | 説明 |
|---|---|
| **再利用性** | 一度定義すれば、何度でも同じ手順を実行可能 |
| **一貫性** | チームメンバー全員が同じプロセスに従える |
| **効率化** | 複雑な指示を毎回入力する手間を削減 |
| **品質向上** | 定義済みの手順でミスを防止 |
| **オンボーディング** | 新メンバーもすぐにベストプラクティスを活用可能 |

---

## 3. Workflowの基本構成

### 3.1 Workflowの定義場所

Cline Workflowは、プロジェクトの `.cline/` ディレクトリ内に定義ファイルとして保存されます。

```
プロジェクトルート/
├── .cline/
│   └── workflows/
│       ├── code-review.md
│       ├── deploy.md
│       └── create-component.md
├── src/
└── ...
```

### 3.2 Workflowファイルの構造

Workflowファイルは**Markdown形式**で記述します。Clineはこのファイルの内容を指示として読み込み、ステップに従って実行します。

基本構造：

```markdown
# Workflow名

## 説明
このワークフローの目的と概要

## ステップ

### Step 1: [ステップ名]
具体的な指示内容

### Step 2: [ステップ名]
具体的な指示内容

### Step 3: [ステップ名]
具体的な指示内容
```

### 3.3 Workflowの構成要素

| 要素 | 説明 | 必須 |
|---|---|---|
| **タイトル** | Workflowの名前（UIに表示される） | ✅ |
| **説明** | Workflowの目的・概要 | 推奨 |
| **ステップ** | Clineが実行する具体的な指示 | ✅ |
| **変数/パラメータ** | 実行時にユーザーが指定する入力値 | ❌ |

### 3.4 命名規則

```
✅ 良い例:
  - code-review.md
  - create-react-component.md
  - deploy-staging.md

❌ 悪い例:
  - workflow1.md
  - test.md
  - new.md
```

---

## 4. Workflowの作成方法

### 方法1: Cline UIから作成

1. VSCodeのClineサイドパネルを開く
2. 設定アイコン（⚙️）をクリック
3. 「Workflows」セクションに移動
4. 「+ New Workflow」ボタンをクリック
5. Workflow名と内容を入力
6. 保存

### 方法2: ファイルを直接作成

プロジェクトルートの `.cline/workflows/` ディレクトリにMarkdownファイルを作成します。

#### 例: コードレビューWorkflow

```markdown
# コードレビュー

## 説明
変更されたファイルをレビューし、コード品質のフィードバックを提供します。

## ステップ

### Step 1: 変更ファイルの特定
gitで変更されたファイルを確認してください:
- `git diff --name-only` を実行
- 変更ファイルの一覧を把握

### Step 2: コードの分析
各変更ファイルについて以下を確認:
- コーディング規約への準拠
- 潜在的なバグやセキュリティリスク
- パフォーマンスの問題
- テストの有無

### Step 3: レビュー結果の報告
以下の形式でレビュー結果をまとめてください:
- ファイルごとの問題点
- 改善提案
- 全体的な評価
```

---

## 5. Workflowの実行方法

### 5.1 Cline UIから実行

1. Clineチャットパネルを開く
2. メッセージ入力欄の付近にある **Workflows** ボタン（または⚡アイコン）をクリック
3. 利用可能なWorkflow一覧が表示される
4. 実行したいWorkflowを選択
5. 必要に応じてパラメータを入力
6. Clineが自動的にステップを実行開始

### 5.2 チャットから実行

チャット入力欄でWorkflowの内容を参照して指示することも可能です：

```
「コードレビュー」のWorkflowを実行してください
```

### 5.3 実行の流れ

```
Workflow選択 → パラメータ入力（必要な場合）→ Clineがステップを順次実行
                                                    ↓
                                              各ステップでツールを使用
                                              （read_file, execute_command等）
                                                    ↓
                                              結果をユーザーに報告
```

---

## 6. 関連機能との比較・連携

### 6.1 Workflow vs Cline Rules vs Skills

| 機能 | 目的 | スコープ | 使い方 |
|---|---|---|---|
| **Workflow** | 再利用可能なタスクテンプレート | タスク単位 | UIまたはコマンドで選択・実行 |
| **Cline Rules** (`.clinerules`) | Clineの動作ルール・制約の定義 | プロジェクト全体 | 自動的に適用される |
| **Skills** (`.claude/skills/`) | 専門的な知識・手順の提供 | 特定タスク | `use_skill` で有効化 |

### 6.2 各機能の使い分け

```
┌─────────────────────────────────────────────────┐
│                Cline Rules                       │
│  プロジェクト全体に適用されるルール               │
│  例: コーディング規約、使用言語、禁止事項          │
├─────────────────────────────────────────────────┤
│          │                    │                  │
│     Workflow                Skills               │
│     タスクの実行手順         専門知識の提供         │
│     例: PR作成手順           例: 設計書解析         │
│         デプロイ手順             Excel解析          │
│         テスト作成               勉強ノート作成     │
└─────────────────────────────────────────────────┘
```

### 6.3 MCP（Model Context Protocol）との連携

Workflowのステップ内でMCPツールを活用できます：

```markdown
### Step: Backlogにチケット作成
MCPサーバー(backlog)を使用して、
レビュー結果をBacklogのチケットとして作成してください。
```

---

## 7. まとめ

### Cline Workflowの要点

| 項目 | 内容 |
|---|---|
| **何ができるか** | 繰り返しタスクをテンプレート化して再利用 |
| **どこに定義するか** | `.cline/workflows/` ディレクトリ内のMarkdownファイル |
| **どう実行するか** | Cline UIのWorkflowボタン、またはチャットで指示 |
| **誰に向いているか** | 定型的な作業が多いチーム・個人開発者 |

### 活用フロー

```
1. よく行うタスクを特定
      ↓
2. Workflowファイルを作成（.cline/workflows/）
      ↓
3. チームで共有（Git管理）
      ↓
4. 必要な時にWorkflowを実行
      ↓
5. 結果を確認・フィードバック
      ↓
6. Workflowを改善
```

---

## 参考リンク

- [Cline 公式ドキュメント - Features](https://docs.cline.bot/features)
- [Cline Workflows](https://docs.cline.bot/features/workflows)
- [Cline Rules](https://docs.cline.bot/features/cline-rules)
- [Plan & Act Mode](https://docs.cline.bot/features/plan-and-act)
- [Cline Tools Reference](https://docs.cline.bot/cline-tools)
- [MCP Overview](https://docs.cline.bot/mcp)

---

> 📝 **補足**: Clineは活発に開発が進んでいるため、Workflow機能の詳細はバージョンアップにより変更される可能性があります。最新情報は[公式ドキュメント](https://docs.cline.bot)を参照してください。