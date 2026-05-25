#!/usr/bin/env python3
"""
学术写作正文风格检查器
基于 WSS-1 规范，输出规则编号 + 说明 + 行号

用法：
    python3 writingstylecheck.py <文件路径>
    python3 writingstylecheck.py --text "你的文本"
    python3 writingstylecheck.py --stdin
    python3 writingstylecheck.py <文件路径> --format json
    python3 writingstylecheck.py <文件路径> --fix
    python3 writingstylecheck.py <文件路径> --fix-dry-run
"""

import argparse
import re
import sys
import json
from pathlib import Path


LEXICON_PATH = Path(__file__).resolve().parent.parent / "references" / "lexicon-substitutions.zh-CN.json"

# ─────────────────────────────────────────────────────────────
# 规则定义
# ─────────────────────────────────────────────────────────────
# 每个规则：(编号, 类别, 正则或条件, 错误描述, ✅正确示例, ❌错误示例)
# mode: "search" = searchall, "line_start" = 行首匹配, "multi" = 整段检查

RULES = [
    # ── L 节：语言基调 ─────────────────────────────────────
    {
        "id": "L1.1",
        "category": "语言基调 / 禁止表达 / 感叹式开头",
        "mode": "line_start",
        "pattern": r"^(在当今|随着|近年来|当前|时下|时下|当今世界)",
        "message": "段落不得以感叹式/背景铺垫开头（L1.1）",
        "suggestion": "直接用判断句陈述技术事实",
        "example_bad": "随着边缘计算技术的不断成熟……",
        "example_good": "边缘计算将数据处理能力从云端向网络边缘迁移……",
    },
    {
        "id": "L1.2",
        "category": "语言基调 / 禁止表达 / 宏大叙事",
        "mode": "search",
        "pattern": r"引领第[一二三四五六七八九十零百千万〇\d]+次.*革命|引领.*工业.*革命|重塑.*人类文明",
        "message": "禁止宏大叙事断言（L1.2）",
        "suggestion": "用客观技术陈述替代政治/历史隐喻",
        "example_bad": "引领第四次工业革命",
        "example_good": "显著提升了系统自动化水平（给出量化指标）",
    },
    {
        "id": "L1.3",
        "category": "语言基调 / 禁止表达 / 文学化比喻",
        "mode": "search",
        "pattern": r"赋予.*灵魂|拥有.*大脑|大脑.*融合|思考.*感知|感知.*思考|蜕变|赋能|插上.*翅膀|让机器.*思考|赋予.*生命",
        "message": "禁止文学化比喻（L1.3）",
        "suggestion": "用具体技术能力描述替代修辞性表达",
        "example_bad": "赋予设备灵魂，使设备拥有自主意识",
        "example_good": "设备具备本地模式识别与异常检测能力，端到端响应时延可降低至毫秒量级",
    },
    {
        "id": "L1.4",
        "category": "语言基调 / 禁止表达 / 能力堆砌",
        "mode": "search",
        "pattern": r"不仅.{0,8}，更.{0,8}，还.{0,8}[，。]|能够.{0,10}，能够.{0,10}，能够.{0,10}",
        "message": "禁止三层递进能力堆砌句（L1.4）",
        "suggestion": "最多使用两层递进，或换用判断句陈述",
        "example_bad": "不仅实现了高效数据传输，更支持边缘计算，还具备自学习能力",
        "example_good": "该系统支持边缘计算和本地自学习能力，数据传输效率提升约40%[X]",
    },
    {
        "id": "L2",
        "category": "语言基调 / 代词使用",
        "mode": "search",
        "pattern": r"(智能制造|智能家居|边缘计算|云端模式|感知层|网络层|应用层|物联网|人工智能|深度学习|机器学习|联邦学习)[^里内中其本之所]\s*(他|她)",
        "message": "指代非人物体/系统必须用「它」，不能用「他」或「她」（L2）",
        "suggestion": "将「他/她」改为「它」",
        "example_bad": "智能制造是AIoT最成熟的应用领域，他主要通过……",
        "example_good": "智能制造是AIoT最成熟的应用领域，它主要通过……",
    },
    {
        "id": "L3",
        "category": "语言基调 / 数据引用",
        "mode": "search",
        "pattern": r"(亿|万|千|百)[^，,，、个十百千万亿人用台器件项元][^据统计测算表明]|[数]?据预测|预计将突破|将超过\d+亿(?!据)",
        "message": "数字引用必须标注来源机构与年份（L3）",
        "suggestion": "格式：据[机构]统计，[年份]，……[引用]",
        "example_bad": "预计到2025年，全球物联网设备数量将突破750亿台",
        "example_good": "据IoT Analytics统计，2023年全球在网物联网设备数量达到163亿台[1]",
    },

    # ── P 节：段落与句子结构 ──────────────────────────────
    {
        "id": "P1",
        "category": "段落结构 / 段落开头",
        "mode": "line_start",
        "pattern": r"^(随着|在.*背景[下中]|基于.*发展|近年来|近年来|当前|时下|当今)",
        "message": "段落第一句不得以状语（时间/条件/背景）开头（P1）",
        "suggestion": "段落首句必须是判断句，直接陈述核心论点",
        "example_bad": "随着边缘计算技术的不断成熟……",
        "example_good": "边缘计算将数据处理能力从云端向网络边缘迁移，显著降低了端到端通信时延。",
    },
    {
        "id": "P2",
        "category": "段落结构 / 列表引出",
        "mode": "search",
        "pattern": r"(主要|重要|关键|核心|包括|涵盖).{0,3}(：|:|有)\s*\n?\s*[^主本可分应]",
        "message": "引出4项及以上并列内容，必须用「……主要包括以下几个方面：」等固定句式（P2）",
        "suggestion": "先用引导句，再出现列表；引导句用句号结尾",
        "example_bad": "AIoT的主要特征包括：实时推理……、自学习……",
        "example_good": "AIoT的核心特征主要表现在以下几个方面：\n1. 实时推理……\n2. 自学习……",
    },
    {
        "id": "P3",
        "category": "段落结构 / 并列标点",
        "mode": "search",
        "pattern": r"[、，][^，。]{0,30}[、，][^，。]{0,30}[、，][^，。]{0,30}[、，]",
        "message": "4个及以上并列成分须用分号（；）分隔，不用顿号连续堆砌（P3）",
        "suggestion": "将顿号改为分号",
        "example_bad": "感知层；网络层；应用层；平台层（应用了分号，但3个以内用顿号）",
        "example_bad2": "实时推理、自学习、分布式协同、边缘优化（4项用顿号，违反规定）",
        "example_good": "感知层；网络层；应用层（4项以上用分号）\n心电、血氧、血压（3项以内用顿号）",
    },

    # ── T 节：技术内容组织 ──────────────────────────────
    {
        "id": "T2",
        "category": "技术内容 / 重点标注",
        "mode": "search",
        "pattern": r"值得注意的是[，。]|很重要的是[，。]|不可忽视的是[，。]|需要特别说明的是|特别值得指出的是",
        "message": "重点内容引出词语错误（T2）",
        "suggestion": "使用「特别指出」「需要说明的是」",
        "example_bad": "值得注意的是，边缘计算可以……",
        "example_good": "特别指出，边缘计算可以将数据处理能力从云端向网络边缘迁移……",
    },

    # ── F 节：符号格式 ─────────────────────────────────
    {
        "id": "F1.1",
        "category": "符号格式 / 中文标点 / 引号",
        "mode": "search",
        "pattern": r"\"[^\"]{2,50}\"|\"[^\"]{2,50}\"",
        "message": "正文须使用中文引号（\u201c\u2026\u2026\u201d）或（\u2018\u2026\u2026\u2019），不得使用英文直引号（F1.1）",
        "suggestion": "将 ASCII 双引号替换为中文双引号，将 ASCII 单引号替换为中文单引号",
        "example_bad": "\u201c边缘计算\u201d是指\u2026\u2026",
        "example_good": "\u201c边缘计算\u201d是指\u2026\u2026",
    },
    {
        "id": "F1.2",
        "category": "符号格式 / 中文标点 / 括号",
        "mode": "search",
        "pattern": r"\([^)]{3,50}\)|（[^）]{3,50}）",  # 混合检测
        "message": "正文须使用中文全角括号「（……）」，不得使用英文半角括号（F1.2）",
        "suggestion": "将 (...) 替换为（……）",
        "example_bad": "边缘计算(Edge Computing)是指……",
        "example_good": "边缘计算（Edge Computing，EC）是指……",
    },
    {
        "id": "F2",
        "category": "符号格式 / 缩写引入",
        "mode": "search",
        "pattern": r"[^\u4e00-\u9fa5](FL|AIoT|IoT|EC|AI|ML|DL|RL|MCS|TinyML|NAS|MPC|MAS|DQN|TSN|FedAvg)\s*[（(]",
        "message": "英文缩写首次出现必须先给全称再给缩写，格式：中文名（英文全称，缩写）（F2）",
        "suggestion": "首次出现使用「中文名（英文全称，缩写）」格式",
        "example_bad": "联邦学习（FL）是一种……",
        "example_good": "联邦学习（Federated Learning，FL）是一种……",
    },
    {
        "id": "F3",
        "category": "符号格式 / 括号滥用",
        "mode": "search",
        "pattern": r"（[^\)]{2,20}）[，。](?!其中|式中|即|也就是)",  # 括号后无技术说明
        "message": "括号不得用于对前文术语进行说明或重述（F3）",
        "suggestion": "将括号内容并入正文，重新组织逻辑结构",
        "example_bad": "适应环境分布的变化（即概念漂移）",
        "example_good": "适应环境分布的变化，即发生概念漂移时也能自动调整",
    },
    {
        "id": "F4",
        "category": "符号格式 / 加粗",
        "mode": "search",
        "pattern": r"\*\*[^\*\n]{1,20}\*\*",
        "message": "正文中不得使用加粗格式（F4）",
        "suggestion": "删除 **，直接使用正文",
        "example_bad": "**关键**在于……",
        "example_good": "边缘计算的核心优势在于……",
    },
    {
        "id": "F5",
        "category": "符号格式 / 破折号分节",
        "mode": "search",
        "pattern": r"——\s*\n|——[^—\n]",
        "message": "正文中不得以破折号「——」作为段落或内容之间的分节符（F5）",
        "suggestion": "改用分级标题（###）或完整的段落过渡句",
        "example_bad": "边缘计算的主要优势是——\n低延迟……\n高隐私……",
        "example_good": "边缘计算的核心优势体现在以下三个方面：\n一、低延迟……\n二、高隐私……",
    },
]


def load_lexicon_mappings(path: Path = LEXICON_PATH):
    """加载词汇替换映射，失败时返回空列表（不影响主规则检查）。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    mappings = data.get("mappings", [])
    normalized = []
    for item in mappings:
        source = str(item.get("source", "")).strip()
        targets = item.get("target", [])
        if not source or not targets:
            continue
        if isinstance(targets, str):
            targets = [targets]
        normalized.append({
            "source": source,
            "target": [str(t).strip() for t in targets if str(t).strip()],
            "tags": item.get("tags", []),
        })
    return normalized


LEXICON_MAPPINGS = load_lexicon_mappings()


def build_code(rule_id: str):
    severity = "W" if rule_id.startswith("LX") else "E"
    return f"{severity}-{rule_id}"


def check_lexicon_substitutions(text: str):
    """检测口语化词汇并给出学术替换建议（LX类）。"""
    violations = []
    if not LEXICON_MAPPINGS:
        return violations

    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        for mapping in LEXICON_MAPPINGS:
            source = mapping["source"]
            idx = stripped.find(source)
            if idx >= 0:
                suggestions = " / ".join(mapping["target"][:3])
                violations.append({
                    "rule_id": "LX1",
                    "category": "词汇替换 / 口语到学术",
                    "line": i,
                    "col": idx + 1,
                    "text": stripped[:80],
                    "message": f"检测到可替换表达：{source}",
                    "suggestion": f"可替换为：{suggestions}",
                    "example_bad": source,
                    "example_good": suggestions,
                })
    return violations


def check_text(text: str, file_path: str = None):
    """检查文本，返回违规列表"""
    violations = []
    lines = text.split("\n")

    for rule in RULES:
        rule_id = rule["id"]
        mode = rule["mode"]
        pattern = rule["pattern"]
        msg = rule["message"]

        if mode == "line_start":
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped and re.search(pattern, stripped):
                    # 跳过纯列表项行
                    if re.match(r"^\d+[.、]|[（（]\d[））]", stripped):
                        continue
                    violations.append({
                        "rule_id": rule_id,
                        "category": rule["category"],
                        "line": i,
                        "col": 1,
                        "text": stripped[:80],
                        "message": msg,
                        "suggestion": rule.get("suggestion", ""),
                        "example_bad": rule.get("example_bad", ""),
                        "example_good": rule.get("example_good", ""),
                    })

        elif mode == "search":
            for i, line in enumerate(lines, 1):
                match = re.search(pattern, line)
                if match:
                    violations.append({
                        "rule_id": rule_id,
                        "category": rule["category"],
                        "line": i,
                        "col": match.start() + 1,
                        "text": line.strip()[:80],
                        "message": msg,
                        "suggestion": rule.get("suggestion", ""),
                        "example_bad": rule.get("example_bad", ""),
                        "example_good": rule.get("example_good", ""),
                    })

    # 词汇替换建议（不改变原有规则检查行为）
    violations.extend(check_lexicon_substitutions(text))

    return violations


def apply_auto_fixes(text: str):
    """低风险自动修复：标点、格式、部分短词替换。"""
    fixed = text
    stats = {
        "ascii_double_quotes": 0,
        "ascii_single_quotes": 0,
        "halfwidth_parentheses": 0,
        "markdown_bold": 0,
        "phrases": 0,
        "lexicon_short": 0,
    }

    # 1) 直引号 -> 中文弯引号（成对）
    fixed, n = re.subn(r'"([^"\n]{1,120})"', r'“\1”', fixed)
    stats["ascii_double_quotes"] += n
    fixed, n = re.subn(r"'([^'\n]{1,120})'", r"‘\1’", fixed)
    stats["ascii_single_quotes"] += n

    # 2) 半角括号 -> 全角括号
    fixed, n = re.subn(r"\(([^()\n]{1,120})\)", r"（\1）", fixed)
    stats["halfwidth_parentheses"] += n

    # 3) 删除 markdown 加粗标记
    fixed, n = re.subn(r"\*\*([^*\n]{1,120})\*\*", r"\1", fixed)
    stats["markdown_bold"] += n

    # 4) T2 常见词替换
    phrase_map = {
        "值得注意的是": "特别指出，",
        "很重要的是": "需要说明的是，",
        "不可忽视的是": "需要说明的是，",
        "需要特别说明的是": "需要说明的是，",
        "特别值得指出的是": "特别指出，",
    }
    for src, tgt in phrase_map.items():
        count = fixed.count(src)
        if count:
            fixed = fixed.replace(src, tgt)
            stats["phrases"] += count

    # 5) 词汇映射短词替换（保守策略）
    # 仅替换短词，避免长句模板引发语义偏移。
    for item in LEXICON_MAPPINGS:
        src = item["source"]
        targets = item["target"]
        if not targets:
            continue
        if len(src) > 8:
            continue
        if any(ch in src for ch in "（）()、，；：\n/ "):
            continue
        tgt = targets[0]
        count = fixed.count(src)
        if count:
            fixed = fixed.replace(src, tgt)
            stats["lexicon_short"] += count

    stats["total"] = sum(stats.values())
    return fixed, stats


def report(violations, file_path=None):
    """输出 pep8 风格报告：path:line:col: CODE message"""
    if not violations:
        print("WSS100 OK  未发现违规项")
        return

    # 统计
    by_code = {}
    err_count = 0
    warn_count = 0
    for v in violations:
        code = build_code(v["rule_id"])
        by_code[code] = by_code.get(code, 0) + 1
        if code.startswith("E-"):
            err_count += 1
        else:
            warn_count += 1

    print("\n" + "=" * 72)
    print("WSS-1 CHECK REPORT")
    if file_path:
        print(f"FILE: {file_path}")
    print(f"TOTAL: {len(violations)}  ERRORS: {err_count}  WARNINGS: {warn_count}")
    print("CODE SUMMARY: " + ", ".join(f"{k} x{v}" for k, v in sorted(by_code.items())))
    print("=" * 72)

    print("\nDETAILS (pep8-style):")
    sorted_violations = sorted(
        violations,
        key=lambda x: (
            0 if build_code(x["rule_id"]).startswith("E-") else 1,
            x["line"],
            x.get("col", 1),
            x["rule_id"],
        ),
    )

    file_ref = file_path if file_path else "<stdin>"
    for v in sorted_violations:
        code = build_code(v["rule_id"])
        col = v.get("col", 1)
        clause = f"条目:{v['rule_id']}"
        print(f"{file_ref}:{v['line']}:{col}: {code} {clause} {v['message']}")
        if v.get("text"):
            print(f"    命中: {v['text']}")
        if v.get("suggestion"):
            print(f"    建议: {v['suggestion']}")

    print("\n" + "=" * 72)
    print("CODE LEGEND: E=Error(MUST), W=Warning(SHOULD) | L/P/T/F/LX 对应规范章节")
    print("=" * 72 + "\n")


def report_json(violations, file_path=None, fix_info=None):
    """JSON 结构化报告，便于自动化接入。"""
    by_code = {}
    err_count = 0
    warn_count = 0
    items = []

    for v in sorted(violations, key=lambda x: (x["line"], x.get("col", 1), x["rule_id"])):
        code = build_code(v["rule_id"])
        by_code[code] = by_code.get(code, 0) + 1
        if code.startswith("E-"):
            err_count += 1
        else:
            warn_count += 1
        items.append({
            "code": code,
            "rule_id": v["rule_id"],
            "category": v["category"],
            "line": v["line"],
            "col": v.get("col", 1),
            "message": v["message"],
            "suggestion": v.get("suggestion", ""),
            "snippet": v.get("text", ""),
        })

    payload = {
        "standard": "WSS-1",
        "file": file_path,
        "summary": {
            "total": len(violations),
            "errors": err_count,
            "warnings": warn_count,
            "code_summary": by_code,
        },
        "fix": fix_info or {"enabled": False},
        "violations": items,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="WSS-1 学术写作风格检查器")
    parser.add_argument("path", nargs="?", help="待检查文件路径")
    parser.add_argument("--text", dest="text", help="直接检查文本")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取文本")
    parser.add_argument("--demo", action="store_true", help="运行内置示例")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")
    fix_group = parser.add_mutually_exclusive_group()
    fix_group.add_argument("--fix", action="store_true", help="启用低风险自动修复并写回文件")
    fix_group.add_argument("--fix-dry-run", action="store_true", help="预览低风险自动修复，不写回文件")
    return parser.parse_args(argv)


def load_input(args):
    """加载输入文本与来源信息。"""
    if args.text is not None:
        return args.text, None, "text"
    if args.stdin:
        return sys.stdin.read(), None, "stdin"
    if args.demo:
        demo_text = """
随着人工智能技术的不断发展，边缘计算越来越重要。
智能制造是AIoT最成熟的应用领域，他主要通过在生产线部署传感器网络实现智能化。
联邦学习（FL）是一种分布式机器学习方法，它可以在不共享原始数据的情况下进行协同训练。
据预测，到2025年全球物联网设备数量将突破百亿台。
预计2025年，全球物联网设备数量将突破750亿台。
主要特征包括：数据传输、边缘推理、自适应学习、实时控制。
感知层、网络层、应用层、平台层都需要统一管理。
值得注意的是，边缘计算可以显著降低时延。
"边缘计算"是指将计算能力下沉到网络边缘的一种架构。
边缘计算(Edge Computing)是指将计算能力下沉到网络边缘的一种架构。
适应环境分布的变化（即概念漂移）会对模型产生影响。
**关键**在于如何平衡性能和效率。
边缘计算的主要优势是——
低延迟，——
高隐私。
"""
        return demo_text, None, "demo"
    if args.path:
        p = Path(args.path)
        if not p.exists():
            print(f"文件不存在：{args.path}")
            sys.exit(1)
        return p.read_text(encoding="utf-8"), args.path, "file"

    print(__doc__)
    sys.exit(0)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    original_text, file_path, source_type = load_input(args)

    text_for_check = original_text
    fix_enabled = bool(args.fix or args.fix_dry_run)
    dry_run = bool(args.fix_dry_run)
    fix_info = {"enabled": fix_enabled, "dry_run": dry_run}
    if fix_enabled:
        fixed_text, fix_stats = apply_auto_fixes(original_text)
        fix_info.update({
            "stats": fix_stats,
            "changed": fixed_text != original_text,
            "source_type": source_type,
        })
        text_for_check = fixed_text

        if source_type == "file" and file_path and fixed_text != original_text and not dry_run:
            Path(file_path).write_text(fixed_text, encoding="utf-8")
            fix_info["write_back"] = True
        else:
            fix_info["write_back"] = False

    violations = check_text(text_for_check, file_path)

    if args.format == "json":
        report_json(violations, file_path=file_path, fix_info=fix_info)
    else:
        if fix_enabled:
            changed = "是" if fix_info.get("changed") else "否"
            dry_run_text = "是" if dry_run else "否"
            print(f"AUTO-FIX: 启用  发生修改: {changed}")
            print(f"AUTO-FIX DRY-RUN: {dry_run_text}")
            print(f"AUTO-FIX STATS: {fix_info.get('stats', {})}")
            if source_type == "file" and fix_info.get("write_back"):
                print(f"AUTO-FIX WRITE-BACK: 已写回文件 {file_path}")
            elif source_type == "file" and dry_run and fix_info.get("changed"):
                print("AUTO-FIX WRITE-BACK: dry-run模式，未写回文件")
        report(violations, file_path)
