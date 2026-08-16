"""平台适配器注册表：真实适配器 vs 模拟适配器。"""
from models import PLATFORM_CODES

from adapters.jd import JDAdapter
from adapters.mock import MockAdapter

# 已接入真实平台的适配器（其余平台接入后在此注册）
_REAL_ADAPTERS = {
    "jd": JDAdapter(),
    # "tmall": TmallAdapter(),
    # "douyin": DouyinAdapter(),
    # "pdd": PddAdapter(),
}


def get_adapter(code: str):
    """返回真实平台适配器；未接入的平台抛 KeyError。"""
    if code not in _REAL_ADAPTERS:
        raise KeyError(f"平台未接入（真实适配器）: {code}")
    return _REAL_ADAPTERS[code]


def get_mock_adapter(code: str) -> MockAdapter:
    """返回模拟适配器（黑客松演示用，不依赖真实平台资质）。"""
    if code not in PLATFORM_CODES:
        raise KeyError(f"未知平台代码: {code}")
    return MockAdapter(code)
