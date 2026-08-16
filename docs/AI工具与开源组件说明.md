# AI 工具、模型、素材及开源组件说明

> 说明：写明工具/模型名称及版本、主要用途、外部数据或素材来源、开源组件及授权情况；没有的项目填「无」。

## 一、大模型 / AI 工具

| 名称 | 版本 | 主要用途 | 来源 |
|---|---|---|---|
| DeepSeek（deepseek-v4-pro） | v4 | 话术生成（主模型，RAG 生成层） | DeepSeek 官方 API（https://api.deepseek.com） |
| DeepSeek（deepseek-v4-flash） | v4 | 话术生成（低延迟备选） | DeepSeek 官方 API |

## 二、开源组件

| 名称 | 版本 | 主要用途 | 授权 |
|---|---|---|---|
| Python | 3.13.12 | 运行语言 | PSF License |
| Streamlit | 1.61.1 | 可视化 Demo 前端（三个 Tab） | Apache-2.0 |
| FastAPI | 0.141.1 | HTTP API（/webhook /demo） | MIT |
| uvicorn | 0.52.3 | ASGI 服务器 | BSD-3-Clause |
| pydantic | 2.13.4 | 消息模型校验 | MIT |
| python-dotenv | 1.2.2 | 读取 .env 密钥 | BSD-3-Clause |
| python-pptx | 1.0.2 | 生成方案 PPT | MIT |
| Pillow | 12.2.0 | 演示视频帧渲染 | HPND（Pillow License） |
| edge-tts | 7.2.8 | 演示视频中文配音 | MIT |
| FFmpeg | 9.0（gyan.dev full build） | 视频/音频编码封装 | LGPL/GPL（本机处理，未再分发二进制） |
| BM25 检索 | 自研实现 | 产品知识召回 | 无（公开算法，自研零依赖） |

## 三、外部数据 / 素材来源

| 项目 | 说明 | 来源 |
|---|---|---|
| 产品知识库 `data/products.json` | 8 款样例产品卖点/参数/竞品/FAQ | 自建样例（模拟小熊电器公开商品信息），正式使用需替换为官方商品中心数据 |
| 平台规则 `data/platform_rules.json` | 四平台优惠/售后/物流/话术风格 | 自建（基于各平台公开规则的一般描述） |
| 样例 QA `data/sample_qa.json` | 10 条咨询 + 人工参考话术 | 自建样例 |
| 图片 / 音乐 / 视频素材 | 无（画面均由代码绘制、配音由 TTS 合成） | 无 |
| 字体 | 微软雅黑 / 微软雅黑 Bold（系统自带） | Windows 系统字体，仅本机渲染，未嵌入分发 |
| 模型训练 / 微调 | 无（仅 API 调用，未训练、未微调） | 无 |

## 四、结论

- 大模型采用 **DeepSeek 官方 API** 调用，未训练/未微调；
- 全部代码组件均为 **开源且许可友好**（MIT / Apache-2.0 / BSD / PSF / HPND / LGPL），无商用授权冲突；
- 外部素材（图片、音乐、视频）**无**，画面与配音均为代码生成；
- 知识库为**自建样例数据**，正式上线前需替换为小熊电器官方授权数据。
