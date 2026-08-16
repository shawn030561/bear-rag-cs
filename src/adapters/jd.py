"""京东商家开放平台适配器（骨架）。

真实对接京东客服消息需要：
1. 在京东商家开放平台（open.jd.com）创建应用，获取 app_key / app_secret；
2. 商家 OAuth 授权，换取 access_token；
3. 订阅买家消息回调，京东会把消息 POST 到本服务的 /webhook/jd；
4. 校验回调签名 → 解析买家消息 → 生成话术 → 调用京东「发消息」API 回发。

本文件为骨架：签名校验与消息回发均为 TODO，接入前请以京东官方文档为准。
"""
import logging

from models import InboundMessage, OutboundReply

log = logging.getLogger("bear.adapter.jd")


class JDAdapter:
    platform_code = "jd"

    def __init__(self, app_key: str = "", app_secret: str = ""):
        self.app_key = app_key or ""
        self.app_secret = app_secret or ""

    def verify_signature(self, payload: dict, headers: dict) -> bool:
        """校验京东回调签名，防止伪造消息。

        TODO(接入)：按京东官方签名规则，用 app_secret 对回调参数计算签名，
        与请求中的 sign 对比。未实现前拒绝接入生产。
        """
        raise NotImplementedError("京东回调签名校验待实现")

    def parse_inbound(self, payload: dict) -> InboundMessage:
        # TODO(接入)：把京东咚咚消息体映射为 InboundMessage。
        # 真实字段大致含：买家昵称/ID、会话 ID、消息文本、消息时间戳等。
        text = (payload.get("text") or "").strip()
        if not text:
            raise ValueError("京东消息体缺少 text 字段")
        return InboundMessage(
            platform=self.platform_code,
            session_id=str(payload.get("session_id") or "jd-session"),
            buyer_id=str(payload.get("buyer_id") or payload.get("buyerNick") or ""),
            text=text,
        )

    def push_reply(self, reply: OutboundReply) -> None:
        # TODO(接入)：调用京东「客服发消息」API，把 reply.text 发给买家。
        # 需带 access_token + 签名；失败记录日志并转人工兜底。
        log.warning("[京东·未接入] 话术已生成但未真实回发（TODO）：%s", reply.text)
