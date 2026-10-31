# 工程接口与运行

## 最小工程

复制 assets/starter（静音）或 assets/starter-narrated（配音示例）到用户指定的项目子目录，并按主题重写 scene.py、project.json 与分镜。此 starter 是明确的静音演示，不是配音任务的默认成片。环境变量 MANIM_FONT 可指定已安装字体；模板会优先选择可用中文字体。

工程通常包含 scene.py、project.json、storyboard.md、audio/、timeline.json 和 out/。无需模型即可使用已经准备好的逐句音频。

## project.json

全局 fps 是正式帧率；narration 显式表示是否配音。voice_profile 是可选说明信息，不能证明实际声音一致。

使用本机音色注册时，voice_profile 建议记录 id、reference_sha256、profile_fingerprint 和实际条件；本机模型、解释器及个人参考路径放在被排除打包的 `.local/` 配置中。切换 voice_profile 后仍须生成或选取相应音频，重新构建时间轴，不能只改元数据宣称已换声。具体参见 [本机可选音色](voice-profiles.md)。

每个 scene 使用唯一 id、title，以及 lead_s、tail_s 和 cues。每个 cue 使用全局唯一 id：

| 字段 | 含义 |
|---|---|
| spoken_text | 实际口播文本 |
| subtitle | 屏幕字幕；省略时取 spoken_text |
| audio | 配音文件路径，相对 project.json；也可读取用户指定的绝对路径 |
| locked_sha256 | 已认可文件的可选哈希，变更时必须失败 |
| estimated_s | 仅静音草稿使用的计划曝光时长 |
| action_s | 本 cue 从开始到动作完成的预算，包含有意的动作内等待 |
| hold_s | 音频与动作都结束后的观察保持 |
| tts_text | 可选，仅送给 TTS 的读音提示；正文与字幕仍用 spoken_text/subtitle |
| voice | 可选，本 cue 使用的 voice profile id（多角色对话） |
| seed | 可选，生成种子；改变它会产生新的缓存文件 |

顶层可选 `music`：`{"file": "bgm.mp3", "gain_db": -22, "duck": true}`，仅 final 模式混入。

配音由 `scripts/synthesize.py` 生成到 `audio/` 并回写各 cue 的 audio 路径；它不改写锁定 cue、正文或字幕。

顶层可选 `pronunciations` 为术语到 TTS 读法的字面映射；只在 cue 没有显式 `tts_text` 时应用。正式正文不变。成功运行后将使用的默认 seed 固定写回选中的 cue；显式 seed 和锁定 cue 保持。生成中断可复用同缓存键下完整原始 WAV，而不重复调用模型。适用范围与示例见 [iteration-and-preflight.md](iteration-and-preflight.md)。

脚本按帧率向上取整：cue 占用时间 = max(音频实测时长或静音曝光时长, action_s) + hold_s。scene 再加章首 lead_s 与章末 tail_s。这些值来自分镜判断；没有统一最佳值。

build_timeline.py 检查输入后写 timeline.json，不生成或覆盖音频。缺音频、锁定哈希不符、重复 id、负数或非有限时间都会失败。它先完成校验再替换时间轴，失败不会写出一个新的成功时间轴。

## 运行

PYTHON 指用于 Manim 的 Python 解释器，SKILL 指当前 Skill 目录；运行时解析真实位置，不写死到生成工程中。

~~~sh
python3 "$SKILL/scripts/build_timeline.py" /absolute/project/project.json
python3 "$SKILL/scripts/render_project.py" /absolute/project --python "$PYTHON" --mode draft
python3 "$SKILL/scripts/render_project.py" /absolute/project --python "$PYTHON" --mode stills
python3 "$SKILL/scripts/render_project.py" /absolute/project --python "$PYTHON" --mode final
python3 "$SKILL/scripts/verify_video.py" /absolute/project/out/final/video.mp4 \
  --timeline /absolute/project/out/final/actual-timeline.json \
  --output /absolute/project/out/final/verification.json
~~~

draft 是保持目标画幅比例的低清动态视频；stills 只生成最后状态和程序保存的检查点，不是动态预演。final 默认 1920×1080，可通过 --resolution 指定其他画幅。模板构图为 16:9；竖屏或方形需求还需重排镜头和 HUD，不能只改输出像素。

render_project.py 只运行项目自己的 scene.py，不能把不可信代码当作纯数据。它用现有解释器，不安装依赖。每次渲染重新测量时间；模板记录实际 cue 起点，SRT 使用该实际起点。

可选 `--cache` 将原生 Manim play 片段放入项目 `.local/manim-cache/`，按场景类、输出尺寸和帧率分开；保留项目 `manim.cfg` 其他配置。默认不启用缓存。合成临时 MP4 在独立 run 中，正式输出仍完整解码后替换。外部资产/共享组件依赖与最终时间轴仍需复核，不能只据缓存存在宣称通过。

## Scene 的适配约定

模板类名 Explainer，可用 --scene 改为其他类。读取 MANIM_PROJECT、MANIM_OUTPUT、MANIM_STILLS 环境变量。自定义 scene.py 需在输出目录写 actual-timeline.json，包含 narration、fps 和 cues；每条 cue 包含 id、subtitle、start_s（成片绝对秒）、duration_s 和可选 audio / audio_sha256。

模板每个 cue 开始时才加入音频，并记录 self.time；动作完成后验证观察预算，再补齐保持时间。HUD 只随镜头或字幕变化更新，不依赖逐帧检查旁白时间。保持画面时冻结帧，节省渲染时间；等待时按实际输出帧率向上取整，防止 Cairo 截断帧数而缩短观察时间。草稿帧率与正式帧率不同时以实际时间轴生成字幕。

## 成片验证的边界

verify_video.py 完整解码 MP4，检查媒体流、源音频哈希、cue 越界和可选的波形对齐。--align-audio 需要当前解释器有 NumPy，检查每句音频在成片中的实际位置；它验证“用了哪些音频、何时播放”，不识别人是否同声。

验证命令失败时保留错误报告并停止宣称技术验收通过。实际知识、遮挡、动态顺序和听感需另行检查。

打包使用明确文件清单，包含 scene.py、项目/时间轴、SRT、分镜、实际旁白和必要的非私密参考文件。个人音色参考、本机解析配置、模型、venv、缓存、环境变量文件和凭据默认排除；用户明确要求个人参考文件时按其范围交付。不要递归打包整个工作区。
