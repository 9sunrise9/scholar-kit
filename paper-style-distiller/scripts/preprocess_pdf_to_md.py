#!/usr/bin/env python3
"""
PDF → 清洁 Markdown 预处理器
目标期刊: TAC / Automatica / JGCD / IEEE Transactions 全系列

输入:  paper-style-distiller/samples/zotero-control-guidance-decision-top-journals/*.pdf
输出:  paper-style-distiller/samples/preprocessed_md/*.md

噪声清除策略:
  1. 用 PyMuPDF 逐页提取文本块（带位置信息）
  2. 去除页眉/页脚（y 坐标极值区域的短行）
  3. 去除页码、DOI 行、Manuscript received 行、版权声明
  4. 跳过第1页前200字（通常是作者单位/摘要前缀噪声）
  5. 检测并截断 References 章节（不提取参考文献）
  6. 识别章节标题（全大写或编号标题）
  7. 输出带章节标记的 Markdown
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF


# ── 目标期刊白名单 ──────────────────────────────────────────────
TARGET_JOURNALS = [
    "ieee transactions on automatic control",
    "automatica",
    "journal of guidance, control, and dynamics",
    "ieee transactions on neural networks",
    "ieee transactions on cybernetics",
    "ieee transactions on control systems technology",
    "ieee transactions on systems",
    "ieee transactions on industrial",
    "ieee transactions on robotics",
    "ieee transactions on aerospace",
    "ieee transactions on signal",
    "ieee transactions on",
]


def is_target_journal(publication: str) -> bool:
    pub = publication.lower().strip()
    return any(j in pub for j in TARGET_JOURNALS)


# ── 噪声行检测 ───────────────────────────────────────────────────
_RE_PAGE_NUMBER   = re.compile(r"^\s*\d{1,4}\s*$")
_RE_VOLUME_INFO   = re.compile(r"\bvol\b.*\bno\b", re.I)
_RE_DOI           = re.compile(r"\b10\.\d{4,}/\S+", re.I)
_RE_COPYRIGHT     = re.compile(r"©|\bcopyright\b|\bauthorized licensed use\b", re.I)
_RE_MANUSCRIPT    = re.compile(r"\bmanuscript received\b|\bdate of publication\b|\breceived\b.*\bRevised\b", re.I)
_RE_INDEX_TERMS   = re.compile(r"^Index Terms[—–-]", re.I)
_RE_EMAIL         = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.I)
_RE_IEEE_HEADER   = re.compile(
    r"^(IEEE |AUTOMATICA|JOURNAL OF GUIDANCE|J\. GUID|AIAA |TRANSACTIONS ON )", re.I
)
_RE_RUNNING_HEAD  = re.compile(r"^[A-Z][A-Z\s,.:]+$")  # 全大写短行（页眉）
_RE_AFFIL_LINE    = re.compile(
    r"\b(university|institute|laboratory|department|college|school|"
    r"national|academy|center|centre|foundation)\b", re.I
)

# 参考文献章节开始的模式
_RE_REFS_HEADER = re.compile(
    r"^R\s*E\s*F\s*E\s*R\s*E\s*N\s*C\s*E\s*S\s*$"
    r"|^REFERENCES\s*$"
    r"|^References\s*$"
    r"|^\[1\]\s+\w",   # 直接从 [1] 开始的参考文献
    re.MULTILINE,
)

# 章节标题模式
_RE_SECTION_NUMBERED = re.compile(
    r"^(I{1,3}V?|V?I{0,3}|[IVX]+)\.\s+[A-Z]"   # 罗马数字: I. INTRODUCTION
    r"|^\d+\.\s+[A-Z]"                             # 阿拉伯数字: 1. Introduction
    r"|^[A-Z]\.\s+[A-Z]",                          # 字母: A. Problem Setup
)
_RE_SECTION_CAPS = re.compile(r"^[A-Z][A-Z\s]{4,40}$")  # 全大写章节标题


def is_noise_line(line: str, page_num: int, is_header_zone: bool) -> bool:
    """判断一行是否为噪声，返回 True 则丢弃。"""
    stripped = line.strip()
    if not stripped:
        return False  # 空行保留（段落分隔）

    # 纯页码
    if _RE_PAGE_NUMBER.match(stripped):
        return True

    # 页眉区域的短行（≤80字符）
    if is_header_zone and len(stripped) <= 80:
        if _RE_IEEE_HEADER.match(stripped):
            return True
        if _RE_RUNNING_HEAD.match(stripped) and len(stripped) <= 60:
            return True
        if _RE_VOLUME_INFO.search(stripped):
            return True

    # DOI 行
    if _RE_DOI.search(stripped) and len(stripped) < 120:
        return True

    # 版权声明
    if _RE_COPYRIGHT.search(stripped) and len(stripped) < 200:
        return True

    # Manuscript received
    if _RE_MANUSCRIPT.search(stripped) and len(stripped) < 200:
        return True

    # 邮件地址行（单位信息）
    if _RE_EMAIL.search(stripped) and len(stripped) < 160:
        return True

    # 第1页的机构行（前10行 & ≤120字符 & 包含机构关键词）
    if page_num == 0 and _RE_AFFIL_LINE.search(stripped) and len(stripped) < 150:
        return True

    return False


def detect_section_title(line: str) -> str | None:
    """如果是章节标题，返回标题文字；否则 None。"""
    stripped = line.strip()
    if _RE_SECTION_NUMBERED.match(stripped) and len(stripped) < 80:
        return stripped
    if _RE_SECTION_CAPS.match(stripped) and len(stripped) < 60:
        return stripped
    return None


def extract_clean_text(pdf_path: Path) -> str:
    """
    使用 PyMuPDF 提取 PDF 正文，返回清洁 Markdown 字符串。
    - 跳过前半页的单位/摘要前缀噪声
    - 识别页眉/页脚区域并去除
    - 截断 References 章节
    - 输出带 ## 章节标记的 Markdown
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    output_lines: list[str] = []
    found_refs = False

    for page_num, page in enumerate(doc):
        if found_refs:
            break

        page_rect = page.rect
        page_height = page_rect.height

        # 页眉/页脚区域阈值：上下各 7% 的高度
        header_threshold = page_height * 0.07
        footer_threshold = page_height * 0.93

        # 提取文本块，按阅读顺序排序（处理双栏布局）
        blocks = page.get_text("blocks", sort=True)

        page_lines: list[str] = []

        for block in blocks:
            # block: (x0, y0, x1, y1, text, block_no, block_type)
            if block[6] != 0:  # 跳过图片块
                continue

            y0 = block[1]
            y1 = block[3]
            text = block[4].strip()

            if not text:
                continue

            # 判断是否在页眉/页脚区域
            is_header_zone = (y0 < header_threshold) or (y1 > footer_threshold)

            # 按行处理块内文本
            for line in text.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue

                # 检查 References 章节开始
                if _RE_REFS_HEADER.match(stripped):
                    found_refs = True
                    break

                if is_noise_line(stripped, page_num, is_header_zone):
                    continue

                page_lines.append(stripped)

            if found_refs:
                break

        # 第1页特殊处理：删除 Abstract—/abstract— 之前的所有行
        if page_num == 0 and page_lines:
            abs_idx = None
            for i, ln in enumerate(page_lines):
                if re.match(r"^(Abstract|ABSTRACT)[—–\-\s]", ln, re.I):
                    abs_idx = i
                    break
            # 如果找到摘要行，保留摘要开始往后；否则跳过前5行（作者/机构噪声）
            if abs_idx is not None:
                page_lines = page_lines[abs_idx:]
            else:
                skip = min(5, len(page_lines) // 4)
                page_lines = page_lines[skip:]

        # 识别章节标题并格式化为 Markdown
        formatted_lines: list[str] = []
        for ln in page_lines:
            title = detect_section_title(ln)
            if title:
                formatted_lines.append(f"\n## {title}\n")
            else:
                formatted_lines.append(ln)

        if formatted_lines:
            output_lines.extend(formatted_lines)
            output_lines.append("")  # 页间空行

    doc.close()

    # 后处理：合并段落（相邻非空行可能是同一段落的换行）
    merged = merge_wrapped_lines(output_lines)
    return merged


def merge_wrapped_lines(lines: list[str]) -> str:
    """
    合并因 PDF 列宽导致的断行。
    规则：如果上一行不以句号/问号/感叹号结尾，且当前行不像章节标题，
    则与上一行合并（用空格）。
    """
    result: list[str] = []
    buffer = ""

    for line in lines:
        stripped = line.strip()

        # 空行 → 段落分隔
        if not stripped:
            if buffer:
                result.append(buffer)
                buffer = ""
            result.append("")
            continue

        # 章节标题（以 ## 开头）
        if stripped.startswith("##"):
            if buffer:
                result.append(buffer)
                buffer = ""
            result.append(stripped)
            continue

        # 判断是否续接上一行
        if buffer:
            # 上一行以完整句子结尾 → 新段落
            if re.search(r"[.!?]\s*$", buffer):
                result.append(buffer)
                buffer = stripped
            # 上一行以连字符结尾 → 去连字符拼接
            elif buffer.endswith("-"):
                buffer = buffer[:-1] + stripped
            # 否则续接
            else:
                buffer = buffer + " " + stripped
        else:
            buffer = stripped

    if buffer:
        result.append(buffer)

    return "\n".join(result)


def process_manifest(sample_dir: Path, out_dir: Path, filter_journals: bool = True) -> list[dict]:
    """读取 manifest.tsv，筛选目标期刊，处理 PDF，输出 MD。"""
    manifest_path = sample_dir / "manifest.tsv"
    if not manifest_path.exists():
        print(f"[ERROR] manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    processed = []
    skipped = []

    with open(manifest_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    for row in rows:
        pub = row.get("publication", "")
        copied = row.get("copied_file", "").strip()
        if not copied:
            continue

        # 从 copied_file 路径提取文件名
        pdf_name = Path(copied).name
        pdf_path = sample_dir / pdf_name

        if not pdf_path.exists():
            print(f"[WARN] PDF not found: {pdf_path}", file=sys.stderr)
            continue

        # 期刊过滤
        if filter_journals and not is_target_journal(pub):
            skipped.append({"file": pdf_name, "publication": pub, "reason": "journal_filter"})
            print(f"  [skip] {pub[:50]} → {pdf_name[:50]}")
            continue

        print(f"  [proc] {pub[:50]} → {pdf_name[:50]}")

        # 提取清洁文本
        try:
            clean_text = extract_clean_text(pdf_path)
        except Exception as e:
            print(f"  [ERROR] {pdf_path.name}: {e}", file=sys.stderr)
            skipped.append({"file": pdf_name, "publication": pub, "reason": str(e)})
            continue

        # 输出 MD
        md_name = pdf_path.stem + ".md"
        md_path = out_dir / md_name
        header = f"---\ntitle: {row.get('title','')}\npublication: {pub}\ndate: {row.get('date','')}\nkey: {row.get('itemKey','')}\n---\n\n"
        md_path.write_text(header + clean_text, encoding="utf-8")

        char_count = len(clean_text)
        word_count = len(clean_text.split())
        print(f"         → {md_name} ({char_count:,} chars, {word_count:,} words)")

        processed.append({
            "file": pdf_name,
            "md": md_name,
            "publication": pub,
            "chars": char_count,
            "words": word_count,
        })

    # 输出处理报告
    report_path = out_dir / "preprocess_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# PDF 预处理报告\n\n")
        f.write(f"## 处理成功 ({len(processed)} 篇)\n\n")
        f.write("| 文件 | 期刊 | 字符数 | 词数 |\n")
        f.write("|------|------|--------|------|\n")
        for p in processed:
            f.write(f"| {p['md'][:50]} | {p['publication'][:40]} | {p['chars']:,} | {p['words']:,} |\n")
        if skipped:
            f.write(f"\n## 跳过 ({len(skipped)} 篇)\n\n")
            for s in skipped:
                f.write(f"- `{s['file'][:60]}` — {s['reason']} — {s['publication']}\n")

    print(f"\n[done] {len(processed)} processed, {len(skipped)} skipped → {out_dir}")
    print(f"       report: {report_path}")

    return processed


def main():
    parser = argparse.ArgumentParser(description="PDF → 清洁 Markdown（去噪、去参考文献）")
    parser.add_argument("--sample-dir", required=True, help="PDF 样本目录（含 manifest.tsv）")
    parser.add_argument("--out-dir",    required=True, help="输出 Markdown 目录")
    parser.add_argument("--all-journals", action="store_true",
                        help="处理所有期刊（默认只处理 TAC/Automatica/JGCD/Trans）")
    args = parser.parse_args()

    sample_dir = Path(args.sample_dir)
    out_dir    = Path(args.out_dir)
    filter_j   = not args.all_journals

    print(f"期刊过滤: {'开启 (TAC/Automatica/JGCD/Trans)' if filter_j else '关闭 (全部)'}")
    process_manifest(sample_dir, out_dir, filter_journals=filter_j)


if __name__ == "__main__":
    main()
