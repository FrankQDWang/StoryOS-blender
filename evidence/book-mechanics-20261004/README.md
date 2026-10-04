# 软皮本力学与无字内页修复证据

- 最终画面：`final/five-books.jpg`、`final/overview.jpg`，五款闭合/打开、第一/三/五位接触。
- 连续自检：`final/normal/`（35帧）与`final/slow/`（95帧），均为实际播放捕获，时点在各自`frames.json`。
- 可播放影片：`final/opening.mp4`来自最终版本的Chrome正常速度录制；`final/recording/raw.webm`与`metadata.json`保留原片/起播时点。MP4起点为原片2.153秒，保留4.7秒；抽查图为`clip-start.jpg`、`clip-end.jpg`。不是静帧合成动画。
- 主路径：`final/acceptance.json`，空库创建、正常开书/返回、减少动态、删除刷新，错误0。
- 数值与来源：`bake.json`、`verification.json`；`sampling-equivalence.json`记录采样缓存优化前后309,276点，最大坐标/切线差4.22e-15。
- 最终加载对照：`performance/`，固定eedd745生产基线、同机独立Chrome154、1512×751/DPR1，每组3配对样本；包含本机及20Mbps/50ms、冷暖缓存、首屏/首次手部绘制/进入工作区。
- 历史试跑：`pre-cache-key-performance/`未完成；`before-sampling-cache-performance/`和`before-focus-preparation-performance/`未过首开10%门槛。均不当作最终通过记录。
- `rejected-cloth-pass/`、`strip-pass/`、`contact-pass/`、`refined-pass/`、`candidate/`为中间排错画面，包含已修正的折回/分层/挡书条穿纸，不能代替`final/`。

本轮的最终助手判断和实现范围见`design/iterations/27-book-mechanics-and-blank-pages.md`、`design-qa.md`和PLAN当前交接；用户尚未评价本轮视觉。
