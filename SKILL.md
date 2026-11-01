---
name: tech-explainer-video
description: "以导演、视觉和分镜专家的方式制作或修改技术科普视频（AI、软件、网络、数据库、算法、系统架构）：知识核实、导演阐述、分镜与镜头语言、风格与引擎选择（Manim / Remotion / 逐帧绘制等按镜头需求选择）、配音生成、时间轴同步、审片与验收。用户说“做个讲解/科普视频”“把这个原理做成动画”“给视频配音/换声/修读音”时使用。只讨论概念或方法时只讨论，不建工程；用户指定引擎时尊重其选择。"
metadata:
  version: "0.2.11"
---

# 技术科普视频（导演视角）

目标：观众看完能解释一个技术机制；交付可播放的 MP4 和可修改的源文件。以导演、视觉设计和分镜师的标准工作：先决定观众每一秒看哪里、理解什么，再决定画法和工具。专业度来自内容、镜头、构图、节奏和审片，不来自工具名或"渲染成功"。

不为用 Manim 而用 Manim，也不为用 Remotion 而用 Remotion：引擎在分镜之后按镜头需求选择，见 [engine-choice.md](references/engine-choice.md)。本 Skill 的配音/时间轴/校验脚本与引擎无关；Manim 有现成渲染脚本与 starter。

`$SKILL` 指本 Skill 目录；`$PROJECT` 指用户项目子目录；`$PY` 指装有 Manim CE 的解释器（先找已有环境，不擅自安装）。

## 工作流

### 1. 定任务与边界
- 区分：讨论 / 分镜设计 / 制作 / 修改已有视频。只讨论不建工程；制作就推进到成片，并说明剩余阻塞。
- 先读用户材料、已有工程和反馈。只补问会改变内容或成本的缺口：受众、核心问题、时长/画幅、重点、是否配音。已有选择直接沿用。
- 修改已有片先按 [iteration-and-preflight.md](references/iteration-and-preflight.md) 划定受影响 cue、共用组件和产物；保留已选声音/风格，先修局部，不默认从头再做。
- 无限制时建议 60–120 秒、16:9（建议而非规定）。竖屏需重排构图，不能只改像素。
- 用一手资料核实机制；区分教学简化、假设数据与真实事实；箭头不能暗示错误的数据流或所有权。
- 每个视频一个独立子目录，保留旧版本；机器路径、模型权重、凭据不写进模板。

### 2. 导演阐述与分镜 → [directing.md](references/directing.md)、[storytelling.md](references/storytelling.md)
- **开头吸引、正文续看、结尾收获与传播，与分镜同级，属于完整视频的必备设计。** 新制完整片与整体重剪必须按 [观看设计](references/audience-design.md) 写明对应口播、实际画面、cue 和正文兑现位置；缺任一项先补齐，不进入正式整片渲染。
- 先写导演阐述：观众、一句话目标、要打掉的误解、情绪曲线、**高潮镜头**。
- 结构：吸引停留并建立观看期待 → 进入过程 → 展开 → 反转/对比 → 收束。以降低2秒跳出、让目标观众愿意先看3–5秒为开头目标：首屏与最先听到的内容尽快给相关吸引点，前3–5秒用问题/效果和具体观看承诺建立继续看的理由，可跨画面与口播并行融合；不机械逐句排队，不要求2秒内讲完，不以提速或堆信息凑时限。每镜只加一个新理解；术语首次出现必须绑定可见对象。
- 每镜定镜头（全/中/特写、推/拉/跟/固定）、唯一视觉焦点、动效与声音；分镜同时标记引入、兑现、续看衔接、调节或收束传播的观看作用，写成 `storyboard.md` 表格。运镜说不出理由就固定。
- 机制片记录跨镜的初态、触发事件与终态；按受众将缩写、中文名、读法与可见对象对应，回放/历史对照明确另起。
- directing.md 每条规则标了依据等级（规范/研究/惯例/经验）：规范默认遵守；经验值只作起点，以预演为准，不要当标准写进报告。

### 3. 风格与引擎 → [visual-styles.md](references/visual-styles.md)、[engine-choice.md](references/engine-choice.md)
- 用户指定参考片，或反馈风格与表现力不足时，先按 [参考风格迁移与验收](references/reference-style-review.md) 拆解参考并复查分镜；像素风可复用 `assets/pixel-kit/pixel_ui.py` 的组件，不默认沿用原示意图构图。
- 用户要求延续认可的网络协议视频效果时，先读 [样例生产基础](references/reference-production.md)，使用随 Skill 保存的可运行工程、通用绘图组件、样式参数与基准帧；先校准基础，再按新机制重写分镜并做短段效果对照。[案例说明](references/example-wifi-protocols.md) 用于查成片与经验，不能只看封面/链接后凭印象重建。
- 风格从受众和内容推出（扁平示意、卡通对话、贴纸、白板、像素、终端、几何、等距 3D、信息图、隐喻……），全片统一；颜色只表达语义。
- 引擎按分镜中最难的 2–3 个镜头选择：公式/几何变形/算法 → Manim；界面/排版/数据模板/品牌包装 → Remotion；位图角色/贴纸/像素/口型 → 逐帧绘制；可混合，按段输出再合成。选择与理由写进 storyboard.md。
- 未指定风格且没有已选参考时，先给 2–3 个风格候选的**静态样张帧**让用户选。已有认可参考则沿用该选择。
- 开头与正文一起设计：先定问题/效果承诺，指定对应镜头，制作关键动态小样，再扩展全片；成片后根据实际效果精修开头。正文在重要阶段转换安排续看节点，长片必须有多个分散节点；结尾按“回扣开头 → 点明具体收获 → 条件式邀请 → 一个相关行动”收束；先让观众判断内容是否帮到自己，再邀请分享/参与，不能只提出动作。
- 正式动画前做 **animatic**：每镜关键帧 + 实际配音按时间轴拼成粗片，审节奏和镜头顺序，锁定分镜后再做动画（directing.md §4）。
- 在整片高清前，用实际声音预演最拥挤、动态经过文字、镜头推拉和状态更新的片段。修片只重做受影响范围，已有明确选择不重复确认。

### 4. 配音 → [audio-and-review.md](references/audio-and-review.md)、[voice-profiles.md](references/voice-profiles.md)
- 口播分别设计讲述感和手机清晰度：短问句、转折与重点停顿不能只靠提速/感叹号；profile 的 `delivery_style` 用于讲稿与试听，不作为 Base 模型不支持的情绪指令。已选方案及自动接入见 [手机人声方案](references/voice-mobile.md)。
- 声音优先级：本轮用户指定 > 工程 `voice_profile.id` > 本机 `default_profile`。`python3 $SKILL/scripts/voice_profiles.py list` 查看可用声音。
- 生成：`python3 $SKILL/scripts/synthesize.py $PROJECT [--profile ID] [--only CUE...] [--dry-run]`
  - 逐 cue 生成到 `audio/`，缓存键含声音指纹+文本+种子；`locked_sha256` 的 cue 永不重生成；不改 `spoken_text`/字幕。
  - 多角色对话：在 cue 上写 `voice: <profile id>`。读音修复：写 `tts_text`（仅送 TTS），用 `--only` 只重做该句。
  - 可用项目级 `pronunciations` 统一已选术语读法；显式 `tts_text` 优先，不自动把所有大写词拆字母。中断后复用完整原始 WAV，只补缺失生成；见 [iteration-and-preflight.md](references/iteration-and-preflight.md)。
- 本机 profile 配置 `processing.denoise` 时，合成脚本在变速后自动执行已选降噪预设，保留 `.local/tts-raw/` 原始生成音频并输出处理溯源；旧锁定音频不动。手工处理已有 WAV 用 `scripts/process_narration.py`，详见 [voice-profiles.md](references/voice-profiles.md#降噪后处理)。
- profile 的 `processing.mastering` 在新工程合成时写入项目；`render_project.py` 自动对整段纯人声执行一次预设，再混背景声，保存源/处理音轨哈希和最终 AAC 响度。已有工程不自动迁移；可显式设置项目 `audio_mastering`，其他引擎按同一参考接入 `master_voice.py`，不要在后面再套旧响度链。
- 没有已登记声音时，使用用户提供的音频或其他 TTS 产出逐句 WAV；缺音频就明确阻塞，不静默换系统音色。
- 生成 ≠ 听感通过。给用户可点击的音频链接试听；认可后把文件 SHA256 写入 `locked_sha256`。平翘舌/术语读错按 audio-and-review.md 的"中文读音局部修复"处理。

### 5. 时间轴与实现 → [implementation.md](references/implementation.md)
- 使用 Manim 时可复制 `assets/starter`（静音）或 `assets/starter-narrated`（配音+可选 BGM）；其他引擎沿用项目与时间轴接口，不必复制 Manim 构图。按主题重写场景。
- `python3 $SKILL/scripts/build_timeline.py $PROJECT/project.json`：用真实音频时长分配 `max(音频, action_s) + hold_s`；缺音频、哈希不符、重复 id、非法时间都会失败。不按字数估时，不默认变速。
- 使用 Manim 时：Manim CE（不混用 ManimGL API）。用其他引擎时：读取 timeline.json 定位每个 cue，并写出 actual-timeline.json 供校验（见 engine-choice.md）。按语义节点触发动作，镜头移动后留可读保持；静止段冻结帧。字幕层与世界坐标分离，检查字号与遮挡。
- 可选 BGM：project.json 的 `music.file / gain_db / duck`，final 时自动循环、侧链闪避、统一响度。

### 6. 渲染与审片
高清前检查实际字体的容器边距、标签/值相交、运动通道与重要文字的遮挡。渲染器可导出同坐标系几何，交给 `scripts/check_layout.py` 筛查；不能把画布边界检查当作全部无遮挡证明。布局检查与局部修订流程见 [iteration-and-preflight.md](references/iteration-and-preflight.md)。

```sh
python3 $SKILL/scripts/render_project.py $PROJECT --python $PY --mode draft    # 低清动态预演，查节奏
python3 $SKILL/scripts/render_project.py $PROJECT --python $PY --mode stills   # 章末静帧，查布局
python3 $SKILL/scripts/render_project.py $PROJECT --python $PY --mode final    # 1920×1080 成片 + SRT
$PY $SKILL/scripts/verify_video.py $PROJECT/out/final/video.mp4 \
  --timeline $PROJECT/out/final/actual-timeline.json --align-audio \
  --output $PROJECT/out/final/verification.json
```
以上为 Manim 流程；其他引擎用其自身渲染命令，`verify_video.py` 照常使用。`--align-audio` 需要 NumPy，用 `$PY` 运行。
Manim 输入依赖已检查时可给渲染命令加 `--cache` 复用持久 play 缓存；默认完整渲染行为不变。自定义引擎的镜头缓存与任务临时文件隔离见 [iteration-and-preflight.md](references/iteration-and-preflight.md)。
开头、正文续看节点和结尾都必须进入实际配音预演及最终编码片的复查；只写进文案或报告不算落实。按 directing.md 的**导演审片清单**看预演和成片（静音看懂吗、焦点唯一吗、词画同步吗、手机上可读吗、哪些镜头能删），问题按"时间码—问题—修改"列出。静帧不能代替动态预演。

### 7. 验收与交付
分开报告四类证据，不把一类升级成另一类：
1. **知识**：机制、字段语义、简化边界是否正确。
2. **画面**：可读、无遮挡、动作与旁白对应、关键关系有观察时间。
3. **音频**：发音、术语、连续听感、声音一致——只有用户实际听音反馈能支持。
4. **技术**：完整解码、音画对齐、源音频哈希一致（verify_video.py）。

出问题先定位到具体 cue/时间，做最小修复。交付 MP4、scene.py、project.json、timeline、SRT、storyboard 和实际旁白；排除模型、venv、缓存、凭据和个人参考录音。给出本地文件链接。渲染未结束不说完成。

## 修改本 Skill
参照 [evals.md](references/evals.md) 选择相关用例实际运行；报告运行了哪些、结果如何、哪些未验证。结构校验不等于行为评测。
