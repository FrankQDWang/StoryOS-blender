# 封皮受力方向与手稿补齐

2026-10-04，0.1.5-preview.5。限定范围见`design/iterations/28-cover-sag-and-manuscript-fill.md`。

- `geometry.json`：持握中段相对书脊/指腹支撑线的偏差；旧版向上，新版向下。62,667个纸页样本差0，闭合和2.10秒后封皮差0。
- `checks.json`：17项既有及针对性测试、生产构建、19项资产核对，以及未改文件与本轮源码哈希。
- `build-identity.json`：冻结eedd745基线与候选生产文件哈希；基线逐文件与首轮保存记录相符。
- `final/`：独立无头Chrome实际五款、全景、接触、正常/慢放，以及创建、完整进入/返回、减少动态、删除刷新检查。页面错误0。
- `final/opening.mp4`：真实Chrome正常速度录像；从原始WebM的2.25秒起保留4.7秒。`recording/metadata.json`记录点击重播在2.452秒；`recording/raw.webm`保留原视频。
- `performance/`：初始3配对及受控暖缓存补足5配对仍失败的原记录，以及定位重复纹理上传的剖析。
- `performance-final/`：去除5次冗余纹理上传后的最终代码；相同机器/Chrome154、1512×751/DPR1、同五书，本机与20Mbps/50ms冷暖3配对，受控暖缓存预先固定5配对。
- `final-upload-check/`：上述无视觉改动的性能修正后，再次完成创建、开书进入/返回、减少动态、删除刷新；页面错误0。最终封面与全景已重新捕获。

生图输出及实际提示词/来源在`assets/source/manuscript-filled/`，运行纹理在`public/assets/textures/manuscript-page-filled.webp`。纹理为原风格补齐，未声称编辑区外逐像素保持。

助手自检：持握阶段封皮中段下凹，材质和原翻页效果保持；内页手稿充实，未见额外的书名/简介汉字。此记录不代替用户本轮视觉评审。
