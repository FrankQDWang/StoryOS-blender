# 本轮 Chrome 验证

依赖用 `npm ci --prefix tools/book-check` 安装在项目内；使用本机 Google Chrome。

- `prepare-textures.mjs`：从已保存的 ImageGen 图集导出共享纹理并记录来源/哈希。
- `serve.mjs <directory> <port>`：同口径静态生产服务，用于冻结基线与候选对照。
- `smoke.mjs [url]`：独立浏览器 context，通过实际创建/删除界面检查顺序、空位、完整列表、取消和刷新。默认连接本轮专用 Chrome CDP 9484，默认 URL 4173。
- `visual.mjs`：在 Vite 的 review.html 中拍摄五款封面/内页、接触正侧面、全景。
- `benchmark.mjs`：项目内专用 Chrome profile，固定五本书，生产基线 4180 / 候选 4182；本机和20 Mbps / 50 ms网络，各3组冷/暖缓存配对样本。保存每个样本和中位数对照。
- `benchmark.mjs --warm-check`：为受控网络暖缓存的短时波动补两组配对，保留原样本并合并统计。
- `fresh-start.mjs`：每个样本重新启动 Chrome 并使用全新空 profile，3组本机冷启动配对，检查首轮着色器/缓存差异。
- `opening.mjs`：生产预览真实点书、连续开书截图、进入/返回、漫游入口/退出及低动态流程。

首屏时间要求当前 Canvas 已执行实体材质绘制，再等待帧与 GPU 完成；返回同样等待新的 Canvas。手部时间取点击后的首个 `USE_SKINNING` 且具有实体光照材质的实际绘制调用（不把阴影 pass 算成手部显示）。这是渲染提交时点，连续 Chrome 画面另行检查。使用同样的仪器同时测基线/候选，不修改产品运行代码。

证据统一保存到 `evidence/five-books-20261003/`（用户确认于10月3日，实施跨至10月4日）。本轮冻结基线位于忽略目录 `.cache/five-books/baseline/`，其代码基线为 `eedd745`；产物文件 SHA 见证据中的 `build-identity.json`。

## 2026-10-04 封面文字

- `cover-typography.mjs`：独立无头Chrome实拍首页深/浅、中/英文、长标题与混排。近景只裁取原首页相机投影，保持光照。校验正常英文按词换行与60字完整性，证据默认在`evidence/cover-typography-20261004/visual/`。
- 本轮生产对照基线`907b14f`冻结于`.cache/cover-typography/baseline/client`，使用同一`serve.mjs`在4180/4182提供基线/候选。`flexible-benchmark.mjs`的`BOOK_CHECK_LOCAL_ROUNDS=5`可事先固定本地样本数；`BOOK_CHECK_EXTEND_NETWORK=local`只对已经保存的3组本地样本补第4、5组，保留其余网络样本。最终每次完整构建独立测量，不能把不同候选混成一组。
