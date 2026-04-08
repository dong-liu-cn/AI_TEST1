# GitHub MCP：CI・CD作成

- copilot - gpt-5-mini
- prompt

GitHub MCP を使用して CI/CD パイプラインを構築する。コードが `branch_test2` ブランチにプッシュされた際にワークフローをトリガーし、新しいプルリクエストを作成する。

追加: `.github/workflows/ci-create-pr.yml`

- トリガー: push on `branch_test2`
- 処理: build（プレースホルダ）後、`actions/github-script` で `main` へ自動 PR を作成（既存 PR がなければ作成）

```yaml
name: Auto Create PR from branch_test2

on:
  push:
    branches:
      - branch_test2

jobs:
  create-pull-request:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create Pull Request
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_ACTOR: ${{ github.actor }}
          PR_SHA: ${{ github.sha }}
        run: |
          # 既存のオープンPRを確認
          PR_COUNT=$(gh pr list \
            --base main \
            --head branch_test2 \
            --state open \
            --json number \
            --jq 'length')

          if [ "$PR_COUNT" -eq 0 ]; then
            TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

            printf '%s\n' \
              '## 自動作成されたプルリクエスト' \
              '' \
              'このPRは `branch_test2` ブランチへのプッシュにより自動作成されました。' \
              '' \
              '- **ソースブランチ:** `branch_test2`' \
              '- **マージ先:** `main`' \
              "- **トリガー:** ${PR_ACTOR} によるプッシュ" \
              "- **コミット:** ${PR_SHA}" \
              > /tmp/pr_body.md

            gh pr create \
              --title "[Auto PR] branch_test2 への変更: ${TIMESTAMP}" \
              --body-file /tmp/pr_body.md \
              --base main \
              --head branch_test2
            echo "PR created successfully."
          else
            echo "PR already exists for branch_test2, skipping creation."
          fi