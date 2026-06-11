#!/usr/bin/env python3
import os
import json
import re
import sys

REGISTRY_FILE = "registry.json"
README_FILE = "README.md"

def parse_mcp_json(filepath):
    """解析并读取 mcp.json"""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[Error] 解析 JSON 失败 {filepath}: {e}")
        return None

def scan_directory(base_dir, mcp_type):
    """扫描指定目录下的所有 MCP 配置"""
    mcps = {}
    if not os.path.exists(base_dir):
        return mcps

    for item in sorted(os.listdir(base_dir)):
        mcp_dir = os.path.join(base_dir, item)
        if os.path.isdir(mcp_dir) and not item.startswith('.'):
            mcp_file = os.path.join(mcp_dir, 'mcp.json')
            meta = parse_mcp_json(mcp_file)

            if not meta:
                print(f"[Error] 缺失或无法读取: {mcp_file}")
                sys.exit(1)

            mcp_name = meta.get("name", "").strip()

            # 严格校验 1: 名称必须与文件夹一致
            if mcp_name != item:
                print(f"[Error] 校验失败: 目录 [{mcp_dir}] 与其内部 mcp.json 的 name 字段 ('{mcp_name}') 不一致！")
                sys.exit(1)

            # 严格校验 2: 必须包含 source_url 方便用户查阅源码
            source_url = meta.get("source_url", "").strip()
            if not source_url or not source_url.startswith("http"):
                print(f"[Error] 校验失败: [{mcp_file}] 必须包含有效的 'source_url' 字段，指向其开源仓库或文档说明！")
                sys.exit(1)

            # 严格校验 3: 必须包含合法的 config
            config = meta.get("config", {})
            if not isinstance(config, dict) or "command" not in config or "args" not in config:
                print(f"[Error] 校验失败: [{mcp_file}] 的 'config' 字段必须包含标准的 'command' 和 'args'！")
                sys.exit(1)

            mcps[item] = {
                "name": mcp_name,
                "description": meta.get("description", "暂无描述"),
                "author": meta.get("author", "PurrCat Contributor"),
                "source_url": source_url,
                "type": mcp_type,
                "tags": meta.get("tags", []),
                "config": config
            }
    return mcps

def generate_markdown_table(mcps_dict, target_type):
    """生成 Markdown 格式表格"""
    lines = [
        "| 安装指令 (Install ID) | 名称 | 描述 | 作者 |",
        "| :--- | :--- | :--- | :--- |"
    ]

    count = 0
    for short_id, info in sorted(mcps_dict.items()):
        if info.get("type") == target_type:
            name = info.get("name", short_id)
            desc = info.get("description", "-")
            author = info.get("author", "-")
            url = info.get("source_url", "#")

            # 将名称直接作为超链接，去掉多余的链接列
            lines.append(f"| `purrcat install mcp {short_id}` | [{name}]({url}) | {desc} | {author} |")
            count += 1

    if count == 0:
        lines.append("| *(虚位以待)* | - | 期待您的 PR！ | - |")

    return "\n".join(lines) + "\n"

def update_readme(registry_data):
    """回写更新 README.md 中的表格 (安全版)"""
    if not os.path.exists(README_FILE):
        return

    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    def replace_between_tags(text, start_tag, end_tag, new_content):
        start_idx = text.find(start_tag)
        end_idx = text.find(end_tag)
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            # 截取 start_tag 之前的内容（包含 start_tag）
            head = text[:start_idx + len(start_tag)]
            # 截取 end_tag 之后的内容（包含 end_tag）
            tail = text[end_idx:]
            # 安全拼接
            return f"{head}\n{new_content}{tail}"
        return text

    off_table = generate_markdown_table(registry_data["mcps"], "official")
    content = replace_between_tags(content, "<!-- OFFICIAL:START -->", "<!-- OFFICIAL:END -->", off_table)

    com_table = generate_markdown_table(registry_data["mcps"], "community")
    content = replace_between_tags(content, "<!-- COMMUNITY:START -->", "<!-- COMMUNITY:END -->", com_table)

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("开始扫描本地目录...")
    official_mcps = scan_directory("official", "official")
    community_mcps = scan_directory("community", "community")

    all_mcps = {**official_mcps, **community_mcps}

    registry = {
        "version": "1.0",
        "repository": "https://github.com/PurrPod/mcps",
        "mcps": all_mcps
    }

    print("生成 registry.json...")
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("更新 README.md...")
    update_readme(registry)

    print("构建与校验完成！")

if __name__ == "__main__":
    main()