"""话术生成器：调用 DeepSeek，基于检索到的产品知识与平台规则生成客服话术。"""
import requests

from config import config


def chat(messages, model=None, max_tokens=2048, temperature=None):
    """调用 DeepSeek OpenAI 兼容接口，返回最终回答文本。"""
    url = config.DEEPSEEK_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or config.DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": max_tokens or config.MAX_TOKENS,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    msg = data["choices"][0]["message"]
    content = (msg.get("content") or "").strip()
    if not content:
        content = "[模型未产出最终话术，请重试或调大 max_tokens]"
    return content


SYSTEM_PROMPT = """你是小熊电器的 AI 智能客服「小熊助手」，负责在电商平台自主接待买家。

你必须遵守的话术三要素（根据买家问题灵活调整侧重点）：
1. 卖点：用 FAB 法则（特性-优势-利益），讲清产品能给买家带来的实际好处；
2. 对比：当买家在对比竞品时，给出差异化优势，不贬低竞品、不虚构参数；
3. 促单：结合平台优惠/活动制造合理的下单理由（如限时券、库存、大促）。

输出要求：
- 语气亲切自然，像真人客服，避免机器人腔和套话；
- 先正面解答买家问题，再顺势推荐或促单；
- 默认控制在 120 字以内，除非买家明确要求详细参数；
- 话术风格要贴合当前平台的话术特点；
- 只使用「检索到的产品知识」和「平台规则」里的真实信息，严禁编造参数、价格、优惠。"""


def build_messages(query, platform_info, products, history, stage_hint):
    platform = platform_info.get("platform", "")
    rules = platform_info.get("script_style", "")
    promotions = "；".join(platform_info.get("promotions", []))
    after_sale = "；".join(platform_info.get("after_sale", []))
    shipping = platform_info.get("shipping", "")

    product_blocks = []
    for r in products:
        p = r["product"]
        specs_text = "；".join(f"{k}={v}" for k, v in (p.get("specs") or {}).items())
        faq_text = "；".join(f"{item['q']}→{item['a']}" for item in p.get("faq", []))
        product_blocks.append(
            f"- 【{p['name']}】{p.get('category', '')} / 参考价 {p.get('price', '')} 元\n"
            f"  卖点：{'；'.join(p.get('selling_points', []))}\n"
            f"  规格：{specs_text}\n"
            f"  适用人群：{'、'.join(p.get('target_users', []))}\n"
            f"  竞品对比：{p.get('competitive_advantage', '')}\n"
            f"  常见问答：{faq_text}"
        )
    products_text = "\n".join(product_blocks) if product_blocks else "（无检索结果）"

    history_text = (
        "\n".join(f"{h['role']}: {h['content']}" for h in history[-6:]) if history else "（新会话）"
    )

    user = f"""当前平台：{platform}
平台话术风格：{rules}
平台优惠：{promotions}
平台售后：{after_sale}
物流：{shipping}

【检索到的产品知识】
{products_text}

【对话历史】
{history_text}

【当前买家咨询】
{query}

{f"【阶段提示】{stage_hint}" if stage_hint else ""}

请直接输出回复话术（不要解释、不要加前缀）。"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def generate(query, platform_info, products, history=None, stage_hint="", model=None):
    """生成话术。products 为 Retriever.search 返回的结果列表。"""
    messages = build_messages(query, platform_info, products, history or [], stage_hint)
    return chat(messages, model=model)
