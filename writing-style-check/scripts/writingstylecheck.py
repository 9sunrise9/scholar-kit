#!/usr/bin/env python3
"""
《物联网技术与系统设计》正文风格检查器
基于 WSS-1 规范，输出错误编号 + 说明 + 行号

用法：
    python3 writingstylecheck.py <文件路径>
    python3 writingstylecheck.py --text "你的文本"
    python3 writingstylecheck.py --stdin
"""

import re
import sys
import json
from pathlib import Path

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
                        "text": stripped[:80],
                        "message": msg,
                        "suggestion": rule.get("suggestion", ""),
                        "example_bad": rule.get("example_bad", ""),
                        "example_good": rule.get("example_good", ""),
                    })

        elif mode == "search":
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    match = re.search(pattern, line)
                    violations.append({
                        "rule_id": rule_id,
                        "category": rule["category"],
                        "line": i,
                        "text": line.strip()[:80],
                        "message": msg,
                        "suggestion": rule.get("suggestion", ""),
                        "example_bad": rule.get("example_bad", ""),
                        "example_good": rule.get("example_good", ""),
                    })

    return violations


def report(violations, file_path=None):
    """格式化输出报告"""
    if not violations:
        print("✅ 未发现 WSS-1 违规")
        return

    # 按规则ID分组
    by_rule = {}
    for v in violations:
        rid = v["rule_id"]
        if rid not in by_rule:
            by_rule[rid] = v

    print(f"\n{'='*60}")
    print(f" WSS-1 风格检查报告")
    if file_path:
        print(f" 文件：{file_path}")
    print(f" 违规总数：{len(violations)} 处，涵盖 {len(by_rule)} 条规则")
    print(f"{'='*60}\n")

    # 按类别分组输出
    current_category = None
    for v in sorted(violations, key=lambda x: (x["rule_id"].split(".")[0], x["rule_id"])):
        cat_prefix = v["rule_id"].split(".")[0]
        if v["category"] != current_category:
            current_category = v["category"]
            print(f"\n{'─'*60}")
            print(f" [{cat_prefix}] {current_category}")
            print(f"{'─'*60}")

        print(f"  🔴 [{v['rule_id']}] 第{v['line']}行")
        print(f"     原文：{v['text']}")
        print(f"     说明：{v['message']}")
        if v["suggestion"]:
            print(f"     建议：{v['suggestion']}")
        if v.get("example_good"):
            print(f"     ✅ 改写参考：{v['example_good']}")

    print(f"\n{'='*60}")
    print(f" 规则覆盖：L=语言基调  P=段落结构  T=技术内容  F=符号格式")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--text":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        violations = check_text(text)
        report(violations)

    elif sys.argv[1] == "--stdin":
        text = sys.stdin.read()
        violations = check_text(text)
        report(violations)

    elif Path(sys.argv[1]).exists():
        file_path = sys.argv[1]
        text = Path(file_path).read_text(encoding="utf-8")
        violations = check_text(text, file_path)
        report(violations, file_path)

    elif sys.argv[1] == "--demo":
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
        violations = check_text(demo_text)
        report(violations)

    else:
        print(f"文件不存在：{sys.argv[1]}")
        sys.exit(1)
