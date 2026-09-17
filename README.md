# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前资产版本为 **0.1.3-preview.3**，用户于2026-09-17正式认可为当前保留版本，现已保存并合入本地/远端同步的 `main`，迭代分支已清理。该版本在A书房基础上统一右三台比例和阅读倾角、均衡间距、拉开蓝书台与书桌之间的留白；书桌和椅子保持位置、尺寸。正面及侧面、开书与通路验收通过。历史标签与旧提交保留；保存完成情况见 [PLAN.md](PLAN.md)，版本约定见 [VERSIONING.md](VERSIONING.md)。

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

此命令由 `scripts/build_library.py` 重新生成场景源文件与模型，再由 `scripts/bake_room_lighting.py` 在实体第二 UV 上烘焙局部遮蔽和直接/间接漫反射，最后由 `scripts/asset_manifest.py` 记录尺寸、哈希和版本。当前烘焙脚本使用本机 Cycles / Metal GPU，4096 像素、128 采样；运行网页不需要烘焙或 Metal。**重建会覆盖生成的 `.blend` 和 GLB；若手工修改 Blender 源文件，请另存一个版本。**

| 文件 | 用途 |
| --- | --- |
| `assets/source/storyos-library.blend` | Room / Book / Hands 集合；纹理已打包，可直接在 Blender 打开 |
| `public/assets/models/library-room.glb` | 房间和静态家具；按材质合并网格 |
| `public/assets/models/story-book.glb` | 通用书本；CoverPivot 和 PagePivot 铰链 |
| `public/assets/models/opening-hands.glb` | 预制手掌、手指与袖口 |
| `public/assets/models/scene.json` | 坐标、展示位和制作版本 |
| `public/assets/textures/` | 木纹、织物、灰泥、装饰图集与真实几何光照图；生成来源和烘焙参数均保留 |
| `apps/web/src/room-layout.json` | Blender、书位与导航共用的米制布局 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

`Scene.jsx` 管理场景、镜头、手部与翻页；`HearthFire.jsx` 提供立体火焰；`roaming.mjs` 负责身体碰撞和滑动。源布局由 Blender 与网页共同读取，导出副本保存在 `scene.json`。书封色、标题与项目数据无需修改 Blender。手部与书本源网格保持 baseline，无烘焙骨骼动画。

## 验收与限制

见 [design-qa.md](design-qa.md)、[PLAN.md](PLAN.md) 和 `evidence/v013-side-balance/`。本轮10项测试、保存模型几何、五台站位及镜头落点、圆台通路、构建与11份生产资产一致性通过。Chrome蓝书台、第五台完整开书进入对应作品，五书位占用画面通过；本轮未重测全屋浏览器步行或未改的创建/Quick Access流程。

最新目标为 `design/round-05/A-hearth-study/final.png`，已认可的preview.2正面亦为本次保留依据。当前1512×751同视口正面/侧面对照为 `evidence/v013-side-balance/comparison-front.jpg` / `comparison-side.jpg`；侧面临时固定镜头已从正式代码移除，参数与补丁留在证据中。整体构图保持，右台的台面轮廓及局部遮挡有小幅变化，不宣称正面逐像素不变。植物、灯具、火舌和材质微细节仍与概念图有差异，手部接触细节沿用原版。

3份GLB共23,419,356 bytes（约22.3 MiB）；房间150,034三角形。Book/Hands源顶点与baseline一致，运行GLB与已保存HEAD逐字节相同。当前全景截图HUD约54–75 FPS、加载1.9–2.9秒，为本机开发态观察，非性能基准或冷启动承诺。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。本轮捕获浏览器错误日志为空。上游 `THREE.Clock` 弃用提醒及构建的大JS分块提示仍在。环境音只有轻声合成和弦，未做音质验收。
