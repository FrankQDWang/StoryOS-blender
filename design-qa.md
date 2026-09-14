# v0.1.1-preview.1 验收 · 2026-09-14

result: passed for preview review

用户看过 v0.2 后要求恢复第一版，只优化壁炉空隙。原版前端完全恢复，壁炉几何单独修复。第二版验收保存在 `evidence/v02/design-qa.md`，不适用于当前手书动作。

## 画面与实际操作

- `evidence/v011/overview.png`：实际 Chrome 全景，1512 × 751；第一版布局、阅读台、夜间冷暖光、中央魔法圆台恢复。
- `book-and-hearth.png`：选中第一本书的实际近景；连续侧柱、拱口与台面连接。
- `workspace.png`：点击实体书并完整播放原版动作后进入《星海余烬》；已操作返回。
- 中央「写下一个新世界」打开新建表单，关闭后数量仍为三；没有新建、清空或迁移用户项目。
- 本轮仅重测恢复所需流程。搜索、超额容量、低动态、漫游等未全部重测；其前端代码与 baseline 完全一致，历史验收见 baseline 标签。

## 模型与工程证据

- `git diff v0.1.0-baseline -- apps/web/src` 无差异。
- `scripts/check_hearth.py` 读取两份保存的 Blender 模型：两侧 330 条正面射线，baseline 16 处漏空，当前 0 处；拱口上沿 25/25 命中，炉膛中部仍开放。结果见 `evidence/v011/hearth-check.json` 和日志。这是指定截面的实体抽查，不等于全场景流形或连续碰撞证明。
- `asset-parity.json`：Book / Hands 集合全部世界空间顶点与 baseline 相同，按 0.01 mm 精度比较。GLB 导出二进制排序不稳定，不以文件字节相同判断几何相同。
- `npm test`：4/4 通过，见 `tests.log`。
- `npm run build`：通过，见 `build.log`；较大 JS 分块提示仍在。
- `npm run assets`：成功重建。三份 GLB 共 6,049,352 bytes，房间 35,668 三角形，书本 3,788，手部 3,224。两张纹理打包进源文件；精确哈希见 `assets/manifest.json`。
- Blender 制作命令增加 factory startup 和 Python 异常退出码，避免本机节点命名设置和静默错误造成索引旧模型；不改用户 GUI 设置。
- 本机开发态本次约 41–45 FPS，页面显示加载 1.9 秒；含缓存和当前机器负载，不是跨设备性能承诺。

## 边界

当前为第一版加壁炉修复。书和手的简化造型、原版接触局限一并恢复，没有复用第二版接触验收或宣称解决这些问题。没有真实 StoryOS 集成，工作区仍为占位；沿用既有纹理，无新参考资产。

预览 `http://127.0.0.1:4173/`；在 `iteration/next` 保存为 `v0.1.1-preview.1`。`main`、`v0.1.0-baseline`、`v0.2.0-preview.1` 保持不变。
