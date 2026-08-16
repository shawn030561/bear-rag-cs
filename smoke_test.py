"""冒烟测试：不真实调用 DeepSeek，走通「适配器解析 → Engine → 回复」全链路。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import engine as eng
from models import InboundMessage
from adapters import get_adapter, get_mock_adapter


def fake_generate(query, platform_info, products, history=None, stage_hint="", model=None):
    top = products[0]["product"]["name"] if products else "无"
    return f"[{platform_info.get('platform')}] 回复关于「{query}」的话术（命中 {top}）"


eng.generate = fake_generate

e = eng.Engine()

# 1. 单轮：对比类意图
msg = InboundMessage(platform="jd", session_id="s1", text="这款按摩器和SKG比有什么优势？")
reply = e.reply(msg)
assert reply.platform == "京东", reply
assert reply.intent == "对比", reply.intent
assert reply.text and reply.retrieved, reply
print("engine.reply OK:", reply.to_dict())

# 2. 多轮：同 session 复用上下文
reply2 = e.reply(InboundMessage(platform="jd", session_id="s1", text="有优惠吗？"))
assert reply2.intent == "优惠", reply2.intent
assert len(e.sessions.get_or_create("s1").history) == 4
print("multi-turn OK, history len =", len(e.sessions.get_or_create("s1").history))

# 3. 适配器
mock = get_mock_adapter("tmall")
m = mock.parse_inbound({"text": "想给爸妈买个养生壶"})
assert m.platform == "tmall" and m.text
mock.push_reply(reply)

jd = get_adapter("jd")
m2 = jd.parse_inbound({"text": "能预约吗？", "buyerNick": "张三"})
assert m2.buyer_id == "张三"
print("adapters OK (mock + jd parse)")

# 4. 错误路径
try:
    get_adapter("tmall")  # 真实适配器未接入
except KeyError:
    print("get_adapter 未接入平台 -> KeyError OK")

try:
    e.reply(InboundMessage(platform="xx", session_id="s", text="hi"))
except ValueError:
    print("未知平台代码 -> ValueError OK")

# 5. FastAPI app 可导入
from api import app
print("FastAPI app OK:", app.title)

print("\nALL SMOKE TESTS PASSED")
