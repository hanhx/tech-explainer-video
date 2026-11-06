---
name: tech-explainer-video
description: "以导演、视觉和分镜专家的方式制作或修改技术科普视频（AI、软件、网络、数据库、算法、系统架构）：知识核实、导演阐述、分镜与镜头语言、风格与引擎选择（Manim / Remotion / 逐帧绘制等按镜头需求选择）、配音生成、时间轴同步、审片与验收。用户说“做个讲解/科普视频”“把这个原理做成动画”“给视频配音/换声/修读音”时使用。只讨论概念或方法时只讨论，不建工程；用户指定引擎时尊重其选择。"
metadata:
  version: "0.3.1"
---

# 技术科普视频（导演视角）

目标：观众看完能解释一个技术机制，而且愿意看完。**用画面讲解，不用文字讲解**：旁白解释，画面展示变化，屏上文字只负责命名。制作任务交付可播放 MP4 与可修改源文件；只讨论概念或方法时只讨论。

`$SKILL` 为本目录，`$PROJECT` 为独立项目目录，`$PY` 为已有的引擎/Pillow/NumPy 环境。按需读取参考，不擅自安装环境。修改已有片、缓存、证据与交付的纪律见 [production-discipline.md](references/production-discipline.md)。

## 1. 任务

- 先读用户材料、已有工程和最新反馈；只补问会改变受众、核心问题、画幅、配音或成本的缺口。已有选择直接沿用，用户指定引擎时尊重。
- 一手资料核实机制；先提取核心主张、成立条件、证据与开放问题，再写故事。架构探索、内部实例、模拟实验和正式产品分别说明。
- 时长由理解目标、实际声音与分镜决定，不为凑 5 分钟删掉必要的桥接或整体倍速；试片可取最难的 60–120 秒。画幅无约束可建议 16:9。
- 先确定改动对象与单位：“5–7”可能是章节数、分钟数或标题字数，结合上下文判断；仍有会影响产物的歧义才问。封面/发布文案/章节整理按 [publishing.md](references/publishing.md) 做，不重剪视频。

## 2. 讲通：导演阐述与故事

按 [storytelling.md](references/storytelling.md) 与 [audience-design.md](references/audience-design.md) 写导演阐述：

- 受众已有经验、看完能解释的问题、要打掉的误解。
- **高潮镜头**：让观众恍然的那个画面变化。先找到它，其余镜头为它铺垫。
- 用受众真实熟悉的任务起步，同一案例贯穿全片；不为套比喻换成陌生业务。客观叙事或第一人称服从用户选择。
- 因果链：谁在什么条件下做什么 → 状态怎样变 → 哪项工作被复用/减少/重排 → 为什么影响目标。
- 用“当前瓶颈 → 最短充分解法 → 解法带来的下一问题”递进，不按术语目录报菜名，也不把所有章节硬串成同一原因。问句后及时接简短答案，再演示机制。
- 开头 3–5 秒给出问题或效果；阶段之间兑现收获并引出下一问；结尾回扣开头，落到人的工作怎样改变。已选结尾与互动原句保留。

## 3. 设计画面（本 Skill 的核心）

读 [visual-craft.md](references/visual-craft.md)，分镜时逐镜落实：

0. **定机制类型**：按 [mechanism-patterns.md](references/mechanism-patterns.md) 判断属于哪一类（容量、按需加载、缓存、并行、协议、查找、分层、权衡），套用该类的镜头骨架与高潮；导演阐述写明类型。
1. **对标**：选 1 个对标作品/方向，写明借用的文字量、变化频率、造型配色。
2. **视觉事件**：每镜写出一个不读字也能感知的变化（流动、累积、复用、对比、规模反差、变形、冲突）。写不出来的镜头要么并入相邻镜，要么重想画法。
3. **文字预算**：字幕 1 层 + 可选短标题（≤12 字）+ 贴身对象标签；不加副标题、横幅、图注；章节导航与页码默认关闭。
4. **运镜与转场**：对象真正执行读取、传递、等待等操作；保留身份与去向。整页缩放不能代替机制，运动连续性按 [motion-and-sound.md](references/motion-and-sound.md) 检查。
5. **节奏**：每镜标快/中/慢，高潮前留白、高潮放慢；避免连续同档。
6. **声音**：默认低音量背景音乐；按可见动作配置克制的状态音、运动音和拟音（用户不要时关闭）。移动、点击、表盘分别设计，不只在片头片尾加叮声，也不铺连续沙沙声。

分镜表格式、镜头语言、构图、字幕、动效规范见 [directing.md](references/directing.md)；风格与引擎见 [visual-styles.md](references/visual-styles.md)、[engine-choice.md](references/engine-choice.md)。无既选风格的新片给 2–3 张静态样张让用户选。

## 4. 配音

- 声音优先级：本轮指定 > 工程 `voice_profile.id` > 本机默认。`scripts/voice_profiles.py list` 查登记声音；没有声音时做静音预演并说明缺口，不静默换系统音色。
- 讲稿先读顺：主语明确、问答相接、意群完整，不强制“你/我们”。术语读法写在 `tts_text`/`pronunciations`；英文词连同前后整句试听，避免孤立拼词、拖尾与重复起音。
- `python3 "$SKILL/scripts/synthesize.py" "$PROJECT" [--profile ID] [--only CUE...] [--dry-run]`
- 音质问题见 [audio-repair.md](references/audio-repair.md)、[audio-and-review.md](references/audio-and-review.md)、[voice-profiles.md](references/voice-profiles.md)、[voice-mobile.md](references/voice-mobile.md)。

## 5. 实现与预演

- 时间轴来自真实 WAV：`python3 "$SKILL/scripts/build_timeline.py" "$PROJECT/project.json"`。
- 先做 animatic（关键状态 + 实际配音），再做最难因果链与最拥挤镜头的动态预演，最后整片。
- **引擎**：先找已有环境（如 `~/.venvs/manim/bin/python` 装有 Manim 0.22.0、Pillow、NumPy，可同时作 `$PY`），不擅自安装。本机有 Manim 时可用 `assets/starter`/`starter-narrated` + `render_project.py`；没有 Manim 或需要位图/逐帧效果时，用 Pillow 引擎：项目里只写 `scenes.py`（每个 scene 一个 `draw_<id>(ctx)`），运行 `"$PY" "$SKILL/scripts/pillow_engine.py" "$PROJECT" [--draft|--still 秒…|--only SCENE]`。绘制优先用 `scripts/pillow_kit.py` 组件（`container` `fill_up` `fly` `morph` `scan` `ring` `bars` `stamp` `gear` `pill` 等），不从零写坐标动画。范例见 [example-agent-disclosure.md](references/example-agent-disclosure.md)。
- **按词触发**：动作写成 `ctx.at('说到的词')`。Pillow 引擎依据实际 WAV 的停顿和字数估计词时点，并非强制词级对齐；关键动作需回听校准。无 WAV 时只是临时时长估计。声音绑定动作的起步、落点、按下或刻度事件，不把所有音效挂在句首；可用 `scripts/action_sounds.py` 的可复现音色。
- 动作后留可读保持；输出 `actual-timeline.json`。

## 6. 审片

先做观众视角，再做技术检查：

1. **去文字测试**：隐藏字幕和说明文字、静音观看，能看出谁在动、什么变了吗？
2. **接触表**：`"$PY" "$SKILL/scripts/contact_sheet.py" VIDEO --timeline actual-timeline.json --output contact.png --at-events`，每镜取关键动作刚发生后的帧（无事件时取 10%/50%/90%）；用 Read 实际看图，记录焦点、文字字数、视觉事件、机位重复。
3. **零上下文复述**：把接触表交给无上下文子代理，用 [visual-craft.md](references/visual-craft.md) §9 的固定提问；“只看画面”判为不懂的镜头优先改画面。
4. **关卡**：把复述结果写进 `$PROJECT/review.json`，运行 `python3 "$SKILL/scripts/review_gate.py" "$PROJECT"`。有“不懂”的镜头、缺判断、或接触表比源码旧时会拦下；**通过前不渲染正式整片**。修画面后重新出 draft、接触表、复述。仅混音且视频压缩流验证一致时，沿用对应画面证据，补做声音与同步检查。
5. 按 [directing.md](references/directing.md) §12 清单逐项过。
6. **动态与声音**：检查最终编码片的连续播放和转场前/中/后密集帧；接触表不证明丝滑。试听包含前后句的动作密集段、英文术语段、结尾；有左右耳异常反馈时检查最终解码的左右通道，不能只看“单/双声道”标签。细则见 [motion-and-sound.md](references/motion-and-sound.md)、[audio-repair.md](references/audio-repair.md)。
7. 技术检查（以下为 Manim 入口；Pillow 等沿用实际引擎输出路径，不为检查另换引擎）：

```sh
python3 "$SKILL/scripts/render_project.py" "$PROJECT" --python "$PY" --mode draft
python3 "$SKILL/scripts/render_project.py" "$PROJECT" --python "$PY" --mode final
"$PY" "$SKILL/scripts/verify_video.py" "$PROJECT/out/final/video.mp4" \
  --timeline "$PROJECT/out/final/actual-timeline.json" --align-audio \
  --output "$PROJECT/out/final/verification.json"
```

记录“时间码—问题—修改”。只有用户或真实观众能说“看懂了”。

## 7. 交付

MP4、源文件、project/timeline、SRT、分镜和旁白的本地链接；细则见 [production-discipline.md](references/production-discipline.md)。

## 修改本 Skill

按 [evals.md](references/evals.md) 选相关场景。除复现检查外，至少用一个**未见过的新主题**做短样片，报告去文字测试、接触表与复述测试结果。
