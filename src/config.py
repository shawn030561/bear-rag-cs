"""配置加载：从项目根目录的 .env 或环境变量读取 DeepSeek 配置。

刻意用极简的 .env 解析器，避免引入 python-dotenv 依赖。
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def _load_dotenv(path: Path) -> None:
    """极简 .env 解析：只处理 KEY=VALUE 与 # 注释，不覆盖已存在的环境变量。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


_load_dotenv(ENV_FILE)


class Config:
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
    DEEPSEEK_FAST_MODEL = os.environ.get("DEEPSEEK_FAST_MODEL", "deepseek-v4-flash")
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))

    DATA_DIR = PROJECT_ROOT / "data"
    PRODUCTS_FILE = DATA_DIR / "products.json"
    RULES_FILE = DATA_DIR / "platform_rules.json"
    SAMPLE_QA_FILE = DATA_DIR / "sample_qa.json"


config = Config()
