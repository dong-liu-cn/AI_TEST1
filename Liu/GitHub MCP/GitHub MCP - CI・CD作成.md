# GitHub MCP：CI・CD作成

- copilot - gpt-5-mini
- prompt

GitHub MCP を使用して CI/CD パイプラインを構築する。コードが `branch_test2` ブランチにプッシュされた際にワークフローをトリガーし、新しいプルリクエストを作成する。

追加: `.github/workflows/ci-create-pr.yml`

- トリガー: push on `branch_test2`
- 処理: build（プレースホルダ）後、`actions/github-script` で `main` へ自動 PR を作成（既存 PR がなければ作成）

```yaml
name: CI and create PR
on:
  push:
    branches:
      - branch_test2
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Placeholder build/tests
        run: |
          echo "No project-specific tests configured. Placeholder build step."
          echo "Build succeeded"
  create_pr:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Create PR if not exists
        uses: actions/github-script@v6
        with:
          script: |
            const owner = context.repo.owner;
            const repo = context.repo.repo;
            const head = 'branch_test2';
            const base = 'main';
            const { data: pulls } = await github.rest.pulls.list({
              owner,
              repo,
              state: 'open',
              head: `${owner}:${head}`,
              base
            });
            if (pulls.length > 0) {
              console.log(`Existing PR found: #${pulls[0].number}`);
            } else {
              const { data: pr } = await github.rest.pulls.create({
                owner,
                repo,
                title: `Auto: Merge ${head} into ${base}`,
                head,
                base,
                body: 'Automated PR created after successful CI on branch_test2.'
              });
              console.log(`Created PR #${pr.number}`);
            }