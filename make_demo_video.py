# -*- coding: utf-8 -*-
"""生成演示视频：Pillow 渲染聊天动画 + edge-tts 中文配音 + ffmpeg 合成 1080p mp4。

运行：python make_demo_video.py  → 输出 docs/演示视频.mp4
依赖：Pillow / edge-tts / ffmpeg（PATH 内）
"""
import asyncio
import shutil
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------- 配色（Bold Signal，与方案一致） ----------
BG     = (0x17, 0x11, 0x0C)
CARD   = (0x22, 0x1A, 0x13)
CARD2  = (0x2A, 0x20, 0x17)
ACCENT = (0xF4, 0x57, 0x1E)
SOFT   = (0xFF, 0x8A, 0x4C)
GOLD   = (0xE0, 0xA8, 0x4C)
TEXT   = (0xF6, 0xF0, 0xE6)
MUTED  = (0xA9, 0x9C, 0x8B)
LINE   = (0x3A, 0x2E, 0x24)
WHITE  = (255, 255, 255)

W, H = 1920, 1080
FPS = 30
TYPING_CPS = 26          # 打字速度（字符/秒）
PAD_SEC = 0.7            # 每段配音后留白

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "docs" / "_frames"
AUDIO = ROOT / "docs" / "_audio"
OUT = ROOT / "docs" / "演示视频.mp4"


def find_font(bold=False):
    for p in [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
    ]:
        if Path(p).exists():
            return p
    raise RuntimeError("找不到中文字体")


FONT = find_font(False)
FONT_B = find_font(True)


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def wrap(text, font, maxw):
    lines, cur = [], ""
    for ch in text:
        if font.getlength(cur + ch) <= maxw:
            cur += ch
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def chip(d, x, y, label, value, color):
    f = fnt(22, True)
    lab = f" {label}：{value} "
    w = int(f.getlength(lab)) + 8
    rr(d, [x, y, x + w, y + 40], 20, fill=CARD, outline=color, width=2)
    d.text((x + 4, y + 8), label, font=f, fill=color)
    return x + w


# ---------- 场景数据 ----------
SCENES = [
    dict(title="小熊电器 AI 智能客服", subtitle="基于大模型 RAG · 可替代人工客服", platform=None,
         narration="各位评委好，这是小熊电器A I智能客服。它基于大模型R A G检索增强生成，融合产品知识库与多平台规则，具备自主应答、话术实时生成、多轮对话、跨渠道接待四大能力。",
         beats=[]),
    dict(title="人工客服的五大痛点", subtitle="① 人力成本高 · ② 响应受人力限制 · ③ 标准化难统一\n④ 无A I自主接待 · ⑤ 多平台规则适配难", platform=None,
         narration="当前人工客服有五大痛点。人力成本高，随业务线性扩张；响应时效受人力限制；话术水平参差不齐；现有机器人只能做人工辅助，没有跑通无人化接待；多平台规则各不相同，容易记混出错。",
         beats=[]),
    dict(platform="jd",
         narration="第一条核心能力，话术生成。买家问对比问题，A I先做R A G检索命中产品知识，再实时生成带卖点、对比、促单三要素的回复。",
         beats=[
             ("user", "这款按摩器和SKG比有什么优势？", None),
             ("ai", "亲，小熊K3在同价位里很少见地做了「揉捏+热敷」二合一，比SKG同档大约便宜30%，还不用下载App、一键启动。京东自营正品，满199减30，喜欢可以先拍下～",
              {"岗位": "售前", "意图": "对比", "命中": "小熊颈椎按摩器 K3"}),
         ]),
    dict(platform="jd",
         narration="第二条核心能力，智能接待。A I具备多轮上下文理解，主动引导、推荐、促单，覆盖推荐、讲解、挖需、核心问答解决后促单的全链路。",
         beats=[
             ("user", "想给爸妈买个养生壶，有推荐吗？", None),
             ("ai", "亲，给爸妈买很推荐小熊养生壶1.5L，12大功能一键煮茶、药膳，55度保温加12小时预约。请问爸妈平时煮花茶还是药膳呢？",
              {"岗位": "售前", "意图": "推荐", "命中": "小熊养生壶 1.5L"}),
             ("user", "能预约吗？", None),
             ("ai", "可以的，支持12小时预约，睡前设定，早上自动煮好，不用早起，特别适合长辈。",
              {"岗位": "售前", "意图": "使用", "命中": "小熊养生壶 1.5L"}),
             ("user", "现在下单有优惠吗？", None),
             ("ai", "有的，现在京东满199减30，叠店铺券更划算，自营次日达。喜欢的话现在拍最合适哦～",
              {"岗位": "售中", "意图": "优惠", "命中": "小熊养生壶 1.5L"}),
         ]),
    dict(platform="pdd",
         narration="同时，A I具备平台感知的差异化回复，京东、天猫、抖音、拼多多各自的优惠和售后规则自动适配，避免记混出错。这里演示拼多多的售后处理。",
         beats=[
             ("user", "养生壶不想要了能退吗？", None),
             ("ai", "亲，不想要可以退的哈，支持7天无理由，有运费险。是哪里不满意呀？现在百亿补贴价挺划算的，可以再考虑下～",
              {"岗位": "售后", "意图": "售后", "命中": "小熊养生壶 1.5L"}),
         ]),
    dict(title="全自主接待 · 人工兜底", subtitle="五大痛点逐一解决 · 覆盖京东 / 天猫 / 抖音 / 拼多多", platform=None,
         narration="总结。A I自主接待售前咨询、产品推荐、售后处理，覆盖京东、天猫、抖音、拼多多四大渠道，五大痛点逐一解决，人工客服转为异常兜底和升级处理。谢谢各位评委。",
         beats=[]),
]

PLATFORMS = [("jd", "京东"), ("tmall", "天猫"), ("douyin", "抖音"), ("pdd", "拼多多")]


def is_card(sc):
    return bool(sc.get("title")) and not sc["beats"]


# ---------- 渲染单帧 ----------
def render(fidx, sc, msgs, show_card, narration):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    if show_card:
        d.rectangle([0, H - 12, W, H], fill=ACCENT)
        d.ellipse([W / 2 - 40, 320, W / 2 + 40, 400], fill=ACCENT)
        d.text((W / 2, 452), sc["title"], font=fnt(66, True), fill=TEXT, anchor="ma")
        sy = 556
        for sl in sc["subtitle"].split("\n"):
            d.text((W / 2, sy), sl, font=fnt(34), fill=SOFT, anchor="ma")
            sy += 54
    else:
        # 页眉
        d.ellipse([90, 46, 126, 82], fill=ACCENT)
        d.text((142, 58), "小熊电器 AI 智能客服", font=fnt(40, True), fill=TEXT, anchor="lm")
        d.text((142, 102), "岗位自动分流 · 四平台话术 · RAG 生成", font=fnt(22), fill=MUTED, anchor="lm")
        # 平台页签（从右往左排）
        px = W - 90
        for code, name in reversed(PLATFORMS):
            active = (code == sc["platform"])
            w = 120
            rr(d, [px - w, 48, px, 94], 23, fill=(ACCENT if active else CARD),
               outline=(ACCENT if active else LINE), width=2)
            d.text((px - w / 2, 71), name, font=fnt(24, True),
                   fill=(WHITE if active else MUTED), anchor="mm")
            px -= w + 14
        # 分流提示条
        rr(d, [90, 126, W - 90, 172], 22, fill=CARD, outline=LINE, width=1)
        hint = "进线即自动分流：售前 ／ 售中 ／ 售后   →   RAG 检索 + 生成   →   秒级回复、无需转接"
        d.text((W / 2, 149), hint, font=fnt(22), fill=SOFT, anchor="mm")

        # 对话区
        y = 206
        f = fnt(27)
        for role, text, chips in msgs:
            lines = wrap(text, f, 940)
            bh = 24 + len(lines) * 44
            if role == "user":
                tw = max(f.getlength(l) for l in lines)
                bw = int(tw) + 52
                rr(d, [W - 90 - bw, y, W - 90, y + bh], 20, fill=ACCENT)
                ty = y + 12
                for l in lines:
                    d.text((W - 116, ty), l, font=f, fill=WHITE, anchor="ra")
                    ty += 44
                y += bh + 26
            else:
                tw = max(f.getlength(l) for l in lines)
                bw = int(tw) + 52
                rr(d, [90, y, 90 + bw, y + bh], 18, fill=CARD, outline=LINE, width=1)
                d.rectangle([90, y + 8, 98, y + bh - 8], fill=SOFT)
                ty = y + 12
                for l in lines:
                    d.text((124, ty), l, font=f, fill=TEXT)
                    ty += 44
                cy = y + bh + 8
                cx = 98
                for k in ("岗位", "意图", "命中"):
                    v = chips.get(k, "")
                    color = SOFT if k == "岗位" else (GOLD if k == "意图" else MUTED)
                    cx = chip(d, cx, cy, k, v, color) + 14
                y = cy + 48

    # 底部字幕
    fcap = fnt(28)
    cap_lines = wrap(narration, fcap, W - 320)
    cap_y = 936
    box_h = 34 + len(cap_lines) * 40
    rr(d, [160, cap_y - 16, W - 160, cap_y - 16 + box_h], 22, fill=(10, 8, 6))
    for i, l in enumerate(cap_lines):
        d.text((W / 2, cap_y + i * 40), l, font=fcap, fill=TEXT, anchor="ma")

    return img


# ---------- 配音 ----------
async def gen_narration():
    import edge_tts
    AUDIO.mkdir(exist_ok=True)
    await asyncio.gather(*[
        edge_tts.Communicate(sc["narration"], "zh-CN-XiaoxiaoNeural").save(str(AUDIO / f"n{i}.mp3"))
        for i, sc in enumerate(SCENES)
    ])


def dur_of(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    return float(out.stdout.strip())


def build_audio(scene_durs):
    clips = []
    for i, d in enumerate(scene_durs):
        wav = AUDIO / f"n{i}.wav"
        subprocess.run(["ffmpeg", "-y", "-i", str(AUDIO / f"n{i}.mp3"),
                        "-af", "apad", "-t", f"{d:.3f}", "-ar", "24000", "-ac", "1",
                        str(wav)], capture_output=True)
        with wave.open(str(wav), "rb") as wf:
            clips.append((wf.getparams(), wf.readframes(wf.getnframes())))
    out = AUDIO / "full.wav"
    with wave.open(str(out), "wb") as wf:
        wf.setparams(clips[0][0])
        for _, data in clips:
            wf.writeframes(data)
    return out


def main():
    shutil.rmtree(FRAMES, ignore_errors=True)
    shutil.rmtree(AUDIO, ignore_errors=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    print("生成配音…")
    asyncio.run(gen_narration())

    scene_durs = []
    for i, sc in enumerate(SCENES):
        nd = dur_of(AUDIO / f"n{i}.mp3")
        typing = sum(len(t) for _, t, _ in sc["beats"]) / TYPING_CPS if sc["beats"] else 0.0
        scene_durs.append(max(nd, typing) + PAD_SEC)

    total = sum(scene_durs)
    print(f"总时长约 {total:.1f}s，合成音轨…")
    full_audio = build_audio(scene_durs)

    fidx = 0
    for si, sc in enumerate(SCENES):
        nf = round(scene_durs[si] * FPS)
        scene_start = fidx
        if is_card(sc):
            for _ in range(nf):
                render(fidx, sc, [], True, sc["narration"]).save(FRAMES / f"{fidx:06d}.png")
                fidx += 1
            continue
        # 每个聊天场景独立累积消息（不跨场景），保证多轮全链路在单场景内完整展示
        acc = []
        for role, text, chips in sc["beats"]:
            acc.append([role, "", chips or {}])
            for k in range(1, len(text) + 1):
                acc[-1][1] = text[:k]
                render(fidx, sc, [tuple(a) for a in acc], False, sc["narration"]).save(FRAMES / f"{fidx:06d}.png")
                fidx += 1
        # 补足本场景剩余帧
        while fidx < scene_start + nf:
            render(fidx, sc, [tuple(a) for a in acc], False, sc["narration"]).save(FRAMES / f"{fidx:06d}.png")
            fidx += 1

    print(f"共渲染 {fidx} 帧，编码 mp4…")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(FRAMES / "%06d.png"),
        "-i", str(full_audio), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(OUT)
    ], capture_output=True)

    print("完成 ->", OUT)
    print("时长(s):", round(dur_of(OUT), 1))
    print("大小(MB):", round(OUT.stat().st_size / 1e6, 2))


if __name__ == "__main__":
    main()
