"""统一消息模型与平台代码映射。

各平台适配器把外部消息格式统一转换成 InboundMessage，
引擎处理后返回 OutboundReply，再交回适配器回发。
"""
from dataclasses import dataclass

# 平台代码 → 中文名（与 data/platform_rules.json 里的 "id" 字段一致）
PLATFORM_CODES = {
    "jd": "京东",
    "tmall": "天猫",
    "douyin": "抖音",
    "pdd": "拼多多",
}


def platform_name(code: str) -> str:
    """把平台代码转为中文名，未知代码抛 ValueError。"""
    try:
        return PLATFORM_CODES[code]
    except KeyError:
        raise ValueError(f"未知平台代码: {code}（可选: {', '.join(PLATFORM_CODES)}）") from None


@dataclass(frozen=True)
class InboundMessage:
    """进入系统的买家消息（已由适配器统一）。"""
    platform: str       # 平台代码：jd / tmall / douyin / pdd
    session_id: str     # 会话 ID，用于多轮上下文
    text: str           # 买家咨询文本
    buyer_id: str = ""  # 买家标识（可选）


@dataclass(frozen=True)
class OutboundReply:
    """系统产出的回复（回发给适配器）。"""
    platform: str           # 中文平台名
    session_id: str
    text: str               # 生成的话术
    intent: str             # 识别出的意图
    post: str = ""          # 客服岗位：售前/售中/售后（替代人工分流）
    retrieved: tuple = ()   # 检索命中的产品名（用于可解释性）

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "session_id": self.session_id,
            "intent": self.intent,
            "post": self.post,
            "retrieved": list(self.retrieved),
            "text": self.text,
        }
