"""模拟平台适配器（黑客松演示用）：不真实对接平台，仅模拟消息进出。"""
import logging

from models import InboundMessage, OutboundReply

log = logging.getLogger("bear.adapter.mock")


class MockAdapter:
    """通用模拟适配器：接受简单 JSON，回复打印到日志，模拟平台回调闭环。"""

    def __init__(self, platform_code: str):
        self.platform_code = platform_code

    def parse_inbound(self, payload: dict) -> InboundMessage:
        text = (payload.get("text") or "").strip()
        if not text:
            raise ValueError("payload 缺少 text 字段")
        return InboundMessage(
            platform=self.platform_code,
            session_id=str(payload.get("session_id") or "demo"),
            buyer_id=str(payload.get("buyer_id") or "buyer-001"),
            text=text,
        )

    def push_reply(self, reply: OutboundReply) -> None:
        # 真实实现：这里应调用平台发消息 API 把话术发回买家。
        log.info(
            "[%s] 模拟回发 → 会话 %s | 意图 %s | %s",
            reply.platform, reply.session_id, reply.intent, reply.text,
        )
