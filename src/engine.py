"""RAG 客服引擎：把检索 + 生成 + 多轮对话封装为无状态服务入口。"""
import json
import logging

from config import config
from generator import generate
from retriever import Retriever

from models import InboundMessage, OutboundReply, PLATFORM_CODES
from sessions import SessionStore

log = logging.getLogger("bear.engine")

# 生成失败时降级为转人工，避免客服链路断掉
FALLBACK_REPLY = "抱歉，我这边临时开小差了，已为您转接人工客服，请稍候～"


def _load_platforms() -> dict:
    data = json.loads(config.RULES_FILE.read_text(encoding="utf-8"))
    return data["platforms"]


class Engine:
    """RAG 话术生成引擎。持有检索器、平台规则、会话存储，暴露 reply()。"""

    def __init__(self, retriever=None, platforms=None, sessions=None, model=None):
        self.retriever = retriever or Retriever()
        self.platforms = platforms if platforms is not None else _load_platforms()
        self.sessions = sessions if sessions is not None else SessionStore()
        self.model = model  # None → 使用默认 deepseek-v4-pro

    def reply(self, msg: InboundMessage) -> OutboundReply:
        # 1. 平台校验
        platform_name = PLATFORM_CODES.get(msg.platform)
        if platform_name is None:
            raise ValueError(f"未知平台代码: {msg.platform}")
        platform_info = self.platforms.get(platform_name)
        if platform_info is None:
            raise ValueError(f"规则库缺少平台: {platform_name}")

        # 2. 输入校验（快速失败）
        text = (msg.text or "").strip()
        if not text:
            raise ValueError("消息文本为空")

        # 3. 取会话、识别意图、检索
        conv = self.sessions.get_or_create(msg.session_id)
        intent = conv.detect_intent(text)
        post = conv.post(text)
        hint = conv.stage_hint(text)
        products = self.retriever.search(text, top_k=3)

        # 4. 生成话术（失败降级转人工，避免客服断线）
        try:
            reply_text = generate(text, platform_info, products, conv.history, hint, self.model)
        except Exception:
            log.exception("话术生成失败 session=%s platform=%s", msg.session_id, platform_name)
            reply_text = FALLBACK_REPLY

        # 5. 回写会话历史
        conv.add("user", text)
        conv.add("assistant", reply_text)

        return OutboundReply(
            platform=platform_name,
            session_id=msg.session_id,
            text=reply_text,
            intent=intent,
            post=post,
            retrieved=tuple(r["product"]["name"] for r in products),
        )
