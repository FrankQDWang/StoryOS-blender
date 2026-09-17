# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

已认可基线为 **0.1.3-preview.3**，于2026-09-17保存到本地/远端同步的 `main`。它在A书房基础上统一右三台比例和阅读倾角、均衡间距、拉开蓝书台与书桌之间的留白；书桌和椅子保持位置、尺寸，正面及侧面已获认可。

已保存的精修基线 **0.1.4-preview.2** 于2026-09-17通过 [PR #1](https://github.com/FrankQDWang/StoryOS-blender/pull/1) 合入同步的main。已用 **MakeHuman/MPFB 的 CC0 真人比例手形、原始骨骼权重和 Mindfront 的 CC0 皮肤**替换被否定的自制手；开书动作由项目适配并烘焙。火焰保持上轮改善，房间仍为已认可基线。素材来源见 [来源记录](assets/vendor/makehuman/README.md)，最新交接见 [PLAN.md](PLAN.md)。

当前工作区为 **0.1.4-preview.4**，在 `codex/wrist-motion-step` 逐点改进。按1.70米角色选择19.5cm手长，修复人体跟随书位缩放、加厚袖子，并重做右手侧边夹持、抬起及松手衔接。已完成Chrome主/侧视、五书位、正常/慢放及真实入口视觉检查；用户于2026-09-17认可并授权提交、push、合并和分支清理，保存进行中。详见[本轮记录](design/iterations/10-human-scale-and-side-grip.md)。

此前preview.3的上方右手动作被用户否定，已补充[五段真人参考与改进方向](design/iterations/09-human-opening-reference-study.md)。preview.4已据此实现侧边夹持并获本轮认可；完整肩肘协作和细微受力仍可继续优化。

## 体验

- 点击实体书 → 查看信息 → 打开这本书；约 3.5 秒的固定镜头、手部和翻书转场，可跳过。
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

此命令由 `scripts/build_library.py` 重新生成场景源文件与模型，再由 `scripts/bake_room_lighting.py` 在实体第二 UV 上烘焙局部遮蔽和直接/间接漫反射，再由 `scripts/build_makehuman_hands.py` 从已保存的 CC0 源人体裁切双手、制作袖口并烘焙动作，最后由 `scripts/asset_manifest.py` 记录尺寸、哈希和版本。当前烘焙脚本使用本机 Cycles / Metal GPU，4096 像素、128 采样；运行网页不需要烘焙或 Metal。**重建会覆盖生成的 `.blend` 和 GLB；若手工修改 Blender 源文件，请另存一个版本。**

| 文件 | 用途 |
| --- | --- |
| `assets/source/storyos-library.blend` | Room / Book / Hands 集合；纹理已打包，可直接在 Blender 打开 |
| `public/assets/models/library-room.glb` | 房间和静态家具；按材质合并网格 |
| `public/assets/models/story-book.glb` | 通用书本；CoverPivot 和 PagePivot 铰链 |
| `public/assets/models/makehuman-hands.glb` | 当前蒙皮双手、袖口、1K贴图与3.5秒动作 |
| `assets/source/makehuman-hands.blend` | 独立手部源文件；动画与贴图已打包 |
| `assets/vendor/makehuman/` | CC0原始资产、许可与固定来源 |
| `public/assets/models/scene.json` | 坐标、展示位和制作版本 |
| `public/assets/textures/` | 木纹、织物、灰泥、装饰图集与真实几何光照图；生成来源和烘焙参数均保留 |
| `apps/web/src/room-layout.json` | Blender、书位与导航共用的米制布局 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

`Scene.jsx` 管理场景和镜头；`opening-sequence.json` 为离线手部动画制作及网页封面、书页提供共同时间参数。`OpeningHands.jsx` 播放 `makehuman-hands.glb` 内的动作，`TurningPages.jsx` 生成可弯曲纸张。左手支撑书身，右手抬起封面后松开，前臂与手腕分别处理方向。`HearthFire.jsx` / `HearthBed.jsx` 和房间布局保持；`roaming.mjs` 负责碰撞和滑动。

当前双手共42关节、28,064三角形、一个烘焙片段，GLB为1,225,908 bytes（约1.17 MiB）。可用 `npm run assets:hands` 单独重建，不覆盖房间；普通重建只需本项目已保存资产与Blender，不依赖MPFB全局安装或下载。`writer-hands.*` 和旧 `opening-hands.glb` 保留为实验历史，当前入口不加载。漫游可见身体仍未实现。

开发态 [动作检查页](http://127.0.0.1:4173/review.html?slot=0&time=0.8) 可切换五个书位、暂停时间、正常/四分之一速度重播；静帧状态停止连续渲染。检查页使用真实场景组件，不读写作品数据，也不包含在生产HTML入口中。验收记录见 `design-qa.md`。

## 验收与限制

当前preview.4证据在 `evidence/v014-human-scale/`：同视角前后对照、侧面接触、正常/慢放、第一书位正式进入与五书位关键姿态均已目视检查。14项测试和构建通过；完整肩肘人体、左手动态受力等仍待后续，不宣称整体动作已最终达标。

上一轮preview.2证据在 `evidence/v014-free-hands/`：源手形、五书位×三个姿态、正常速度/四分之一速度连续截图，以及正式入口的开书过程均已目视复查。正式流程验证第一/第三书位完整开书进入、第二书位跳过、低动态直接进入、搜索直达和返回；第四/第五位使用独立检查页，不宣称创建了用户作品或完成其真实项目进入。

12项测试、生产构建、13份public资源与产物逐字节一致检查通过；最终两页面捕获控制台错误0条。房间、书本及7份原纹理哈希保持。详细修正过程包括袖口穿插、握书位置、入场袖子露头和开发环境重复挂载导致动画停播，见 [design-qa.md](design-qa.md)。

本轮没有重测全屋浏览器步行，也没有更改布局、漫游碰撞或创建逻辑。原房间验收证据仍在 `evidence/v013-side-balance/`，视觉基线为 `design/round-05/A-hearth-study/final.png`。窗景/墙面/灯具精修及漫游手脚仍属后续范围。

当前为本机Chrome样片，未集成真实StoryOS、账户、云同步和编辑器；未验收移动端或低端设备。帧率记录受多个Chrome窗口与截图操作影响，本轮不宣称已证明性能无退化。GitHub保存状态见PLAN，本次不部署网站。构建已有的大JS分块提示仍在。
