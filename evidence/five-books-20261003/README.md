# 五款书本实施证据

用户确认于2026-10-03，验证于2026-10-04。基线 `eedd745`，候选 0.1.5-preview.1。

- `smoke.json`：最终生产预览4182的9项真实界面主流程，全部通过、页面错误0；01–05 PNG记录空架、五书、删除空位、清空刷新及新一轮第一本。
- `material-{1..5}-{cover,open}.png`：五款真实Chrome近景；`cover-contact-sheet.png`、`open-contact-sheet.png` 为等比联系表。
- `five-materials-overview.png`：五位全景。`contact-{1.7,side-1.7}.png`：原开书动作接触正侧面。
- `opening.json`：最终生产入口正常开书9帧时间戳、进入/返回、漫游Esc退出、低动态通过。最终帧集合以JSON列出的文件为准；`opening-contact-sheet.png` 为节选。助手已实看。
- `benchmark-raw.json`：完整28个冷/暖样本，包含全部初始波动；每个样本还测首开、工作区、返回和复开。`benchmark-summary.json` 为分组中位数，全部≤+10%。受控网络暖缓存因接近门槛补充到5对，原3对未删。
- `fresh-browser-start.json`：每个样本全新Chrome进程/空profile，3对本机冷启动，首屏中位数+4.97%。
- `build-identity.json`：基线及最终候选生产文件SHA，房间/书本/手部GLB、布局、火焰、手部代码与时序不变。
- `asset-check.json`：17项manifest资源和生产public产物校验通过。`visual-errors.json`：13张最终静帧捕获的页面/控制台错误为空。

`first-cover.png`、`first-open.png` 为首稿，后者保留了后来修复的纸背镜像；`refined-*` 为修正阶段；最终以 `material-*`、真实主流程和opening集合为准。首次并行开发捕获曾引起smoke等待超时，后续单独执行及生产执行均通过。早期基准工具返回后过早点击已修正为等待新Canvas实际实体绘制；只有修正后的完整样本进入统计。

验证依赖/脚本在 `tools/book-check/`；测试Chrome使用项目内专用profile，未用于创建或删除用户Chrome中的作品。最终已在用户Chrome打开4173，原3本作品仍在，服务留给用户体验。实际新增素材与提示词见 `assets/source/manuscript/`。
