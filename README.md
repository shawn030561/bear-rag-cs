# 🐻 小熊电器 · AI 智能客服（RAG 话术生成）

基于大模型 **RAG（检索增强生成）** 的电商智能客服，融合**产品知识库**与**多平台规则**，实现买家咨询的**全岗位自主接待**——进线即自动分流（售前 / 售中 / 售后），无需人工分岗与转接，覆盖京东 / 天猫 / 抖音 / 拼多多 4 大渠道。

> 赛题来源：小熊电器黑客松命题 ——「打造可替代人工客服的 AI 智能客服」。对标千牛人工工作流：客户进线 → 系统分流 → 售前/售中 → 分流不精准转接，本方案用 AI 直接替代「分岗 + 分流 + 转接」。

## 功能特性

- **话术生成（Demo A）**：买家提问 → BM25 检索产品知识 + 平台规则 → DeepSeek 生成带「卖点 / 对比 / 促单」的回复话术。
- **岗位自动分流**：意图识别 → 自动路由 **售前 / 售中 / 售后**，替代人工分岗与转接。
- **智能接待（Demo B）**：多轮对话 + 意图识别 + 漏斗阶段跟踪，自主完成「推荐 → 讲解 → 挖需 → 促单」。
- **话术对比（Demo C）**：AI 话术 vs 人工话术，对齐赤兔名品三指标（接待量 / 满意度 / 转化率）。
- **平台感知**：京东 / 天猫 / 抖音 / 拼多多各自的话术风格、优惠、售后规则，自动切换。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置密钥（复制 .env.example 为 .env 并填入）
#    DEEPSEEK_API_KEY=sk-xxx
#    DEEPSEEK_BASE_URL=https://api.deepseek.com
#    DEEPSEEK_MODEL=deepseek-v4-pro

# 3. 启动可视化演示（浏览器自动打开 http://localhost:8501）
streamlit run src/app.py
```

### 也可用 HTTP 服务（供平台 Webhook 接入 / curl 演示）

```bash
uvicorn api:app --app-dir src --reload
```

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 生成话术（京东）
curl -X POST http://127.0.0.1:8000/demo/jd \
  -H "Content-Type: application/json" \
  -d '{"text":"想给爸妈买个养生壶","session_id":"demo-1"}'
```

接口：`GET /health` · `POST /webhook/{platform}`（真实平台回调）· `POST /demo/{platform}`（模拟演示）。

### 冒烟测试（不耗 API，秒出结果）

```bash
python smoke_test.py   # 预期输出 ALL SMOKE TESTS PASSED
```

## 项目结构

```
bear-rag-cs/
├── data/
│   ├── products.json          # 产品知识库（样例：小熊电器 8 款产品）
│   ├── platform_rules.json    # 4 平台规则（话术风格/优惠/售后/物流）
│   └── sample_qa.json         # 10 条样例咨询 + 人工参考话术（用于对比）
├── src/
│   ├── config.py              # 配置加载（.env）
│   ├── models.py              # 统一消息模型 + 平台代码映射
│   ├── retriever.py           # BM25 检索（中文分词，零外部依赖）
│   ├── generator.py           # DeepSeek 话术生成
│   ├── conversation.py        # 多轮对话 + 意图识别 + 岗位路由(售前/售中/售后)
│   ├── sessions.py            # 会话存储（内存，生产可换 Redis）
│   ├── engine.py              # RAG 客服引擎（校验→分流→检索→生成→回写）
│   ├── api.py                 # FastAPI HTTP 服务（/webhook /demo）
│   ├── app.py                 # Streamlit 前端（三个 Demo）
│   └── adapters/              # 平台适配器（统一网关 → 各平台消息格式）
│       ├── base.py            #   PlatformAdapter 协议
│       ├── mock.py            #   模拟适配器（演示用）
│       └── jd.py              #   京东适配器骨架（签名/鉴权 TODO）
├── docs/
│   ├── 方案PPT.pptx           # 方案 PPT（12 页）
│   ├── 方案PPT.html           # PPT 浏览器版（无需 Office）
│   ├── 交互Demo.html          # 零安装交互 Demo（双击即玩）
│   ├── 方案PPT.md             # PPT 大纲
│   ├── 技术路线.md            # 技术路线说明
│   ├── 解决方案.md / .pdf     # 解决方案（项目介绍+架构+流程+制作说明）
│   ├── AI工具与开源组件说明.md / .pdf  # 工具/模型/素材/开源组件及授权
│   ├── 项目介绍.md            # 100 字项目介绍
│   ├── 提交说明.md            # 提交材料总览
│   ├── 演示脚本.md            # 演示视频分镜脚本
│   └── 答辩Q&A.md             # 答辩预演
├── build_pptx.py              # PPT 生成脚本
├── build_pdf.py               # 解决方案 / AI 组件说明 PDF 生成脚本
├── smoke_test.py              # 冒烟测试
├── requirements.txt
└── .env.example               # 密钥模板（真实 .env 已 gitignore）
```

## 替换成真实数据

`data/` 下三个 JSON 是样例，替换字段结构即可换成小熊电器正式数据：

- `products.json`：产品名称、卖点、规格、竞品对比、FAQ。
- `platform_rules.json`：各平台优惠、售后、物流、话术风格。
- `sample_qa.json`：真实买家咨询 + 人工话术（用于对比评测）。

## 技术栈

- **语言**：Python 3.13
- **前端**：Streamlit
- **服务**：FastAPI + uvicorn
- **大模型**：DeepSeek（`deepseek-v4-pro` / `deepseek-v4-flash`，OpenAI 兼容接口）
- **检索**：BM25（字符 bigram 中文分词，零依赖；可平滑升级向量检索）

## 技术亮点

- **岗位自动分流**：`conversation.post()` 把意图映射到售前/售中/售后，进线即分流，无需转接。
- **可解释**：每次回复输出「命中产品 + 意图 + 岗位」，链路透明。
- **多平台适配**：统一网关 + Adapter 层隔离平台差异，风格自动切换。
- **可扩展**：知识库改 JSON 即更新，零训练成本；检索可平滑升级向量检索。

> ⚠️ 请勿将 `.env` 提交到公开仓库。
