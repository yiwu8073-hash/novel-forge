#!/usr/bin/env python3
"""NovelForge 工作流辅助脚本
提供:进度读写、JSON 台账原子更新、L1 硬性规则质检。

用法:
  python3 nf.py progress            # 查看当前进度
  python3 nf.py progress-set K=V    # 更新进度字段,如 phase=WRITING
  python3 nf.py ledger <file>       # 查看台账
  python3 nf.py qc-l1 <chapter-md>  # L1 硬性质检
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS = os.path.join(ROOT, "state", "progress.json")
CONFIG = os.path.join(ROOT, "novel-config.json")


def read_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def atomic_write(path, data):
    """临时文件 + rename 原子写,避免半截 JSON"""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)  # 原子覆盖


def get_progress():
    return read_json(PROGRESS, {"phase": "INIT", "nextChapter": 1})


def set_progress(**kwargs):
    p = get_progress()
    p.update(kwargs)
    p["updatedAt"] = __import__("datetime").datetime.now().isoformat(timespec="seconds")
    atomic_write(PROGRESS, p)
    print(f"progress updated: {json.dumps(kwargs, ensure_ascii=False)}")


def qc_l1(path):
    """L1 硬性规则检查:存在性、YAML 元信息、字数区间、结构"""
    if not os.path.exists(path):
        return {"pass": False, "issues": ["文件不存在"]}
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    issues = []

    # 1. YAML 头部
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        issues.append("缺少 YAML 头部元信息")
    else:
        body = text[m.end():]
        for key in ["chapter", "title", "status", "qc_score"]:
            if not re.search(rf"^{key}:\s*\S+", m.group(1), re.M):
                issues.append(f"YAML 缺少字段: {key}")

    # 2. 字数(去空白后)
    cfg = read_json(CONFIG, {})
    target = cfg.get("target", {}).get("wordsPerChapter", 1200)
    clean = re.sub(r"\s", "", text)
    words = len(clean)
    low, high = int(target * 0.6), int(target * 1.5)
    if not (low <= words <= high):
        issues.append(f"字数 {words} 不在区间 [{low}, {high}]")

    # 3. 结构:一级标题 + 至少 2 个自然段
    if not re.search(r"^#\s", body, re.M):
        issues.append("缺少一级标题")
    if len([p for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]) < 2:
        issues.append("段落不足 2 段")

    return {"pass": len(issues) == 0, "words": words, "issues": issues}


def qc_l2_report(chapter_md, score=None, pass_threshold=7.5):
    """生成 L2 评分卡报告骨架(LLM 评审后填充各维度得分与意见)"""
    with open(chapter_md, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^chapter:\s*(\d+)", text, re.M)
    ch = m.group(1) if m else "?"
    m = re.search(r"^title:\s*(.+)", text, re.M)
    title = m.group(1).strip() if m else "?"
    dims = [
        ("角色一致性", 0.25), ("情节逻辑", 0.25), ("文风贴合", 0.20),
        ("悬念与钩子", 0.15), ("伏笔执行", 0.15),
    ]
    lines = [
        f"# QC 报告 · 第 {ch} 章「{title}」",
        "",
        f"- 章节:chapter-{ch}",
        "- 质检时间:(填写)",
        "- L1 硬性规则:待运行",
        f"- L2 评分:待定 / 10(阈值 {pass_threshold})",
        "",
        "## 评分卡",
        "",
        "| 维度 | 权重 | 得分 | 加权 |",
        "|---|---|---|---|",
    ]
    for name, w in dims:
        lines.append(f"| {name} | {w} | 待评 | — |")
    lines += [
        "| **合计** | 1.00 | — | **待定** |",
        "",
        "## 评审意见",
        "",
        "(LLM 评审:优点 / 可改进 / 伏笔执行核对)",
        "",
        "## 结论",
        "",
        "**待定** — 是否进入版本管理。",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "progress"
    if cmd == "progress":
        print(json.dumps(get_progress(), ensure_ascii=False, indent=2))
    elif cmd == "progress-set":
        for kv in sys.argv[2:]:
            k, v = kv.split("=", 1)
            try:
                set_progress(**{k: json.loads(v)})
            except (json.JSONDecodeError, ValueError):
                set_progress(**{k: v})
    elif cmd == "ledger":
        print(json.dumps(read_json(os.path.join(ROOT, sys.argv[2])), ensure_ascii=False, indent=2))
    elif cmd == "qc-l1":
        r = qc_l1(sys.argv[2])
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif cmd == "qc-l2-skeleton":
        print(qc_l2_report(sys.argv[2]))
    else:
        print("unknown command")
