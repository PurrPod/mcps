#!/usr/bin/env python3
"""构建 registry.json 并同步 README.md

目录约定:
  mcps/<mcp-name>/mcp.json   官方 MCP (源码在本仓库维护)
  external/<mcp-name>.json   外部 MCP (仅收录元数据)

统一字段: name / desc / icon-link / repo / mcpServers
"""
import json
import os
import sys

REGISTRY_FILE = "registry.json"
README_FILE = "README.md"
REPO_URL = "https://github.com/PurrPod/mcps"

OFFICIAL_DIR = "mcps"
EXTERNAL_DIR = "external"

REQUIRED_FIELDS = ("name", "desc", "icon-link", "repo", "mcpServers")


def fail(msg):
    print(f"[Error] {msg}")
    sys.exit(1)


def load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        fail(f"无法读取或解析 {filepath}: {e}")


def validate_entry(filepath, entry, expected_name):
    """校验单个 MCP 条目 (官方与外部共用同一套字段规范)"""
    if not isinstance(entry, dict):
        fail(f"[{filepath}] 内容必须是一个 JSON 对象")

    for field in REQUIRED_FIELDS:
        if field not in entry:
            fail(f"[{filepath}] 缺少必填字段 '{field}'")

    # 校验 1: name 必须与目录/文件名一致
    name = str(entry.get("name", "")).strip()
    if not name:
        fail(f"[{filepath}] 'name' 不能为空")
    if name != expected_name:
        fail(f"[{filepath}] 'name' ('{name}') 必须与目录/文件名 ('{expected_name}') 一致")

    # 校验 2: desc 不能为空
    if not str(entry.get("desc", "")).strip():
        fail(f"[{filepath}] 'desc' 不能为空")

    # 校验 3: icon-link / repo 必须是合法链接
    for field in ("icon-link", "repo"):
        value = str(entry.get(field, "")).strip()
        if not value.startswith("http"):
            fail(f"[{filepath}] '{field}' 必须是合法的 http(s) 链接")

    # 校验 4: mcpServers 必须包含与 name 同名的键，且具备可用的安装配置
    mcp_servers = entry.get("mcpServers")
    if not isinstance(mcp_servers, dict) or name not in mcp_servers:
        fail(f"[{filepath}] 'mcpServers' 必须是一个对象，且包含键 '{name}'")

    target = mcp_servers[name]
    if not isinstance(target, dict):
        fail(f"[{filepath}] 'mcpServers.{name}' 必须是一个对象")

    has_command = isinstance(target.get("command"), str) and target["command"].strip()
    has_url = isinstance(target.get("url"), str) and target["url"].strip()

    if has_command:
        if not isinstance(target.get("args"), list):
            fail(f"[{filepath}] 使用 'mcpServers.{name}.command' 时必须同时提供数组类型的 'args'")
    elif not has_url:
        fail(f"[{filepath}] 'mcpServers.{name}' 必须包含 'command'+'args' (stdio 型) 或 'url' (远程型) 配置")


def normalize(entry):
    """输出为统一的注册表条目，仅保留约定的字段"""
    return {
        "name": entry["name"],
        "desc": entry["desc"],
        "icon-link": entry["icon-link"],
        "repo": entry["repo"],
        "mcpServers": entry["mcpServers"],
    }


def scan_official():
    """扫描 mcps/ 下的官方 MCP 目录"""
    entries = []
    if not os.path.isdir(OFFICIAL_DIR):
        return entries

    for item in sorted(os.listdir(OFFICIAL_DIR)):
        mcp_dir = os.path.join(OFFICIAL_DIR, item)
        if item.startswith(".") or not os.path.isdir(mcp_dir):
            continue

        meta_file = os.path.join(mcp_dir, "mcp.json")
        if not os.path.isfile(meta_file):
            fail(f"官方 MCP 目录缺失元数据文件: {meta_file}")

        entry = load_json(meta_file)
        validate_entry(meta_file, entry, item)
        entries.append((item, normalize(entry)))
    return entries


def scan_external():
    """扫描 external/ 下的外部 MCP JSON 文件"""
    entries = []
    if not os.path.isdir(EXTERNAL_DIR):
        return entries

    for item in sorted(os.listdir(EXTERNAL_DIR)):
        if item.startswith(".") or not item.endswith(".json"):
            continue

        meta_file = os.path.join(EXTERNAL_DIR, item)
        expected_name = item[: -len(".json")]

        entry = load_json(meta_file)
        validate_entry(meta_file, entry, expected_name)
        entries.append((expected_name, normalize(entry)))
    return entries


def generate_markdown_table(entries):
    """生成 Markdown 格式表格"""
    lines = [
        "| 安装指令 (Install ID) | 名称 | 描述 |",
        "| :--- | :--- | :--- |",
    ]

    if not entries:
        lines.append("| *(虚位以待)* | - | 期待您的收录！ |")
        return "\n".join(lines) + "\n"

    for short_id, info in sorted(entries):
        name = info["name"]
        desc = str(info["desc"]).replace("|", "\\|")
        repo = info["repo"]
        lines.append(f"| `purrcat install mcp {short_id}` | [{name}]({repo}) | {desc} |")

    return "\n".join(lines) + "\n"


def replace_between_tags(text, start_tag, end_tag, new_content):
    """将文本中 start_tag 与 end_tag 之间的内容替换为 new_content"""
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        head = text[: start_idx + len(start_tag)]
        tail = text[end_idx:]
        return f"{head}\n{new_content}{tail}"
    return text


def update_readme(official, external):
    """回写更新 README.md 中的表格"""
    if not os.path.exists(README_FILE):
        return

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    content = replace_between_tags(
        content, "<!-- OFFICIAL:START -->", "<!-- OFFICIAL:END -->",
        generate_markdown_table(official),
    )
    content = replace_between_tags(
        content, "<!-- EXTERNAL:START -->", "<!-- EXTERNAL:END -->",
        generate_markdown_table(external),
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    print("扫描官方 MCP (mcps/) ...")
    official = scan_official()

    print("扫描外部 MCP (external/) ...")
    external = scan_external()

    # 校验 5: 官方与外部不允许同名 MCP
    all_names = [name for name, _ in official] + [name for name, _ in external]
    duplicates = sorted({n for n in all_names if all_names.count(n) > 1})
    if duplicates:
        fail(f"官方与外部目录存在同名 MCP: {', '.join(duplicates)}")

    merged = sorted([*official, *external], key=lambda pair: pair[0])

    registry = {
        "version": "2.0",
        "repository": REPO_URL,
        "mcps": [info for _, info in merged],
    }

    print(f"生成 {REGISTRY_FILE} ...")
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("更新 README.md ...")
    update_readme(official, external)

    print(f"构建与校验完成！官方 {len(official)} 个，外部 {len(external)} 个，共 {len(registry['mcps'])} 条。")


if __name__ == "__main__":
    main()
