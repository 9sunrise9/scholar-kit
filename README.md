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
