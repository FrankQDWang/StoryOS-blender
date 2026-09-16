# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前资产版本为 `0.1.2-preview.4`（`iteration/next`，未新增 Git 标签），用户于 2026-09-16 实际体验后认可并要求保存进度：暖炉房间、清楚的漫游空间，以及后排 0°、中段内收 10°、前景内收 20° 的阅读台布局。第二版 `v0.2.0-preview.1` 保留为历史，已认可小样 `v0.1.0-baseline` 与 `main` 不动。恢复/对比方法与边界见 [VERSIONING.md](VERSIONING.md)，最新范围以 [PLAN.md](PLAN.md) 为准。

## 体验

- 点击实体书 → 查看信息 → 打开这本书；约 2.6 秒的固定镜头、手部和翻书转场，可跳过。
- 点击「继续最近的写作」或「全部作品」直接进入；`⌘/Ctrl + K` 搜索。
- 点击中央魔法圆台或「新建作品」，输入书名和封面色；约 3.1 秒成书归位。默认 3 本示例、2 个空位；超过 5 本仍保存在完整列表。
- 「自由漫游」：WASD / 方向键移动，鼠标环顾；若浏览器拒绝指针锁定，提示改为按住鼠标拖拽。`Esc` /「返回全景」退出。靠近作品后可按 `E` 查看。
- 右上角可减少动态效果或打开简易环境音。列表与创建表单支持键盘；3D 资产失败时仍可从列表或快捷入口进入。

## 重新启动

已导出的 GLB 随项目保存，只运行网页不需要 Blender。

```sh
cd /Users/frankqdwang/MLE/StoryOS-blender
npm --prefix apps/web ci
npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
```

```sh
npm test
npm run build
```

Node/npm 的现有安装用于前端；依赖精确版本在 `apps/web/package-lock.json`。服务只绑定本机，未发布到外网。

## Blender 源资产

Blender 5.2.1 LTS：`/Applications/Blender.app`，Homebrew 管理。

```sh
npm run assets
```

此命令由 `scripts/build_library.py` 重新生成场景源文件与模型，再由 `scripts/asset_manifest.py` 记录尺寸、哈希和版本。**重建会覆盖生成的 `.blend` 和 GLB；若手工修改 Blender 源文件，请另存一个版本。**

| 文件 | 用途 |
| --- | --- |
| `assets/source/storyos-library.blend` | Room / Book / Hands 集合；纹理已打包，可直接在 Blender 打开 |
| `public/assets/models/library-room.glb` | 房间和静态家具；按材质合并网格 |
| `public/assets/models/story-book.glb` | 通用书本；CoverPivot 和 PagePivot 铰链 |
| `public/assets/models/opening-hands.glb` | 预制手掌、手指与袖口 |
| `public/assets/models/scene.json` | 坐标、展示位和制作版本 |
| `public/assets/textures/` | 木纹、灰泥与四象限装饰图集，均保留生成来源 |
| `apps/web/src/room-layout.json` | Blender、书位与导航共用的米制布局 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

`Scene.jsx` 管理场景、镜头、手部与翻页；`HearthFire.jsx` 提供立体火焰；`roaming.mjs` 负责身体碰撞和滑动。源布局由 Blender 与网页共同读取，导出副本保存在 `scene.json`。书封色、标题与项目数据无需修改 Blender。手部与书本源网格保持 baseline，无烘焙骨骼动画。

## 验收与限制

见 `design-qa.md`、`evidence/v012-gentle-angles/` 与 `PLAN.md`。当前版本 10 项领域/漫游测试、模型几何检查、生产构建、Chrome 后排漫游/E 选书、开书返回和前景选书通过；整体氛围阶段的搜索、新建取消/归位/刷新保存及低动态流程记录在 `evidence/v012/`。3 份 GLB 共 12,247,380 bytes（约 11.68 MiB），图片嵌入模型。

暖炉、冷夜窗、木材/灰泥和贴墙陈设参照 `design/round-04/01-open-hearth.png`；当前实际截图在 `evidence/v012-gentle-angles/07-overview-final.jpg`。保留五台与中央留白，五台正面可达，圆台可完整绕行。壁炉 330 条柱射线零漏空、拱沿 25/25 命中；手部接触局限仍在，按用户要求暂缓。

本机原生 DPR 2 多页测试约 39–64 FPS；最终 1512×756、DPR 1 的单页截图显示 120 FPS、加载 1.1 秒。条件不同，不作为跨设备或冷启动性能保证。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。开发控制台仍有上游 `THREE.Clock` 弃用提醒，构建有较大单个 JS 分块提示，不影响本次已验证流程。环境音只有轻声合成和弦，未做音质验收。
