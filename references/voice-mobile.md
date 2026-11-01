# 讲述感与手机人声方案

用户认可自己的讲述声时，保留声纹、术语读法及真实选中文件。用短问句建立好奇，用正常陈述解释，用转折与结论落重点；停顿给关键动作和术语留空间。不要每句都兴奋、逐字重读或统一加快。`conversational-explainer-v1` 是 Agent 的讲稿/导演约定，不是 TTS 自动情绪能力；新题目的具体音频仍需试听。

## 自动接入

本机已选个人 profile 可设置：

```json
{
  "delivery_style": "conversational-explainer-v1",
  "processing": {
    "tempo": 1.0,
    "pitch_semitones": 0,
    "sentence_ending": "exclamation",
    "denoise": {"preset": "afftdn-hiss-v1"},
    "mastering": {"preset": "speech-mobile-v1"}
  }
}
```

这是个人已选方案的配置片段，不覆盖其他人的声音。新工程照常运行 synthesize.py 和 render_project.py 即可：合成只做一次已选变速/降噪；渲染从原逐句 WAV 按实际 cue 时间组成纯人声，对整段执行一次母带，再按原项目选择混入 BGM。未配置时不改变旧行为。已有工程要显式采用时设置 `"audio_mastering": {"preset": "speech-mobile-v1"}`；设置 null 关闭。先检查音轨是否已经处理，不给已处理的成片再次叠加。

`speech-mobile-v1` 保存本次试听的处理链：75 Hz 高通、250 Hz -1.5dB、2.5 kHz +2dB、2.5:1 适度压缩、loudnorm（I=-15/TP=-2/LRA=5）、末端+1.7dB和限峰0.77。它不再次降噪/变速，保持48k单声道的实际样本数。所有这些人声滤镜在一个处理入口执行一次；启用时替代旧导出 loudnorm，不能先新后旧叠加。混 BGM 后只有总线限幅保护，不再执行人声 EQ/压缩/响度归一化；最终测量只读，不会再次加工声音。实测输出取决于输入，不能把参数 I=-15 当作输出必然正好 -15 LUFS，更不是抖音发布规范。其他声音先试听；发硬、齿音突出、呼吸声变明显就调整或回退。

## Pillow、Remotion 等其他引擎

在最终混 BGM/编码前，将按实际时间混好的**纯人声**交给相同脚本：

```sh
python3 "$SKILL/scripts/master_voice.py" narration.wav narration-mobile.wav
```

输出新 WAV 和 `.mastering.json`；同路径再次运行拒绝覆盖。不要在随后编码时再添加旧 loudnorm 链。需要从逐句文件混音时，可复用 master_voice.py 的 mix_cues(root, actual_cues, duration_s, output)。不要求引擎改成 Manim。

## 验证与反馈范围

渲染的 actual-timeline.json 保存 audio_mastering.file/sha256 及最终 AAC 实测响度。verify_video.py 继续检查原逐句哈希，同时用处理后纯人声作编码/时间对齐参考，保留原0.85相关性、80ms偏移门槛；不因压缩改变波形而调低门槛。搬迁交付目录时同步带上此参考 WAV 与溯源。

测量、解码、样本数与相关性是技术证据；手机/耳机上实际播放才能确认清晰度、术语、句尾与语气。首次新内容用问句、普通解释句、术语与收尾短段结合画面检查；已明确选定的处理方向直接沿用，不每次重选音色。

此预设来源于2026-11-01的约16秒浅色手绘联网开场：用户先分别认可清晰度和约14秒的新讲述，再观看合并demo反馈“好多了”。这只覆盖这些实际文件；不把原7分钟全片或未来句子记为人工听音通过。个人试听与哈希放本机 profile 的 mobile_review，通用 Skill 不包含个人录音或视频。
