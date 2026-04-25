# scholar-kit

面向学术写作与科研生产力的 AI 技能包，覆盖：

* 学术文稿格式转换（Markdown → docx / LaTeX）
* 学术图表绘制（TikZ / matplotlib）
* 学术写作风格检查（规则化检测与报告）

兼容 **Claude Code**、**OpenCode**、**GitHub Copilot**、**Codex** 等主流 AI 编程助手。

---

## 技能列表

| 技能 | 说明 | 触发关键词示例 |
|------|------|----------------|
| `academic-writing` | Markdown → docx / LaTeX 格式转换，pandoc 驱动 | "帮我把 md 转成 docx"、"导出 LaTeX" |
| `scientific-drawing` | TikZ / matplotlib 学术图表生成 | "画图"、"生成架构图"、"绘制流程图" |
| `writing-style-check` | 学术正文风格检查，输出可执行修改建议 | "检查写作规范"、"润色论文"、"风格检查" |

---

## 依赖说明

各技能所需的外部工具与库如下表所示。

### academic-writing

| 依赖 | 类型 | 版本要求 | 安装方式 |
|------|------|----------|----------|
| **pandoc** | 必需 | ≥ 3.0 | `brew install pandoc` / `sudo apt install pandoc` / [pandoc.org](https://pandoc.org/installing.html) |
| **Python** | 必需 | ≥ 3.9 | 系统自带或 `brew install python` / `sudo apt install python3` |
| **docx 模版** | 必需 | `.docx` | 用户自行提供，放项目根目录 |
| **watchdog** | 可选 | — | `pip install watchdog`（自动监控 md 文件变化） |
| **python-docx** | 可选 | — | `pip install python-docx`（辅助分析 docx 样式） |
| **fswatch** | 可选（macOS） | — | `brew install fswatch` |
| **inotify-tools** | 可选（Linux） | — | `sudo apt install inotify-tools` |

### scientific-drawing

#### TikZ 绘图

| 依赖 | 类型 | 版本要求 | 安装方式 |
|------|------|----------|----------|
| **LaTeX 发行版**（xelatex） | 必需 | TeX Live 2020+ / MacTeX 2020+ | `brew install --cask mactex` / `sudo apt install texlive-xetex texlive-latex-extra` |
| **xeCJK** | 必需 | 最新版 | TeX Live 自带 |
| **fontspec** | 必需 | 最新版 | TeX Live 自带 |
| **poppler-utils** | 必需 | 最新版 | `brew install poppler` / `sudo apt install poppler-utils` |
| **中文字体** | 必需 | — | macOS 系统自带 PingFang SC；Linux: `sudo apt install fonts-noto-cjk`；或安装[思源黑体](https://fonts.google.com/noto) |

#### Python matplotlib 绘图

| 依赖 | 类型 | 版本要求 | 安装方式 |
|------|------|----------|----------|
| **Python** | 必需 | ≥ 3.8 | 系统自带或 `brew install python` |
| **matplotlib** | 必需 | ≥ 3.5 | `pip install matplotlib` |
| **numpy** | 可选 | ≥ 1.20 | `pip install numpy` |
| **pandas** | 可选 | ≥ 1.3 | `pip install pandas` |
| **latexmk** | 可选 | — | TeX Live 自带 |
| **ImageMagick** | 可选 | — | `brew install imagemagick` |
| **Ghostscript** | 可选 | — | `brew install ghostscript` |

### writing-style-check

| 依赖 | 类型 | 版本要求 | 安装方式 |
|------|------|----------|----------|
| **Python** | 必需 | ≥ 3.9 | 系统自带或 `brew install python` / `sudo apt install python3` |

> 无第三方依赖，仅使用 Python 标准库。

---

## 安装

### For Humans

**选项一：交给 LLM agent 安装（推荐）**

把下面这段话复制粘贴给你的 LLM agent（Claude Code、OpenCode、Copilot 等）：

```
请按照以下指南帮我安装 scholar-kit：
https://raw.githubusercontent.com/sunyue/scholar-kit/main/install.md
```

**选项二：自己跑一键安装脚本**

```bash
curl -fsSL https://raw.githubusercontent.com/sunyue/scholar-kit/main/install.sh | bash
```

---

### For LLM Agents

拉取安装指南并照着执行：

```bash
curl -s https://raw.githubusercontent.com/sunyue/scholar-kit/main/install.md
```

---

## 仓库结构

```
scholar-kit/
├── README.md
├── install.sh                  # 交互式安装脚本（终端）
├── install.md                  # AI 向导安装提示词
├── academic-writing/
│   ├── SKILL.md                # 技能入口（AI 自动加载）
│   ├── README.md
│   └── scripts/                # pandoc 转换辅助脚本
├── scientific-drawing/
│   ├── SKILL.md
│   ├── README.md
│   └── references/             # 配色规范、TikZ/matplotlib 规则
└── writing-style-check/
    ├── SKILL.md
    ├── README.md
    └── references/             # 写作风格规则库
```

---

## License

MIT
