<h1 align="center">PurrCat MCP Market</h1>

<p align="center">
    专为 <a href="https://github.com/PurrPod/purrcat">PurrCat</a> 构建的 Model Context Protocol (MCP) 服务器市场与注册表中心。
</p>

---

## 1. 快速安装

基于本仓库提供的全局注册表，支持通过**短名**进行一键安装配置：

```bash
purrcat install mcp playwright
```

系统将自动下载对应的配置，并合并至您的本地 `.purrcat/mcp_config.json` 文件中。有的 MCP Server 可能需要密钥配置或个性化配置才可以正常使用，这种情况下您安装成功后需要自行去修改对应的配置文件。

---

## 2. 仓库架构设计

```text
mcps/
├── .github/workflows/   # CI/CD 自动化构建流
├── scripts/             # 注册表构建与校验脚本
├── registry.json        # 全局注册表 (由 Action 自动生成)
├── README.md            # 说明文档与 MCP 列表 (由 Action 自动更新)
│
├── mcps/                # 官方 MCP (源码直接在本仓库维护，不接收外部 PR)
│   └── <mcp-name>/
│       ├── mcp.json     # 元数据 (统一字段规范)
│       └── ...          # MCP 源代码
│
└── external/            # 外部 MCP (仅通过单个 JSON 收录，不存放源码)
    └── <mcp-name>.json
```

* **官方 MCP (`mcps/`)**: 由我们直接在本仓库内维护源代码与配置，不接收外部贡献者的源码 PR。
* **外部 MCP (`external/`)**: 第三方 MCP 仅需提交一个 `<mcp-name>.json` 元数据文件即可收录，源代码仍保留在原仓库。

---

## 3. 已收录 MCP 清单

*(注：本列表由自动化流水线实时生成，点击名称可访问源代码库)*

### Official (官方维护)
<!-- OFFICIAL:START -->
| 安装指令 (Install ID) | 名称 | 描述 |
| :--- | :--- | :--- |
| *(虚位以待)* | - | 期待您的收录！ |
<!-- OFFICIAL:END -->

### External (外部收录)
<!-- EXTERNAL:START -->
| 安装指令 (Install ID) | 名称 | 描述 |
| :--- | :--- | :--- |
| `purrcat install mcp playwright` | [playwright](https://github.com/microsoft/playwright-mcp) | 浏览器自动化 MCP，提供网页截图、交互与测试能力。 |
<!-- EXTERNAL:END -->

---

## 4. 统一字段规范

无论是官方 MCP (`mcps/<mcp-name>/mcp.json`) 还是外部 MCP (`external/<mcp-name>.json`)，均使用完全相同的字段规范：

```json
{
  "name": "playwright",
  "desc": "浏览器自动化 MCP，提供网页截图、交互与测试能力。",
  "icon-link": "https://avatars.githubusercontent.com/microsoft?s=200",
  "repo": "https://github.com/microsoft/playwright-mcp",
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### 字段解析

* **`name`** (必填): 安装标识，必须与目录名或 JSON 文件名完全一致，也是用户用于安装的指令标识。
* **`desc`** (必填): 一句话描述该 MCP 的用途。
* **`icon-link`** (必填): 图标链接，用于市场展示。
* **`repo`** (必填): 源码仓库链接。外部 MCP 指向其原始仓库；官方 MCP 指向本仓库内对应目录。
* **`mcpServers`** (必填): MCP 安装配置，必须包含与 `name` 同名的键，内部字段对齐官方 MCP JSON 规范。stdio 型提供 `command` + `args`（`env` 可选）；远程型提供 `url` 即可。

CI 构建时会自动校验以上字段，并将 `mcps/` 与 `external/` 中的所有条目整理为统一的 `registry.json`。

---

## 5. 收录方式

### 外部 MCP

在 `external/` 目录下新建 `<mcp-name>.json`（内容遵循上述统一字段规范），提交 Pull Request。CI 校验通过并合并后，列表与注册表将全自动更新。

### 官方 MCP

`mcps/` 目录由维护者直接提交，每个 MCP 目录需包含 `mcp.json` 元数据与完整源代码，不接收外部 PR。
