# tech-explainer-video

用于制作和修改中文技术科普视频的 Codex Skill。覆盖知识核实、导演阐述、分镜、视觉风格、引擎选择、配音同步和审片，交付可播放视频与可编辑源文件。

按镜头需求选择 Manim、Remotion 或逐帧绘制等工具。也可以只讨论选题、原理或分镜，不必创建视频工程。

## 安装与调用

将本仓库放在稳定的本地目录，然后建立软链接。把下面的仓库路径替换为自己的实际路径；目标位置已有内容时，先保留原目录。

```sh
mkdir -p ~/.codex/skills
ln -s /absolute/path/to/tech-explainer-video ~/.codex/skills/tech-explainer-video
```

调用示例：

```text
使用 $tech-explainer-video，把 DNS 缓存原理做成中文动画。
先设计导演阐述与分镜，按镜头需求选择引擎，再制作实际配音预演和成片。
```

如果技能列表仍显示旧内容，在客户端重新加载后查看。

## 内容与运行环境

- `SKILL.md`：制作与修改工作流。
- `references/`：导演、镜头、风格、配音、局部修订和验收说明。
- `scripts/`：音色解析、逐句合成、时间轴、布局筛查、渲染和媒体校验。
- `assets/`：静音与配音 Manim starter、像素绘图组件和示例音色配置。

阅读和使用 Skill 不要求预先安装所有引擎。实际制作时，按选定工具准备依赖；Manim starter 的依赖列在其 `requirements.txt`。媒体处理需要 FFmpeg/ffprobe，波形对齐检查还需要 NumPy。其他引擎的项目需要自行准备对应环境。

## 配音与个人音色

仓库不包含个人参考录音、模型权重或本机音色配置。没有个人音色时，可以制作分镜和静音动画，也可以提供自己生成的 WAV 或真人录音，继续进行时间轴与合成。

随附自动合成脚本使用已登记的本地 Qwen3-TTS Base 环境。需要自动生成配音时，参考 [`references/voice-profiles.md`](references/voice-profiles.md)，用 [`assets/voices.example.json`](assets/voices.example.json) 准备本机配置，填写自己的解释器、模型、参考录音、录音转写和真实 SHA256。示例中的占位符不能直接运行。

为兼容已有安装，默认注册文件位置和环境变量名称继续保留：

```text
~/.config/manim-tech-explainer-video/voices.json
MANIM_VOICE_CONFIG
```

也可以用 `--config` 指向其他本机注册文件。修改 Skill 名称不会移动或修改现有个人录音与音色配置。

## 复用与验收

修改已有视频时，先确定受影响镜头和声音，复用不受影响的实际文件；术语读法、动态遮挡和跨镜状态应在整片高清前通过局部实际配音预演检查。

完整解码、哈希、波形对齐与布局筛查分别提供技术证据，不能代替主观听音或观众理解。实际评测范围见 [`references/evals.md`](references/evals.md)。

本次DeepInfer参考提供可克隆的明亮纸张风格工程、三项可见滑动导航、原生曲线图标及声音/节奏修复案例，见 [`references/example-deepinfer.md`](references/example-deepinfer.md)。仓库不分发该片声音/视频；无配音也能校准真实画面和输出静音动态预演。
