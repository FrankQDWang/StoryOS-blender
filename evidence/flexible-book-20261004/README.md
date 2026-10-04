# 柔软皮面本自检证据

本轮基线检查点为本地提交2e48105（用户要求保存的材质改善），加载比较基线另固定为eedd745生产构建。所有浏览器检查使用隔离无头Chrome，未控制用户浏览器。

- `baseline/`：preview.2在同视口的正侧面关键帧。
- `pass-1`–`pass-4/`：中间稿，保留发现的书芯缺面、穿皮等问题，不作为最终结果。
- `final/`：五款闭合/打开、三个书位接触、全景、正常36帧/慢放94帧与实际入口冒烟。`first-closed-before-ready.jpg`明确为首轮过早截到加载中的废片；正式`book-1-closed.jpg`已按scene-ready重采。`handoff-captures.json`记录最终截图错误0。
- `final/opening.mp4`：实际正常播放截图依原捕获时间间隔编码，末帧加1秒停留；不是均匀采样的完整录屏。原图/时点位于`final/normal/`。
- `performance/`：最终生产构建与eedd745的24个冷/暖样本（本机与20Mbps/50ms，各3配对）；12项中位数比较全部在+10%内，错误0。脚本`tools/book-check/flexible-benchmark.mjs`。
- `geometry-check.json`：最终中心线长度和纸页/封皮间距诊断；只证明曲面约束，不代替视觉评审。
- `build-identity.json`：最终源文件与生产JS的SHA、manifest/public产物一致性、保持不变的房间/手部/纹理资产。

16项测试与构建通过。冒烟仅在首次返回后点击过早失败，修正测试等待当前Canvas绘制后单独复跑并通过；未强制点击。视觉判断见项目`design-qa.md`和第26轮记录，用户尚未认可本轮效果。
