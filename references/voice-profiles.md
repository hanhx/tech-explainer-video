# 本机可选音色

这是配音任务的可选注册层，不是通用 Skill 的内置声音。个人录音、试听和机器路径留在本机；未配置的机器仍可用用户提供的音频或其他后端，不自动下载模型、克隆声音或切换系统音色。

## 选择与沿用

1. 运行 `python3 "$SKILL/scripts/voice_profiles.py" list` 查看本机已注册的名称。
2. 优先采用本轮用户明确指定的声音；其次沿用当前工程的 `voice_profile.id`；新工程才采用本机 `default_profile`。用户说“候选音色”时读取本机 `candidate_profile`；多个候选且无映射时再补问。
3. 使用 `resolve <id>` 验证参考哈希、文字和本地 Base 模型。需要本机运行参数时可加 `--output "$PROJECT/.local/voice-profile.json"`。这个解析文件包含本机路径，不能打进源码包。
4. 在工程中记录 `voice_profile.id`、`reference_sha256`、`profile_fingerprint` 与实际采用的生成/后处理条件。这些记录不能替代音频本身的哈希和听感验收。

切换名称只改变后续生成条件，不会把已存在的音频变成新音色。保留已认可的录音，在新目录生成所选声音的片段，重测字幕与动画时间；不改写已有锁定哈希以掩盖覆盖。不重复询问已明确的音色选择。

本机常用名称可使用 `my-voice-lively`（个人明快版）和 `ono-anna`（固定参考的候选音色）。它们是否可用、哪个默认，以本机注册文件为准；不要把某个用户的选择变成其他机器的默认。

## 注册文件

默认位置是 `$XDG_CONFIG_HOME/manim-tech-explainer-video/voices.json`；未设置 XDG_CONFIG_HOME 时为 `~/.config/manim-tech-explainer-video/voices.json`。也可用 `MANIM_VOICE_CONFIG` 或命令行 `--config` 指定。注册文件的基本形状：

~~~json
{
  "schema_version": 1,
  "default_profile": "my-voice-lively",
  "candidate_profile": "ono-anna",
  "runtime": {
    "python": "/absolute/local/tts-venv/bin/python",
    "model_id": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "model_path": "/absolute/local/base-model",
    "device": "auto",
    "attn_implementation": "sdpa"
  },
  "profiles": {
    "my-voice-lively": {
      "label": "我的声音 · 明快版",
      "backend": "qwen3-tts-base",
      "reference_audio": "~/.local/share/manim-tech-explainer-video/voices/my-voice/reference.wav",
      "reference_sha256": "sha256-of-the-selected-reference-file",
      "reference_text": "与录音严格对应的文字",
      "generation": {"language": "Chinese", "non_streaming_mode": true, "max_new_tokens": 384},
      "processing": {"tempo": 1.06, "pitch_semitones": 0, "sentence_ending": "exclamation"}
    }
  }
}
~~~

注册文件里的机器路径是本机配置，不能复制进通用模板。个人参考素材可放在 `~/.local/share/manim-tech-explainer-video/voices/` 或用户指定的稳定位置；不要依赖聊天附件临时目录。注册新个人声音时由用户提供参考与对应文字，不自行获取其他人的录音。

## 生成条件

两种已注册声音都可采用 Qwen Base 的固定参考方式：

~~~python
profile = resolved_profile
prompt = model.create_voice_clone_prompt(
    ref_audio=profile["reference_audio"],
    ref_text=profile["reference_text"],
    x_vector_only_mode=False,
)
# 同一轮全部句子复用这个 prompt。
wavs, sr = model.generate_voice_clone(
    text=spoken_text, voice_clone_prompt=prompt, **profile["generation"]
)
~~~

`processing.sentence_ending=exclamation` 表示把该句结束的句号换成感叹号来尝试引导韵律，不添加“开心地说”等会被读出的指令；屏幕字幕可保留原来的标点。`processing.tempo` 只在用户认可的音色方案中显式采用，处理后重新实测时长，不能再叠加一次相同提速。`pitch_semitones=0` 表示不变调。

Base 不支持 CustomVoice 的 `speaker` / `instruct` 方式。候选名称为 Ono_Anna 时，注册层仍可使用用户选中的 Ono_Anna 录音作为 Base 的固定参考；不要悄悄退回逐句独立 CustomVoice 生成。参考一致能固定条件，不能保证听感必然一致。

缓存键包含 profile_fingerprint、实际口播文本、随机种子及其他生成参数。项目记录声音来源；用户认可的具体片段仍用 locked_sha256 锁定并直接复用。已有批准文件的正文不因标点策略被静默修改或重新生成。

新视频至少复查术语、数字与连续句子的听感；以前认可的短片段不等于未来整片人工听音通过。个人录音、参考特征、本机配置、模型和缓存默认不进入可分享源码包，渲染包只需实际采用的逐句旁白；用户明确要求这些参考文件时按其范围交付。


## 降噪后处理

支持可选的 `processing.denoise: {"preset": "afftdn-hiss-v1"}`。仅对在本机注册文件里显式启用的 profile 生效，不改变其他声音。用户选择的参考音色、节奏和读音策略继续沿用。

预设来自 2026-10-30 的低微沙沙声修复试听：用户对约 26 秒的开场与核心网段落 B 反馈“好多了”，并要求后续复用。其滤镜为 `afftdn=nr=8:nf=-42:tn=0:gs=8`，48 kHz 单声道，预补 0.1 秒尾音、去除滤镜引入的 1200 样本（25 ms）延迟，截取原时长。试听人声与 A 配平；新句处理按整句 RMS 配平并限制峰值，具体增益按句计算，不照搬试听的增益数值。FFmpeg 版本改变时用短脉冲/真实句子复核延迟，不能默认所有滤镜都延迟 25 ms。

`synthesize.py` 顺序为：生成并保留原始 WAV → 仅一次已选 tempo → 降噪 → 按实际新 WAV 建时间轴。后处理条件进入 profile 指纹和缓存键，处理失败的半成品不能当成功缓存；已锁定句子始终直接复用。输出 WAV 邻近的 `.processing.json` 记录原始/处理前/输出哈希、参数、增益和工具版本。不要把新处理条件的 fingerprint 追填给未处理的旧 WAV。

手动处理**已变速**的已有句子时：

```sh
python3 "$SKILL/scripts/process_narration.py" source.wav clean-variant.wav
```

它不再变速，不覆盖源文件或已存在的输出。新生成原始文件在项目 `.local/tts-raw/` 中保留，分享包仍只含实际逐句成片旁白；个人参考录音和试听基准留在本机。个人基准文件及其 SHA256/反馈范围可记录于本机 profile 的 `denoise_review`，不写进通用 Skill。

这次认可覆盖上述 B 试听的降噪方向，不代表未来新句或整片人工听音通过。新片继续检查清晰度、齿音、收尾和连续听感；如果变闷或产生水声，保留原句并局部调整，不把参数成功执行当成音质通过。
