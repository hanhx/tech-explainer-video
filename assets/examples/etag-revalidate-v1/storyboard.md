# 刷新网页，为什么有时不用重下？

给知道浏览器和服务器分别是什么、没听过条件请求的观众。看完能复述，同一个刷新动作为什么一次沿用本地页面，另一次拿到新页面。类型是协议与缓存。高潮是同一条返回路径先只飞过一个小回执，后来飞回一张完整网页。

视觉参考是像素游戏里的物品交换。借用轮廓清楚的物件、明确方向和落点反馈。左右一直是同一个浏览器和服务器，网页画成可辨认的像素景色，颜色和形状一起换。标题和标签只做定位，浏览器什么时候能换页面由实际到达的物件决定。

| 时段 | 提问与答案 | 同一个场景里的动作 |
| --- | --- | --- |
| 00:00–00:04 | 刷新网页，一定要重下吗？ | 先看到两端持有同一份蓝色页面。鼠标点刷新，浏览器端的标签随请求出发，整页留下。 |
| 00:04–00:09 | 服务器怎么知道浏览器存的是哪份？浏览器带上本地副本的 ETag。 | 原标签留在页面旁，它的副本沿上轨到达，与服务器当前标签并列比较，出现对勾。 |
| 00:09–00:15 | 标签对上会怎样？服务器回 304，浏览器沿用本地那份。 | 小回执从右往左走。到达后描亮左边原页面，留时间看清内容保持不变。 |
| 00:15–00:27 | 服务器换了页面怎么办？浏览器仍拿旧标签来比，这次拿到新正文。 | 服务器先换成橙色新页面，浏览器仍是蓝色。第二次点击后标签比较出现叉号，新页面跨屏，到达后左侧才改变。 |

适用场景是已有缓存副本，且请求发到了源服务器做条件 GET。小回执表示无正文的 304 响应，仍可携带响应头。标签不同的一幕假设 GET 正常成功，因此回 200 和新正文。“a”“b”是示意的实体标签值。相关规则见 [RFC 9110 §13.1.2](https://www.rfc-editor.org/rfc/rfc9110.html#name-if-none-match) 和 [§15.4.5](https://www.rfc-editor.org/rfc/rfc9110.html#name-304-not-modified)。

封面和首句可以都用“刷新网页，为什么有时不用重下？”304 是其中一个答案，主画面可以把两次回程并列。样例覆盖 ETag 条件校验，封面主题保持这个范围。

背景调用 `pillow_kit.moving_grid` 的平面配置。新主题可保留背景和同场景重演的骨架，按主题更换对象、可见条件与结果。

## 运行

用现成的 Pillow、NumPy、中文字体和 FFmpeg 环境。建议把样例复制到独立工作目录后再渲染。以仓库根目录为当前目录，设置 `PROJECT` 和 `PY` 后执行：

```sh
"$PY" scripts/pillow_engine.py "$PROJECT" --draft
"$PY" scripts/contact_sheet.py "$PROJECT/out/draft.mp4" \
  --timeline "$PROJECT/out/actual-timeline.json" \
  --output "$PROJECT/out/contact.png" --at-events
```

当前时间轴是这份无旁白样例的锁定时轴。若从 `project.json` 重建，按新分镜复查动作时点，再填入接触表的 `review_times_s`。去文字预演时保存正常版草稿，再运行下列命令。开关移除画面标签，并在调用引擎时关闭字幕，最后只导出画面流。

```sh
ETAG_HIDE_COPY=1 PYTHONPATH=scripts "$PY" - "$PROJECT" <<'PY'
import sys
from pillow_engine import Engine
engine = Engine(sys.argv[1])
engine.subtitle = lambda image, time: image
engine.render(draft=True)
PY
ffmpeg -y -i "$PROJECT/out/draft.mp4" -map 0:v -c copy "$PROJECT/out/textless.mp4"
```

按 Skill 的复述关卡审完，再用同一引擎去掉 `--draft` 生成正式样片。正常版有字幕和动作音效，录音和配乐均留空。
