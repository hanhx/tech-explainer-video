# DeepInfer：明亮纸张风格与多轮修片参考

适用于沿用本次效果、修复同类声音/节奏问题，以及评测Skill是否尊重最新用户选择。用于学习制作方法与复现画面，不是“所有画面与整片听感已获用户通过”的标杆。

## 参考材料与复现

- `assets/examples/deepinfer-paper-v10/project/`：27 cue的正式口播、时间轴、可编辑Pillow/FFmpeg renderer、字体选择和曲线图标生成代码。使用当前director_v10.py，不依赖原个人工作目录。
- `goldens/`：8幅1920×1080基准帧及哈希，覆盖开箱、CPU/GPU时间重排、KV传输中/到达后、章节滑动中、索引特写、运行块释放与结尾。
- `case.json`：本例范围与用户实际反馈。`media-manifest.json`记录可选本地媒体哈希。
- 本机收录的[成片](../assets/examples/deepinfer-paper-v10/media/video.mp4)和[章节滑动短段](../assets/examples/deepinfer-paper-v10/media/sliding-demo.mp4)不随Git分发；本例27段WAV，保留在project/audio/供本地有声复现。个人参考录音、模型和声音注册配置未收录。

在可写工作目录克隆，校准不需音频或模型：

```sh
python3 "$SKILL/scripts/reference_project.py" clone "$WORK/deepinfer-reference" --case deepinfer-paper-v10
python3 "$SKILL/scripts/reference_project.py" check "$WORK/deepinfer-reference" --case deepinfer-paper-v10 --python "$PY"
```

本例默认使用本机可用的苹方SC，旧绘图基础还使用macOS黑体。无相同字体的环境可设置EXPLAINER_FONT指向可用中文字体；实际像素会变化，不能把字体差异当作已校准。没有附带字体文件或授权字体的再分发。

有Pillow和FFmpeg时，无音频也能输出实际时间的静音预演：

```sh
cd "$WORK/deepinfer-reference"
"$PY" preview.py --cue capacity-question --seconds 2
"$PY" rebuild.py --mode stills
```

静音预演只检查画面。完整有声重建需恢复manifest中全部27个精确WAV；Git版会明确列出缺失，不生成测试音、静默换声或下载TTS。音频齐全后：

```sh
"$PY" rebuild.py --mode final
"$PY" runtime/scripts/verify_video.py out/final/video.mp4 --timeline out/final/actual-timeline.json --align-audio --output out/final/verification.json
```

通用脚本默认仍为wifi-protocols-v6；不要求现有使用者更换命令。新题目不能仅换标题：重写机制与分镜，重新核实知识、字幕时点和状态。

## 可迁移的方法与本例选择

|反馈/问题|本片采用的处理|迁移边界|
|---|---|---|
|画面简陋、灰暗，后来偏写实|保留扁平纸张设备、浅明背景与语义色；统一轮廓、阴影和留白|不要求其他题目都用纸张、芯片或本配色|
|字体与结尾图标不好看|苹方SC统一字重；圆角曲线原生图标、统一线宽与视觉重量|字体和图标尺寸取决于目标平台与设计坐标，不照抄像素|
|六章同排太挤，又不希望丢章节|完整六章轨道，3项可见，当前章高亮，必要时0.75秒自动滑动|导航可选；3项和0.75秒是本次选择。MP4不支持手势滑动|
|语音提速后画面也快|从源录音按目标有效倍率处理声音；动作时长、语义事件和观察保持单独安排|本例原0.92×1.5等效1.38，不是所有声音默认倍率|
|持续沙沙声，后来声音空灵且小|定位旧处理链，从同一批原始take更轻清理，完整纯人声只做一次母带；保留A/B范围|案例DSP只保存在project/runtime，不覆盖通用预设和本机profile|
|“请求排长队”前像缺词|完整前后句核对；实际前句“先拆开一台机器”，去掉异常头部空白并缩短交接hold|RMS与ASR仅筛查，不能证明发音或作为自动切音依据|
|机制镜头像幻灯片、跨镜重置|同一GPU重排交接，状态到达才出现，展开HBM保留已有内容，释放A时其他请求不消失|新题目另写初态/触发/到达/终态；教学编号不是性能数据|
|结尾不自然，用户不要分享|上一技术图完成结论，邀请时再退出，精修图标与谢谢大家收束|正式结尾按用户原句，不能强加单一行动/分享模板|

本例结尾原句：“如果这段动画让你有所收获，欢迎点赞收藏加关注，谢谢大家。”CPU读法采用用户此前认可的原take。不要把本例“DeepInfer”或“少”的TTS提示变成跨项目同音字替换；先用自然上下文试听，正式文字保持规范。

## 证据与未验证项

原交付V10约215.2秒，1080p/30fps。技术报告记录27段音源哈希、母带哈希与波形对齐通过，AAC实测约-13.99LUFS、-1.37dBTP；这些是该文件的统计，不是通用平台标准。

用户明确反馈“B 更自然，音量合适”覆盖18.733秒试听（saving-promise、opening、roles）；CPU读法与衔接有此前局部反馈。整片尚无新的用户连续听看验收，无留存提升数据。几何筛查与编码片采样复核也不能替代这些反馈。

本例技术内容固定于DeepInfer提交5537415的静态源码/官方文档，证据在project/knowledge-evidence.json；没有运行部署或性能跑分，外围长期缓存及生产Decode的边界仍要显示。将来把其技术论断写入新视频时重新核实，不从标题推断政治影响、厂商反应或实际收益。
