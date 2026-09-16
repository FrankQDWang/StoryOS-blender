# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前资产版本为 **0.1.3-preview.2**（`iteration/next` 已认可进度快照）：按已选 A 图重新校准镜头、五台朝向/比例、窗右桌椅、圆台/地毯及木材和空间光照。`0.1.3-preview.1` 的还原效果已被用户否定；本轮实际检查见下方验收记录。`0.1.2-preview.4` 是此前已认可并保存版本。用户已认可当前整体效果并要求提交保存；本次为本地Git快照，尚未推送，main 和现有标签未移动。右侧三台侧面比例及书桌邻近关系留待下一轮局部调整，书桌现位优先保留。恢复/对比见 [VERSIONING.md](VERSIONING.md)，最新范围以 [PLAN.md](PLAN.md) 为准。

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

见 [design-qa.md](design-qa.md)、[PLAN.md](PLAN.md) 和 `evidence/v013-a-rebuild/`。10项测试、保存模型几何、五台站位及镜头落点、圆台通路、构建与11份生产资产一致性通过。Chrome完整开书返回、第五台、原生W短步接近后E选书、搜索直达、圆台创建取消通过；完整绕行由运动函数校验，未宣称浏览器走完全屋。

最新目标为 `design/round-05/A-hearth-study/final.png`；同尺寸1849×851实拍为 `evidence/v013-a-rebuild/23-overview-final.jpg`，同框全景和局部为 `comparison-full.jpg` / `comparison-details.jpg`。正常1512×695窗口为 `24-overview-native.jpg`。本轮正面对照自检通过，用户已认可整体效果并要求保存；新增侧面协调问题见PLAN.md，尚未实施修正。植物、灯具细部、火舌和材质微细节仍与概念图有差异，不宣称逐像素相同。手部接触细节沿用原版。

3份GLB共23,275,792 bytes（约22.2 MiB）；房间150,034三角形。Book/Hands源顶点与baseline一致，运行GLB与已保存HEAD逐字节相同。最终全景HUD约70–92 FPS（视口不同），加载3.1秒，为本机开发态观察，非跨设备或严格冷启动承诺。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。应用错误0条；另有2条翻译扩展网络错误，记录中已区分。上游 `THREE.Clock` 弃用提醒及构建的大JS分块提示仍在。环境音只有轻声合成和弦，未做音质验收。
