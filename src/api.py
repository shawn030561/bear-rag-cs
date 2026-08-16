"""HTTP 服务：把 RAG 客服引擎暴露为 API，供各平台 Webhook 调用。

运行（在项目根目录）：
    uvicorn api:app --app-dir src --reload
或：
    cd src && uvicorn api:app --reload

接口：
    GET  /health               健康检查
    POST /webhook/{platform}   真实平台回调入口（京东已配骨架，其余待接入）
    POST /demo/{platform}      模拟平台入口（黑客松演示，直接返回话术）
"""
import logging

from fastapi import Body, FastAPI, HTTPException

from adapters import get_adapter, get_mock_adapter
from engine import Engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("bear.api")

app = FastAPI(title="小熊电器 AI 智能客服", version="1.0")

# 全局单例：检索器/平台规则只加载一次
engine = Engine()


@app.get("/")
def root():
    return {
        "service": "小熊电器 AI 智能客服（RAG 话术生成）",
        "endpoints": {
            "health": "GET /health",
            "webhook": "POST /webhook/{jd|tmall|douyin|pdd}",
            "demo": "POST /demo/{jd|tmall|douyin|pdd}  body: {text, session_id?, buyer_id?}",
        },
    }


@app.get("/health")
def health():
    return {"ok": True, "service": "bear-rag-cs"}


@app.post("/webhook/{platform}")
async def webhook(platform: str, payload: dict = Body(...)):
    """真实平台回调：解析消息 → 生成话术 → 回发平台。"""
    try:
        adapter = get_adapter(platform)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        msg = adapter.parse_inbound(payload)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    reply = engine.reply(msg)

    try:
        adapter.push_reply(reply)
    except NotImplementedError as e:
        log.warning("回发未接入，仍返回已生成话术：%s", e)

    return {"ok": True, "reply": reply.to_dict()}


@app.post("/demo/{platform}")
async def demo(platform: str, payload: dict = Body(...)):
    """模拟平台入口：直接返回 AI 话术，供 curl 演示。"""
    try:
        adapter = get_mock_adapter(platform)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        msg = adapter.parse_inbound(payload)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    reply = engine.reply(msg)
    adapter.push_reply(reply)  # 模拟：仅打日志
    return {"ok": True, "reply": reply.to_dict()}
