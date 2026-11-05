# 参考案例：Agent 渐进式披露（0.3.0 推荐）

`assets/examples/agent-disclosure-v1/`：83 秒、8 镜、16:9，用 0.3.0 规则从零制作，Pillow 引擎。只收源码与接触表，不含配音与视频。

## 值得借的方法

- **开头先给灾难结果再倒放**：第 1 帧就是溢出的窗口，1 秒内倒回，再讲过程。
- **一个对象贯穿全片**：100 本说明书 → 溢出 → 缩成 100 条简介 → 其中一条展开成正文 → 对比柱中的三层 → 变形成书的目录/章节/附录。
- **先单个特写，再推广到全部**：第 3 镜先让一本书慢慢压成一行简介，再让 100 本一起压。
- **文字预算**：除字幕外每屏只有对象标签；收尾用一张卡片给出可执行的建议。
- **按词触发**：所有动作写成 `ctx.at('一股脑')` 这类短语，换配音后自动对齐。
- **字幕分段**：长旁白用 `subtitle_parts` 按短语切换字幕。

## 复述测试记录

- 第 4 轮：第 5 镜“不懂”，`review_gate.py` 拦下。原因是一镜三件事（用到的文件、用不到的文件、脚本只回结果）。
- 修法：拆成 `files`（两份文件只读一份）和 `script`（代码被挡在窗外，只送回结果）两镜，各重录一句旁白，不是加字。
- 第 5 轮：没有“不懂”，关卡通过；第 7 镜“懂”，其余“半懂”。“半懂”多数指向标签字号，是接触表缩小所致，以全尺寸为准。
- 用户尚未完成整片听看验收。

## 复现

```sh
cp -r "$SKILL/assets/examples/agent-disclosure-v1" "$PROJECT"
python3 "$SKILL/scripts/synthesize.py" "$PROJECT"          # 需本机声音配置
python3 "$SKILL/scripts/build_timeline.py" "$PROJECT/project.json"
"$PY" "$SKILL/scripts/pillow_engine.py" "$PROJECT" --draft
```
