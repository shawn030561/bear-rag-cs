"""平台适配器协议：把各平台消息格式统一为 InboundMessage / OutboundReply。"""
from typing import Protocol

from models import InboundMessage, OutboundReply


class PlatformAdapter(Protocol):
    """适配器只做两件事：解析进站消息、回发话术。

    parse_inbound：把平台回调的原始 payload 转成 InboundMessage；
    push_reply：把 OutboundReply 通过平台 API 发回给买家。
    """
    platform_code: str

    def parse_inbound(self, payload: dict) -> InboundMessage: ...

    def push_reply(self, reply: OutboundReply) -> None: ...
