# -*- coding: utf-8 -*-
"""生成提交用 PDF：docs/解决方案.pdf 与 docs/AI工具与开源组件说明.pdf。

运行：python build_pdf.py
依赖：reportlab（内置 STSong-Light 中文字体，无需外部字体文件）
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
FONT = "STSong-Light"

# 配色（Bold Signal，与方案一致）
ACCENT = colors.HexColor("#F4571E")
SOFT = colors.HexColor("#FF8A4C")
GOLD = colors.HexColor("#E0A84C")
TEXT = colors.HexColor("#2B211A")
MUTED = colors.HexColor("#8A7D6D")
LINE = colors.HexColor("#E6DCCD")
BG = colors.HexColor("#FBF7F1")
RED = colors.HexColor("#D14A3C")

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

INTRO = ("小熊电器AI客服，基于大模型RAG，融合产品知识库与多平台规则，实现全自主接待，"
         "覆盖京东、天猫、抖音、拼多多四渠道，具备话术生成与多轮接待能力，人工转异常兜底，"
         "破解人力成本高、响应慢等五大痛点。")


def styles():
    s = getSampleStyleSheet()
    out = {}
    out["title"] = ParagraphStyle("title", parent=s["Title"], fontName=FONT,
                                  fontSize=24, leading=32, textColor=ACCENT,
                                  alignment=TA_LEFT, spaceAfter=4)
    out["subtitle"] = ParagraphStyle("subtitle", parent=s["Normal"], fontName=FONT,
                                     fontSize=11, leading=16, textColor=MUTED,
                                     alignment=TA_LEFT, spaceAfter=12)
    out["h2"] = ParagraphStyle("h2", parent=s["Heading2"], fontName=FONT,
                               fontSize=15, leading=20, textColor=TEXT,
                               spaceBefore=14, spaceAfter=8)
    out["h3"] = ParagraphStyle("h3", parent=s["Heading3"], fontName=FONT,
                               fontSize=12, leading=17, textColor=ACCENT,
                               spaceBefore=10, spaceAfter=6)
    out["body"] = ParagraphStyle("body", parent=s["Normal"], fontName=FONT,
                                 fontSize=10.5, leading=17, textColor=TEXT,
                                 alignment=TA_LEFT, spaceAfter=6)
    out["cell"] = ParagraphStyle("cell", parent=s["Normal"], fontName=FONT,
                                 fontSize=9.5, leading=14, textColor=TEXT)
    out["cellb"] = ParagraphStyle("cellb", parent=out["cell"], textColor=colors.white)
    out["small"] = ParagraphStyle("small", parent=out["body"], fontSize=9,
                                  textColor=MUTED, leading=14)
    return out


def P(text, st):
    return Paragraph(text, st)


def section(doc, elems, num, title):
    elems.append(P(f"{num}　{title}", styles()["h2"]))


def build_solution():
    st = styles()
    doc = SimpleDocTemplate(str(DOCS / "解决方案.pdf"), pagesize=A4,
                            leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title="小熊电器 AI 智能客服 —— 解决方案",
                            author="小熊电器")
    E = []

    # 封面标题
    E.append(P("小熊电器 AI 智能客服", st["title"]))
    E.append(P("基于大模型 RAG · 融合产品知识库与多平台规则 · 可替代人工客服", st["subtitle"]))
    E.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceAfter=10))

    # 一、项目介绍
    section(doc, E, "一", "项目介绍（100 字以内）")
    intro_box = Table([[P(INTRO, ParagraphStyle("intro", parent=st["body"],
                                                fontSize=12, leading=20,
                                                backColor=BG, textColor=TEXT))]],
                      colWidths=[170 * mm])
    intro_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, ACCENT),
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    E.append(intro_box)
    E.append(P(f"字数：{len(INTRO)} 字（含标点、字母、数字）", st["small"]))

    # 二、核心定位
    section(doc, E, "二", "核心定位")
    E.append(P("AI 智能客服作为 <b>全自主接待单元</b>，直接面向买家进行<b>售前咨询应答、产品推荐、售后问题处理</b>，"
               "覆盖京东 / 天猫 / 抖音 / 拼多多 4 大电商渠道；人工客服转为<b>异常兜底与升级处理</b>。", st["body"]))
    E.append(P("两条核心能力：", st["h3"]))
    E.append(P("① <b>话术生成</b> —— 基于 RAG 检索产品知识 + 平台规则，实时生成贴合买家问题的回复话术；", st["body"]))
    E.append(P("② <b>智能接待</b> —— 多轮对话上下文理解，主动引导、推荐、促单，覆盖「推荐 → 讲解 → 挖需 → 核心问答解决后促单」全链路。", st["body"]))
    E.append(P("对应破解的五大痛点：① 人力成本高 ② 响应时效受人力限制 ③ 标准化难统一 ④ 无 AI 自主接待能力 ⑤ 多平台规则适配难。", st["body"]))

    # 三、技术架构
    section(doc, E, "三", "技术架构（五层）")
    rows = [
        [P("层", st["cellb"]), P("职责", st["cellb"]), P("实现", st["cellb"])],
        [P("数据层", st["cell"]), P("产品知识、平台规则、样例咨询", st["cell"]), P("data/*.json（结构化、可替换）", st["cell"])],
        [P("检索层", st["cell"]), P("从知识库召回与问题相关的产品", st["cell"]), P("BM25 + 中文字符 bigram 分词", st["cell"])],
        [P("生成层", st["cell"]), P("基于检索结果 + 规则生成话术", st["cell"]), P("DeepSeek（OpenAI 兼容接口）", st["cell"])],
        [P("对话层", st["cell"]), P("多轮上下文、意图识别、岗位路由", st["cell"]), P("conversation.py（售前/售中/售后）", st["cell"])],
        [P("应用层", st["cell"]), P("可演示的 Web 界面 + API", st["cell"]), P("Streamlit + FastAPI", st["cell"])],
    ]
    t = Table(rows, colWidths=[26 * mm, 70 * mm, 74 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    E.append(t)
    E.append(Spacer(1, 6))
    E.append(P("数据流：<b>买家咨询 → 意图识别（售前/售中/售后）→ BM25 检索 → DeepSeek 生成 → 回复（含岗位/意图/命中）</b>", st["body"]))

    # 四、工作流程
    section(doc, E, "四", "工作流程（RAG）")
    steps = [
        ("1. 意图识别", "关键词规则分类（售前推荐 / 产品对比 / 参数 / 优惠 / 物流 / 售后 / 使用）。"),
        ("2. 检索 Retrieval", "BM25 对产品文档打分，召回 Top-K 最相关产品；平台规则按当前渠道注入。"),
        ("3. 增强 Augmented", "将「产品卖点/规格/竞品/FAQ」+「平台优惠/售后/话术风格」拼进 Prompt。"),
        ("4. 生成 Generation", "DeepSeek 按「卖点 FAB + 对比 + 促单」三要素生成贴合平台风格的客服话术。"),
    ]
    for head, body in steps:
        E.append(P(f"<b>{head}</b>：{body}", st["body"]))
    E.append(P("<b>多平台适配</b>：一个模型 + 平台规则注入，京东/天猫/抖音/拼多多话术风格、优惠、售后自动切换，无需训练四套模型。", st["body"]))

    # 五、制作说明
    section(doc, E, "五", "制作说明")
    rows = [
        [P("交付物", st["cellb"]), P("制作方式", st["cellb"])],
        [P("可运行代码 src/", st["cell"]), P("Python 3.13 + FastAPI + Streamlit，RAG 引擎（校验→分流→检索→生成→回写）", st["cell"])],
        [P("演示视频 演示视频.mp4", st["cell"]), P("Pillow 逐帧渲染聊天动画 + edge-tts 中文配音 + FFmpeg 合成 1080p", st["cell"])],
        [P("方案 PPT 方案PPT.pptx", st["cell"]), P("python-pptx 脚本生成（12 页，可编辑）", st["cell"])],
        [P("交互 Demo 交互Demo.html", st["cell"]), P("纯 HTML/JS 离线版，内置意图识别 + 岗位分流 + 四平台预置话术", st["cell"])],
        [P("冒烟测试 smoke_test.py", st["cell"]), P("不耗 API，验证检索→分流→生成链路可用", st["cell"])],
    ]
    t = Table(rows, colWidths=[52 * mm, 118 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    E.append(t)

    # 六、交付物清单
    section(doc, E, "六", "交付物清单")
    E.append(P("src/（代码）、data/（样例知识库）、docs/（PPT / 视频 / 交互 Demo / 本方案 / 技术路线 / AI 组件说明）、"
               "README.md、requirements.txt、build_pptx.py、build_pdf.py、make_demo_video.py、smoke_test.py。", st["body"]))
    E.append(P("⚠️ .env（含真实密钥）不随提交包分发，仅提供 .env.example。", ParagraphStyle("warn", parent=st["small"], textColor=RED)))

    doc.build(E)
    print("已生成 ->", DOCS / "解决方案.pdf")


def build_ai_components():
    st = styles()
    doc = SimpleDocTemplate(str(DOCS / "AI工具与开源组件说明.pdf"), pagesize=A4,
                            leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title="AI 工具、模型、素材及开源组件说明",
                            author="小熊电器")
    E = []
    E.append(P("AI 工具、模型、素材及开源组件说明", st["title"]))
    E.append(P("写明工具/模型名称及版本、主要用途、外部数据或素材来源、开源组件及授权情况；没有的项目填「无」。", st["subtitle"]))
    E.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceAfter=10))

    def tbl(header, rows, widths):
        data = [[P(h, st["cellb"]) for h in header]]
        data += [[P(c, st["cell"]) for c in row] for row in rows]
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return t

    section(doc, E, "一", "大模型 / AI 工具")
    E.append(tbl(["名称", "版本", "主要用途", "来源"],
                 [["DeepSeek（deepseek-v4-pro）", "v4", "话术生成（主模型，RAG 生成层）", "DeepSeek 官方 API（https://api.deepseek.com）"],
                  ["DeepSeek（deepseek-v4-flash）", "v4", "话术生成（低延迟备选）", "DeepSeek 官方 API"]],
                 [52 * mm, 16 * mm, 58 * mm, 44 * mm]))

    section(doc, E, "二", "开源组件")
    E.append(tbl(["名称", "版本", "主要用途", "授权"],
                 [["Python", "3.13.12", "运行语言", "PSF License"],
                  ["Streamlit", "1.61.1", "可视化 Demo 前端（三个 Tab）", "Apache-2.0"],
                  ["FastAPI", "0.141.1", "HTTP API（/webhook /demo）", "MIT"],
                  ["uvicorn", "0.52.3", "ASGI 服务器", "BSD-3-Clause"],
                  ["pydantic", "2.13.4", "消息模型校验", "MIT"],
                  ["python-dotenv", "1.2.2", "读取 .env 密钥", "BSD-3-Clause"],
                  ["python-pptx", "1.0.2", "生成方案 PPT", "MIT"],
                  ["Pillow", "12.2.0", "演示视频帧渲染", "HPND（Pillow License）"],
                  ["edge-tts", "7.2.8", "演示视频中文配音", "MIT"],
                  ["FFmpeg", "9.0（gyan.dev full build）", "视频/音频编码封装", "LGPL/GPL（本机处理，未再分发二进制）"],
                  ["BM25 检索", "自研实现", "产品知识召回", "无（公开算法，自研零依赖）"]],
                 [34 * mm, 34 * mm, 56 * mm, 46 * mm]))

    section(doc, E, "三", "外部数据 / 素材来源")
    E.append(tbl(["项目", "说明", "来源"],
                 [["产品知识库 products.json", "8 款样例产品卖点/参数/竞品/FAQ", "自建样例（模拟小熊电器公开商品信息），正式使用需替换为官方商品中心数据"],
                  ["平台规则 platform_rules.json", "四平台优惠/售后/物流/话术风格", "自建（基于各平台公开规则的一般描述）"],
                  ["样例 QA sample_qa.json", "10 条咨询 + 人工参考话术", "自建样例"],
                  ["图片 / 音乐 / 视频素材", "无（画面由代码绘制、配音由 TTS 合成）", "无"],
                  ["字体", "微软雅黑 / 微软雅黑 Bold（系统自带）", "Windows 系统字体，仅本机渲染，未嵌入分发"],
                  ["模型训练 / 微调", "无（仅 API 调用，未训练、未微调）", "无"]],
                 [40 * mm, 62 * mm, 68 * mm]))

    section(doc, E, "四", "结论")
    E.append(P("① 大模型采用 DeepSeek 官方 API 调用，未训练、未微调；", st["body"]))
    E.append(P("② 全部代码组件均为开源且许可友好（MIT / Apache-2.0 / BSD / PSF / HPND / LGPL），无商用授权冲突；", st["body"]))
    E.append(P("③ 外部素材（图片、音乐、视频）<b>无</b>，画面与配音均为代码生成；", st["body"]))
    E.append(P("④ 知识库为自建样例数据，正式上线前需替换为小熊电器官方授权数据。", st["body"]))

    doc.build(E)
    print("已生成 ->", DOCS / "AI工具与开源组件说明.pdf")


if __name__ == "__main__":
    print("项目介绍字数：", len(INTRO))
    build_solution()
    build_ai_components()
