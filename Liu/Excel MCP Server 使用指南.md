# Excel MCP Server 使用指南（中文版）

## 1. 什么是 Excel MCP Server？

**Excel MCP Server** 是一个基于 **Model Context Protocol（MCP）** 的服务器程序，用于让 AI 助手（如 Cline / Claude）能够直接**读取、写入、分析 Excel 文件**，无需人工手动复制粘贴数据。

### 核心价值
- AI 可以直接操作 `.xlsx` / `.xls` / `.csv` 文件
- 支持读取多个工作表（Sheet）
- 支持写入数据、创建表格
- 大文件自动分页处理

---

## 2. 安装与配置

### 步骤一：确认 Node.js 环境已安装

```bash
node -v
npm -v
```

### 步骤二：配置 Cline 的 MCP 设置

在 VS Code 中，点击 Cline 插件图标 → 点击右上角 **MCP Servers（插件图标）** → 选择 **Edit MCP Settings**，打开 `cline_mcp_settings.json` 文件，添加以下配置：

```json
{
  "mcpServers": {
    "excel": {
      "command": "npx",
      "args": [
        "-y",
        "@negokaz/excel-mcp-server"
      ],
      "env": {
        "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

> **说明：**
> - `EXCEL_MCP_PAGING_CELLS_LIMIT`：每次读取的最大单元格数（默认 4000），大文件会自动分页
> - `disabled: false`：表示启用该 MCP Server
> - 使用 `npx` 可以无需全局安装，自动下载并运行

### 步骤三：验证配置是否生效

重启 VS Code 后，在 Cline 的 MCP Servers 面板中，可以看到 `excel` 服务器处于 **Connected（已连接）** 状态。

---

## 3. 提供的工具（Tools）列表

配置完成后，Cline 可以使用以下工具操作 Excel 文件：

| 工具名称 | 功能说明 | 参数示例 |
|---------|---------|---------|
| `excel_describe_sheets` | 列出 Excel 文件中所有工作表名称 | `filePath` |
| `excel_read_sheet` | 读取指定工作表的内容 | `filePath`, `sheetName`, `range` |
| `excel_write_to_sheet` | 向工作表写入数据 | `filePath`, `sheetName`, `data` |
| `excel_create_table` | 在工作表中创建带格式的表格 | `filePath`, `sheetName`, `headers`, `rows` |
| `excel_get_worksheet_info` | 获取工作表信息（行数、列数等） | `filePath`, `sheetName` |

---

## 4. 使用方法与示例

### 示例一：读取 Excel 文件并分析

直接在 Cline 对话框中输入自然语言指令：

```
请读取文件 C:/work/data.xlsx，列出所有工作表，
并将第一个工作表的内容整理成 Markdown 表格展示给我。
```

**Cline 的执行流程：**
1. 调用 `excel_describe_sheets` → 获取工作表列表
2. 调用 `excel_read_sheet` → 读取指定 Sheet 的数据
3. 将数据整理后以 Markdown 格式输出

---

### 示例二：从 Excel 提取数据生成文档

```
请读取 C:/work/design.xlsx 中的"功能设计"工作表，
将其中的功能列表整理成标准的 Markdown 设计文档。
```

---

### 示例三：将数据写入 Excel

```
请将以下员工信息写入 C:/work/employees.xlsx 的 Sheet1：

| 姓名 | 部门   | 职位     |
|------|--------|--------|
| 张三 | 开发部 | 工程师   |
| 李四 | 测试部 | 测试工程师 |
| 王五 | 运营部 | 运营专员  |
```

---

### 示例四：分析大型 Excel 文件

对于行数较多的 Excel 文件，Excel MCP Server 支持**分页读取**：

```
请读取 C:/work/sales_data.xlsx 的"2024年销售数据"工作表，
统计每个月的销售总额，并生成柱状图数据。
```

---

## 5. 在当前项目中的应用场景

当前工作目录中有以下 Excel 文件，可以直接用 Excel MCP Server 处理：

| 文件名 | 可能的用途 |
|--------|-----------|
| `Liu/(サンプル)アプリケーション詳細設計書.xlsx` | 读取应用详细设计书内容，转换为 Markdown |
| `skill/D-IM-010-P_業務機能設計書_在庫一覧(Webデポ)_Ver0.1.xlsx` | 解析业务功能设计书，提取处理逻辑 |
| `Liu/VSCode開発環境構築手順書_Oracle版.xlsx` | 读取环境构建步骤，生成操作手顺文档 |
| `「ClineでGitの小難しい部分をいかに簡単にできるか」調查.xlsx` | 读取调查数据，进行分析汇总 |

---

## 6. 常见问题与注意事项

### ❓ Q1：文件路径如何填写？

推荐使用**绝对路径**，Windows 系统示例：
```
C:/work/UPR2_work/GitHub/AI_TEST1/data.xlsx
```
也可以使用反斜杠，但需要转义：
```
C:\\work\\data.xlsx
```

### ❓ Q2：读取大文件时数据不完整怎么办？

调整环境变量 `EXCEL_MCP_PAGING_CELLS_LIMIT` 的值，例如设为 `10000`：
```json
"env": {
  "EXCEL_MCP_PAGING_CELLS_LIMIT": "10000"
}
```
或者在指令中指定读取范围：
```
请读取第 1 行到第 100 行的数据
```

### ❓ Q3：写入操作会覆盖原文件吗？

是的，写入操作会直接修改原文件。**建议操作前先备份重要文件。**

### ❓ Q4：支持哪些文件格式？

| 格式 | 支持情况 |
|------|---------|
| `.xlsx`（Excel 2007+） | ✅ 完全支持 |
| `.xls`（Excel 97-2003） | ✅ 支持读取 |
| `.csv` | ✅ 支持 |
| `.ods`（OpenDocument） | ⚠️ 部分支持 |

---

## 7. 与其他 MCP Server 的对比

| MCP Server | 用途 |
|-----------|------|
| **Excel MCP Server** | 读写 Excel / CSV 文件 |
| **GitHub MCP Server** | 操作 GitHub 仓库、Issue、PR |
| **Backlog MCP Server** | 操作 Backlog 项目管理工具 |
| **Filesystem MCP Server** | 读写本地文件系统 |

---

## 8. 快速上手总结

```
1. 打开 Cline 设置 → MCP Servers → Edit MCP Settings
2. 添加 excel MCP Server 配置（见第2节）
3. 重启 VS Code，确认连接状态为 Connected
4. 在 Cline 对话框中直接用自然语言指令操作 Excel 文件
```

---

*文档生成时间：2026/04/17*  
*适用版本：@negokaz/excel-mcp-server（最新版）*