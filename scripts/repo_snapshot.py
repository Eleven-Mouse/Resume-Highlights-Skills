#!/usr/bin/env python3
"""生成轻量级、只基于仓库事实的结构摘要。"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".gradle",
    ".mvn",
    "node_modules",
    "target",
    "build",
    "dist",
    "out",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
}

KEY_FILES = [
    "README.md",
    "README",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".github/workflows",
    "Jenkinsfile",
    "Makefile",
]

AREA_KEYWORDS = {
    "entrypoints": ("main", "app", "bootstrap", "server", "router", "route"),
    "controllers": ("controller", "handler", "api", "endpoint"),
    "services": ("service", "usecase", "use_case", "workflow", "agent"),
    "data_access": ("repository", "repo", "dao", "mapper", "entity", "model", "schema"),
    "infra": ("config", "docker", "k8s", "helm", "deploy", "infra"),
    "data_assets": ("sql", "migration", "ddl", "seed", "fixture"),
    "tests": ("test", "spec", "benchmark", "eval"),
    "ai_assets": ("prompt", "rag", "retriev", "embedding", "vector", "tool"),
}

AREA_LABELS = {
    "entrypoints": "入口线索",
    "controllers": "接口入口",
    "services": "服务层线索",
    "data_access": "数据访问层线索",
    "infra": "基础设施线索",
    "data_assets": "数据资产线索",
    "tests": "测试线索",
    "ai_assets": "AI 相关线索",
    "docs_assets": "规则文档线索",
    "automation_assets": "自动化脚本线索",
    "agent_assets": "Agent 配置线索",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".java": "Java",
    ".kt": "Kotlin",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".scala": "Scala",
    ".sql": "SQL",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".json": "JSON",
    ".md": "Markdown",
}

SOURCE_SUFFIXES = {
    ".py",
    ".java",
    ".kt",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".cpp",
    ".cc",
    ".cxx",
    ".c",
    ".cs",
    ".php",
    ".rb",
    ".scala",
    ".sql",
    ".sh",
    ".ps1",
}

TEXT_CONFIG_SUFFIXES = {
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".xml",
}

AUXILIARY_DIRS = {"docs", "doc", "references", "scripts", "agents"}
DOC_LIKE_SUFFIXES = {".md", ".yaml", ".yml", ".toml", ".json"}


def should_skip_dir(path: Path) -> bool:
    return path.name in IGNORED_DIRS


def walk_repo(repo_root: Path) -> tuple[list[Path], int]:
    files: list[Path] = []
    dir_count = 0
    for current_root, dirs, filenames in os.walk(repo_root, topdown=True):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        dir_count += len(dirs)
        current_path = Path(current_root)
        for filename in filenames:
            files.append(current_path / filename)
    return files, dir_count


def top_level_overview(repo_root: Path) -> dict[str, list[str]]:
    dirs: list[str] = []
    files: list[str] = []
    for child in sorted(repo_root.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
        if child.name in IGNORED_DIRS:
            continue
        if child.is_dir():
            dirs.append(child.name)
        else:
            files.append(child.name)
    return {"dirs": dirs, "files": files}


def detect_key_files(repo_root: Path) -> list[str]:
    found: list[str] = []
    for name in KEY_FILES:
        candidate = repo_root / name
        if candidate.exists():
            found.append(name)
    return found


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def summarize_languages(files: list[Path], repo_root: Path) -> list[dict[str, object]]:
    by_lang: Counter[str] = Counter()
    by_files: defaultdict[str, list[str]] = defaultdict(list)
    for path in files:
        lang = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if not lang:
            continue
        by_lang[lang] += 1
        if len(by_files[lang]) < 5:
            by_files[lang].append(path.relative_to(repo_root).as_posix())

    items = []
    for lang, count in by_lang.most_common():
        items.append(
            {
                "language": lang,
                "files": count,
                "examples": by_files[lang],
            }
        )
    return items


def summarize_extensions(files: list[Path]) -> list[dict[str, object]]:
    counts = Counter(path.suffix.lower() or "[无后缀]" for path in files)
    return [{"extension": ext, "files": count} for ext, count in counts.most_common(12)]


def looks_like_tooling_repo(files: list[Path], repo_root: Path) -> bool:
    source_files = 0
    doc_like_files = 0
    auxiliary_files = 0
    for path in files:
        rel_parts = {part.lower() for part in path.relative_to(repo_root).parts}
        suffix = path.suffix.lower()
        if suffix in SOURCE_SUFFIXES:
            source_files += 1
        if suffix in DOC_LIKE_SUFFIXES:
            doc_like_files += 1
        if rel_parts & AUXILIARY_DIRS:
            auxiliary_files += 1
    return auxiliary_files >= 2 and doc_like_files >= source_files


def detect_tooling_areas(files: list[Path], repo_root: Path) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    area_prefixes = {
        "docs_assets": "references/",
        "automation_assets": "scripts/",
        "agent_assets": "agents/",
    }
    for area, prefix in area_prefixes.items():
        paths = [path.relative_to(repo_root).as_posix() for path in files if path.relative_to(repo_root).as_posix().startswith(prefix)]
        if paths:
            matches[area] = paths[:10]
    return matches


def detect_areas(files: list[Path], repo_root: Path) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}
    for area, keywords in AREA_KEYWORDS.items():
        if area == "entrypoints":
            entrypoints = likely_entrypoints(files, repo_root)
            if entrypoints:
                matches[area] = entrypoints
            continue
        paths: list[str] = []
        for path in files:
            rel = path.relative_to(repo_root).as_posix().lower()
            suffix = path.suffix.lower()
            rel_parts = {part.lower() for part in path.relative_to(repo_root).parts}
            if area in {"entrypoints", "controllers", "services", "data_access", "tests", "ai_assets"}:
                if suffix not in SOURCE_SUFFIXES:
                    continue
                if rel_parts & AUXILIARY_DIRS:
                    continue
                if area in {"controllers", "services", "data_access"} and rel_parts & {"test", "tests"}:
                    continue
            if area == "infra" and suffix not in SOURCE_SUFFIXES | TEXT_CONFIG_SUFFIXES and path.name not in KEY_FILES:
                continue
            if area == "data_assets" and suffix not in SOURCE_SUFFIXES | TEXT_CONFIG_SUFFIXES:
                continue
            if any(keyword in rel for keyword in keywords):
                paths.append(path.relative_to(repo_root).as_posix())
            if len(paths) >= 10:
                break
        if paths:
            matches[area] = paths
    tooling_matches = detect_tooling_areas(files, repo_root)
    if tooling_matches and (not matches or looks_like_tooling_repo(files, repo_root)):
        matches.update({area: paths for area, paths in tooling_matches.items() if area not in matches})
    return matches


def is_likely_entrypoint(path: Path, repo_root: Path) -> bool:
    rel = path.relative_to(repo_root).as_posix()
    name = path.name
    suffix = path.suffix.lower()
    text = read_text_safely(path)

    if suffix == ".java":
        return name.endswith("Application.java") or "public static void main" in text
    if suffix == ".py":
        return name in {"main.py", "app.py", "server.py", "manage.py"} or '__name__ == "__main__"' in text
    if suffix == ".go":
        return name == "main.go" or ("/cmd/" in rel and "package main" in text)
    if suffix in {".js", ".ts"}:
        return name in {"main.js", "main.ts", "index.js", "index.ts"} and any(
            marker in text for marker in ("listen(", "createApp(", "bootstrap(", "new Server(")
        )
    return False


def likely_entrypoints(files: list[Path], repo_root: Path) -> list[str]:
    results: list[str] = []
    for path in files:
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel_parts = {part.lower() for part in path.relative_to(repo_root).parts}
        if rel_parts & AUXILIARY_DIRS:
            continue
        rel = path.relative_to(repo_root).as_posix()
        if is_likely_entrypoint(path, repo_root):
            results.append(rel)
        if len(results) >= 10:
            break
    return results


def build_snapshot(repo_root: Path) -> dict[str, object]:
    files, dir_count = walk_repo(repo_root)

    return {
        "repo_root": str(repo_root),
        "top_level": top_level_overview(repo_root),
        "counts": {
            "files": len(files),
            "dirs": dir_count,
        },
        "key_files": detect_key_files(repo_root),
        "likely_entrypoints": likely_entrypoints(files, repo_root),
        "languages": summarize_languages(files, repo_root),
        "extensions": summarize_extensions(files),
        "area_hints": detect_areas(files, repo_root),
    }


def render_markdown(snapshot: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# 仓库结构摘要")
    lines.append("")
    lines.append("> 这是一份只基于仓库事实的结构摘要，本身不直接推导业务价值。")
    lines.append("")
    lines.append("## 规模统计")
    lines.append("")
    counts = snapshot["counts"]
    lines.append(f"- 文件数：{counts['files']}")
    lines.append(f"- 目录数：{counts['dirs']}")
    lines.append("")
    lines.append("## 顶层结构")
    lines.append("")
    top_level = snapshot["top_level"]
    if top_level["dirs"]:
        lines.append("- 顶层目录：")
        for item in top_level["dirs"]:
            lines.append(f"  - `{item}`")
    if top_level["files"]:
        lines.append("- 顶层文件：")
        for item in top_level["files"]:
            lines.append(f"  - `{item}`")
    lines.append("")
    lines.append("## 关键清单文件")
    lines.append("")
    if snapshot["key_files"]:
        for item in snapshot["key_files"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- 内置清单里没有命中常见关键文件")
    lines.append("")
    lines.append("## 疑似入口")
    lines.append("")
    if snapshot["likely_entrypoints"]:
        for item in snapshot["likely_entrypoints"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- 按文件名启发式未发现明显入口")
    lines.append("")
    lines.append("## 语言分布")
    lines.append("")
    for item in snapshot["languages"]:
        examples = ", ".join(f"`{path}`" for path in item["examples"])
        lines.append(f"- {item['language']}：{item['files']} 个文件")
        if examples:
            lines.append(f"  - 示例：{examples}")
    if not snapshot["languages"]:
        lines.append("- 没有识别到已知语言后缀")
    lines.append("")
    lines.append("## 扩展名分布")
    lines.append("")
    for item in snapshot["extensions"]:
        lines.append(f"- `{item['extension']}`：{item['files']}")
    lines.append("")
    lines.append("## 区域线索")
    lines.append("")
    area_hints = snapshot["area_hints"]
    if area_hints:
        for area, paths in area_hints.items():
            label = AREA_LABELS.get(area, area)
            lines.append(f"- {label}：")
            for path in paths:
                lines.append(f"  - `{path}`")
    else:
        lines.append("- 按路径启发式未发现明显区域线索")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成仓库结构摘要。")
    parser.add_argument("repo_path", help="仓库根目录路径")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="输出格式",
    )
    parser.add_argument(
        "--output",
        help="可选的输出文件路径；不传则打印到标准输出。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_path).resolve()
    if not repo_root.exists():
        raise SystemExit(f"未找到仓库目录：{repo_root}")
    if not repo_root.is_dir():
        raise SystemExit(f"目标路径不是目录：{repo_root}")

    snapshot = build_snapshot(repo_root)
    if args.format == "json":
        content = json.dumps(snapshot, ensure_ascii=False, indent=2)
    else:
        content = render_markdown(snapshot)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
