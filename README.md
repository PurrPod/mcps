<h1 align="center">PurrCat MCP Servers</h1>

<p align="center">
    专为 <a href="https://github.com/PurrPod/purrcat">PurrCat</a> 构建的 Model Context Protocol (MCP) 服务器配置合集与注册表中心。
</p>

---

## 1. 快速安装

基于本仓库提供的全局注册表，支持通过**短名**进行一键安装配置：

```bash
purrcat install mcp playwright
```

系统将自动下载对应的配置，并合并至您的本地 `.purrcat/mcp_config.json` 文件中。

---

## 2. 仓库架构设计

```text
mcps/
├── .github/workflows/   # CI/CD 自动化构建流
├── scripts/             # 注册表构建与校验脚本
├── registry.json        # 全局注册表 (由 Action 自动生成)
├── README.md            # 说明文档与 MCP 列表 (由 Action 自动更新)
│
├── official/            # 官方核心 MCP
│   └── playwright/
│       └── mcp.json     # 核心配置文件
│
└── community/           # 社区扩展 MCP
    └── sqlite/
        └── mcp.json

```

---

## 3. 已收录 MCP 清单

*(注：本列表由自动化流水线实时生成，点击名称可访问源代码库)*

### Official (官方核心)
<!-- OFFICIAL:START -->
| 安装指令 (Install ID) | 名称 | 描述 | 作者 |
| :--- | :--- | :--- | :--- |
| *(虚位以待)* | - | 期待您的 PR！ | - |
<!-- OFFICIAL:END -->

### Community (社区扩展)
<!-- COMMUNITY:START -->
| 安装指令 (Install ID) | 名称 | 描述 | 作者 |
| :--- | :--- | :--- | :--- |
| *(虚位以待)* | - | 期待您的 PR！ | - |
<!-- COMMUNITY:END -->

---

## 4. 贡献指南 (提交 MCP 配置)

本仓库负责管理 MCP 的连接配置索引。提交前，请在 `community/` 下创建与您 MCP 短名一致的目录，并在其中提供标准的 `mcp.json` 文件。

### 规范的 `mcp.json` 格式说明

您的配置文件必须严格遵循如下规范，包括基础的展示元信息（metadata），以及控制 Agent 连接行为的 `config` 块。

```json
{
  "name": "playwright",
  "description": "浏览器自动化 MCP，提供网页截图、交互与测试能力。",
  "author": "Playwright Team",
  "source_url": "https://github.com/playwright-community/mcp-server",
  "tags": ["browser", "automation"],
  "config": {
    "command": "npx",
    "args": [
      "-y",
      "@playwright/mcp@latest",
      "--user-data-dir=agent_vm/.buffer/playwright",
      "--output-dir=agent_vm/.buffer/screenshots"
    ],
    "env": {}
  }
}
```

### 字段解析：

* **`name`**: 必须与您创建的文件夹名称完全一致。也是用户用于安装的指令标识。
* **`source_url`** (必填): 提供该 MCP 的开源代码库 URL（如 GitHub 链接），以便用户查阅说明文档与安全审阅代码。
* **`config`** (核心配置): 其内部字段完全对齐官方的 MCP JSON 规范。其中 `command` 和 `args` 为必填项，`env` 为可选项（如需要 API Key 时预留空值即可，安装后 CLI 会智能提示用户补充）。

### 提交流程

创建完毕后，提交 Pull Request。我们的 CI 脚本将自动检验名称一致性、URL 是否合法以及 `config` 结构是否完整。检验通过合并后，列表与注册表均将全自动更新。