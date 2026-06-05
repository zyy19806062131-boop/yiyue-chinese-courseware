#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给声调训练器加真人语音（女声 / 男声 / 儿童 三种可选）。

用法：把本文件和 tone_trainer.html 放在同一个文件夹里，然后运行：
    python3 build_voice.py
完成后生成 tone_trainer_voiced.html —— 用 Chrome 打开，三种声音都能切换。

想先看看有哪些中文音色可用，可以运行：
    python3 build_voice.py --list

（脚本会自动安装 edge-tts，需要联网。）
"""

import sys, os, subprocess, base64, asyncio, json

# ---- 确保 edge-tts 已安装 ----
try:
    import edge_tts
except ImportError:
    print("正在安装 edge-tts ……")
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "--quiet"])
    import edge_tts

# ---- 三种音色（key 要和训练器里的 f / m / k 对应）----
# 如果运行时提示某个音色不可用，用 --list 看可选项，把下面对应的名字换掉即可。
VOICES = {
    "f": "zh-CN-XiaoxiaoNeural",   # 女声（自然、温暖）
    "m": "zh-CN-YunyangNeural",    # 男声（稳重、清晰）
    "k": "zh-CN-YunxiaNeural",     # 儿童（童声）
}

RATES = {
    "f": {"n": "+0%", "s": "-40%"},
    "m": {"n": "-12%", "s": "-45%"},
    "k": {"n": "+0%", "s": "-40%"},
}

# ---- 训练器里的所有句子（id 必须和 tone_trainer.html 一致）----
SENTENCES = {
    "cafe-1": "我要一杯咖啡",
    "cafe-2": "我要热的",
    "cafe-3": "来一个蛋糕",
    "cafe-4": "这个多少钱",
    "cafe-5": "还要别的吗",
    "cafe-6": "一共四十五块",
    "cafe-7": "可以用手机支付吗",
    "cafe-8": "扫这里",
    "kids-1": "我喜欢你",
    "kids-2": "这是什么",
    "e1-1": "我是老师",
    "e1-2": "今天天气很好",
    "e2-1": "你周末有空吗",
    "e2-2": "我想去北京旅游",
    "mid-1": "我觉得这部电影很有意思",
    "mid-2": "这个问题不太容易回答",
}

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "tone_trainer.html")
OUTPUT = os.path.join(HERE, "tone_trainer_voiced.html")
TMP = os.path.join(HERE, "_audio_tmp")


async def zh_voices():
    vs = await edge_tts.list_voices()
    return sorted(v["ShortName"] for v in vs if v["ShortName"].startswith("zh-CN"))


async def list_mode():
    print("可用的中文（zh-CN）音色：\n")
    for name in await zh_voices():
        print("  " + name)
    print("\n把上面任意一个名字填到脚本顶部 VOICES 里对应的位置即可。")


async def synth(text, voice, rate, path):
    last_error = None
    for attempt in range(1, 4):
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(path)
            return
        except Exception as exc:
            last_error = exc
            if os.path.exists(path):
                os.remove(path)
            if attempt < 3:
                await asyncio.sleep(attempt)
    raise RuntimeError(f"合成失败：text={text!r}, voice={voice}, rate={rate}") from last_error


def to_data_uri(path):
    raw = open(path, "rb").read()
    return "data:audio/mpeg;base64," + base64.b64encode(raw).decode("ascii")


async def main():
    if not os.path.exists(TEMPLATE):
        print("找不到 tone_trainer.html，请把它和本脚本放在同一个文件夹里。")
        sys.exit(1)

    # 校验三个音色是否可用
    available = set(await zh_voices())
    bad = {k: v for k, v in VOICES.items() if v not in available}
    if bad:
        print("下面这些音色名字不可用：")
        for k, v in bad.items():
            print(f"  [{k}] {v}")
        print("\n可用的中文音色有：")
        for name in sorted(available):
            print("  " + name)
        print("\n请把脚本顶部 VOICES 里不可用的名字换成上面任意一个，再重新运行。")
        sys.exit(1)

    os.makedirs(TMP, exist_ok=True)
    audio = {}
    total = len(SENTENCES) * len(VOICES) * 2
    done = 0
    for sid, text in SENTENCES.items():
        audio[sid] = {}
        for vk, voice in VOICES.items():
            n_path = os.path.join(TMP, f"{sid}_{vk}_n.mp3")
            s_path = os.path.join(TMP, f"{sid}_{vk}_s.mp3")
            await synth(text, voice, RATES[vk]["n"], n_path)    # 正常速
            await synth(text, voice, RATES[vk]["s"], s_path)    # 慢速
            audio[sid][vk] = {"n": to_data_uri(n_path), "s": to_data_uri(s_path)}
            done += 2
        print(f"[{done}/{total}] 已完成：{text}")

    audio_js = json.dumps(audio, ensure_ascii=False)
    html = open(TEMPLATE, encoding="utf-8").read()
    if "/*__AUDIO_DATA__*/ {}" not in html:
        print("模板里没找到音频占位符，请确认用的是最新版 tone_trainer.html。")
        sys.exit(1)
    html = html.replace("/*__AUDIO_DATA__*/ {}", audio_js)
    open(OUTPUT, "w", encoding="utf-8").write(html)

    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    os.rmdir(TMP)

    print("\n✅ 完成！生成文件：tone_trainer_voiced.html")
    print("   用 Chrome 打开，右上播放区可切换 女声 / 男声 / 儿童。")


if __name__ == "__main__":
    if "--list" in sys.argv:
        asyncio.run(list_mode())
    else:
        asyncio.run(main())
