"""小熊电器 AI 智能客服 —— RAG 话术生成 Demo（Streamlit）。

运行：streamlit run src/app.py
包含三个 Tab：
  Demo A 话术生成 / Demo B 智能接待（多轮）/ Demo C 话术质量对比
"""
import json

import streamlit as st

from config import config
from retriever import Retriever
from generator import generate
from conversation import Conversation

st.set_page_config(page_title="小熊电器 AI 智能客服", page_icon="🐻", layout="wide")


@st.cache_resource
def get_retriever():
    return Retriever()


@st.cache_data
def load_platforms():
    return json.loads(config.RULES_FILE.read_text(encoding="utf-8"))["platforms"]


@st.cache_data
def load_sample_qa():
    return json.loads(config.SAMPLE_QA_FILE.read_text(encoding="utf-8"))["qa"]


retriever = get_retriever()
platforms = load_platforms()
sample_qa = load_sample_qa()

PLATFORM_NAMES = list(platforms.keys())
MODELS = ["deepseek-v4-pro", "deepseek-v4-flash"]
PRODUCTS_BY_ID = {p["id"]: p for p in retriever.products}


def format_product(r):
    p = r["product"]
    return f"【{p['name']}】{p['category']} / ¥{p.get('price','')}（相关度 {r['score']}）"


# ---------------- 侧边栏 ----------------
with st.sidebar:
    st.title("🐻 小熊 AI 客服")
    st.caption("基于 RAG 的电商智能客服话术生成")
    platform = st.selectbox("接待平台", PLATFORM_NAMES)
    model = st.selectbox("生成模型", MODELS, help="v4-pro 质量更高，v4-flash 更快")
    show_ctx = st.checkbox("显示检索到的产品上下文", value=True)
    st.divider()
    if not config.DEEPSEEK_API_KEY:
        st.error("未检测到 DEEPSEEK_API_KEY，请在 .env 中配置")

platform_info = platforms[platform]

st.title("🐻 小熊电器 · AI 智能客服")
st.caption("基于大模型 RAG：产品知识库 + 平台规则 → 实时生成客服话术，覆盖京东/天猫/抖音/拼多多")

tab_a, tab_b, tab_c = st.tabs(["🔤 话术生成 Demo A", "💬 智能接待 Demo B", "📊 对比数据 Demo C"])

# ---------------- Demo A 话术生成 ----------------
with tab_a:
    st.subheader("Demo A · 话术生成")
    st.markdown("输入一条买家咨询 → RAG 自动检索产品知识库 + 平台规则 → 生成带**卖点/对比/促单**的回复话术。")
    query = st.text_input("买家咨询", placeholder="例如：这款按摩器和SKG比有什么优势？")
    if st.button("生成话术", type="primary"):
        if not query.strip():
            st.warning("请先输入买家咨询")
        else:
            products = retriever.search(query.strip())
            if show_ctx:
                with st.expander("🔎 检索到的产品知识（Top3）", expanded=True):
                    for r in products:
                        st.markdown(f"- **{r['product']['name']}** · ¥{r['product'].get('price','')} · 相关度 `{r['score']}`")
                        st.markdown(f"  卖点：{'；'.join(r['product']['selling_points'])}")
            with st.spinner("小熊助手生成中…"):
                answer = generate(query.strip(), platform_info, products, model=model)
            _conv = Conversation()
            intent = _conv.detect_intent(query.strip())
            post = _conv.post(query.strip())
            st.markdown("### 🤖 AI 回复话术")
            st.success(answer)
            st.caption(f"岗位：{post} · 意图：{intent} · 命中：{'、'.join(r['product']['name'] for r in products)}")

# ---------------- Demo B 智能接待 ----------------
with tab_b:
    st.subheader("Demo B · 智能接待（多轮对话）")
    st.markdown("模拟买家多轮咨询，AI 自主完成「推荐 → 讲解 → 挖需 → 促单」，并**自动分流岗位**（售前 / 售中 / 售后）。")

    if "conv" not in st.session_state:
        st.session_state.conv = Conversation()
        st.session_state.chat = []

    if st.button("🔄 重置对话"):
        st.session_state.conv = Conversation()
        st.session_state.chat = []
        st.rerun()

    conv = st.session_state.conv

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    if prompt := st.chat_input("以买家身份提问，例如：想给爸妈买个养生壶，有推荐吗？"):
        st.session_state.chat.append({"role": "user", "content": prompt})
        conv.add("user", prompt)
        with st.chat_message("user"):
            st.write(prompt)

        products = retriever.search(prompt)
        hint = conv.stage_hint(prompt)
        intent = conv.detect_intent(prompt)
        post = conv.post(prompt)
        with st.spinner("小熊助手思考中…"):
            reply = generate(prompt, platform_info, products, conv.history, hint, model=model)

        st.session_state.chat.append({"role": "assistant", "content": reply})
        conv.add("assistant", reply)
        with st.chat_message("assistant"):
            st.write(reply)
            st.caption(f"岗位：{post} · 意图：{intent}")

# ---------------- Demo C 对比数据 ----------------
with tab_c:
    st.subheader("Demo C · AI vs 人工 话术质量对比")
    st.markdown("用样例咨询，对比 **人工客服话术** 与 **AI 生成话术**。")

    if st.button("⚡ 批量生成 AI 话术（10 条样例）", type="primary"):
        with st.spinner("正在生成全部对比话术，请稍候…"):
            progress = st.progress(0)
            for idx, qa in enumerate(sample_qa):
                # 直接用题目标注的相关产品，保证对比公平
                products = [{"product": PRODUCTS_BY_ID[pid], "score": 1.0}
                            for pid in qa["related_products"] if pid in PRODUCTS_BY_ID]
                pinfo = platforms[qa["platform"]]
                qa["ai_answer"] = generate(qa["query"], pinfo, products, model=model)
                progress.progress((idx + 1) / len(sample_qa))
            progress.empty()
        st.success("对比生成完成！")

    if sample_qa and all("ai_answer" in q for q in sample_qa):
        for qa in sample_qa:
            with st.container(border=True):
                st.markdown(f"**买家**（{qa['platform']} · {qa['stage']} · {qa['intent']}）：{qa['query']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("👤 **人工客服话术**")
                    st.info(qa["human_answer"])
                with c2:
                    st.markdown("🤖 **AI 生成话术**")
                    st.success(qa["ai_answer"])
    else:
        st.info("点击上方按钮，批量生成 AI 话术与人工话术做对比。")
