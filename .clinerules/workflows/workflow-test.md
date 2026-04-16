# Excel設計書 → 詳細設計書 自動生成ワークフロー

## 概要
Excel業務機能設計書を3つのスキルを連携させて、自動的に詳細設計書（Markdown）まで変換するワークフローです。

## ワークフロー全体像

```mermaid
graph LR
    A[Excel設計書] -->|Step1| B[解析結果MD]
    B -->|Step2| C[分析レポートMD]
    C -->|Step3| D[詳細設計書MD]
    
    style A fill:#f9f,stroke:#333
    style D fill:#9f9,stroke:#333
```

## 実行手順

### Step1: excel-parse（Excel設計書解析）

**スキル名:** `excel-parse`  
**入力:** Excel業務機能設計書（`.xlsx`）  
**出力:** 解析結果Markdown（`output/parse_result/`）

```bash
# スキルを有効化
use_skill: excel-parse

# 解析スクリプトを実行
py .agents/skills/excel-parse/scripts/excel_to_md.py --input "<入力Excelパス>" --output "output/parse_result/<機能ID>_parse.md"
```

**処理内容:**
- Excelシートの自動分類（変更履歴、仕様概要、画面項目定義、画面遷移図など）
- 各シートに対応するパーサーで構造化データを抽出
- 画面遷移図の図形からMermaid記法を自動生成
- Markdown形式で統合出力

---

### Step2: design-analyzer（設計分析）

**スキル名:** `design-analyzer`  
**入力:** Step1の解析結果Markdown  
**出力:** 設計分析レポート（`output/analysis_result/`）

```bash
# スキルを有効化
use_skill: design-analyzer

# Step1の解析結果を読み込み、以下の観点で分析レポートを生成:
# - ソースコード構成サマリ（クラス一覧の導出）
# - 処理フロー構成（処理間依存関係の可視化）
# - 画面項目構成分析
# - テーブル設計分析（マッピング整合性チェック）
# - 潜在的な問題の検出
# - DTO構造の導出
# - 共通機能利用一覧
# - 設計判断記録
```

**処理内容:**
- 解析結果からクラス一覧（JS/Resource/Logic/DTO/HTML/CSS）を自動導出
- 処理フローの依存関係をMermaidで可視化
- テーブルマッピングの整合性チェック
- 設計上の矛盾・不整合を検出して潜在的問題として報告
- DTO構造（フィールド/型/必須/説明）を自動設計

---

### Step3: md-design-generator（詳細設計書生成）

**スキル名:** `md-design-generator`  
**入力:** Step1の解析結果 + Step2の分析レポート  
**出力:** 詳細設計書Markdown（`output/design_doc/`）

```bash
# スキルを有効化
use_skill: md-design-generator

# Step1/Step2の結果を統合し、以下の章構成で詳細設計書を生成:
# 1. 処理詳細設計（処理フロー、クラス/メソッド定義）
# 2. Javaクラス設計（Resource/Logic/DTO）
# 3. JavaScript設計（画面制御、イベントハンドラ）
# 4. HTML/CSS設計（画面レイアウト）
# 5. DTO設計（フィールド定義、バリデーション）
# 6. テーブル項目マッピング
# 7. 共通機能参照
```

**処理内容:**
- 分析レポートの構造化データを詳細設計書テンプレートに変換
- 各クラスの責務・メソッド仕様を記述
- 処理フローを処理詳細として展開
- テーブル項目マッピングを画面項目↔DBカラム対応として記述

---

## ディレクトリ構成

```
output/
├── parse_result/          # Step1: 解析結果
│   └── <機能ID>_parse.md
├── analysis_result/       # Step2: 分析レポート
│   └── <機能ID>_analysis.md
└── design_doc/            # Step3: 詳細設計書
    └── <機能ID>_詳細設計書.md
```

## 実行例

```
# 在庫一覧（Webデポ）の場合:
入力: skill/D-IM-010-P_業務機能設計書_在庫一覧(Webデポ)_Ver0.1.xlsx

Step1出力: output/parse_result/D-IM-010-P_在庫一覧_parse.md
Step2出力: output/analysis_result/D-IM-010-P_在庫一覧_analysis.md
Step3出力: output/design_doc/D-IM-010-P_在庫一覧_詳細設計書.md
```

## 注意事項

- 各Stepは順番に実行する必要があります（Step1→Step2→Step3）
- Step1の`excel-parse`はPythonスクリプトで自動実行されます
- Step2の`design-analyzer`とStep3の`md-design-generator`はClineのスキルとして実行されます
- Excel内の画像貼り付けフローチャートは解析不可（openpyxlの制限）
- テーブル物理名が設計書にない場合、Step2で「潜在的な問題」として検出されます