# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前迭代为 `v0.2.0-preview.1`（`iteration/next`，待用户评审），已认可小样保存在 `v0.1.0-baseline`，`main` 保留。baseline 对照：<http://127.0.0.1:4175/>。代码、Blender 源文件、GLB、纹理、参考来源和截图一起版本化；后续调整在独立分支进行。恢复/对比方法与边界见 [VERSIONING.md](VERSIONING.md)。

## 体验

- 点击实体书 → 查看信息 → 打开这本书；约 3.8 秒的抽书、桌面镜头、手部开封面和弯曲翻页，可跳过。
- 点击「继续最近的写作」或「全部作品」直接进入；`⌘/Ctrl + K` 搜索。
- 点击书桌魔法区域或「新建作品」，输入书名和封面色；约 3.1 秒成书归位。默认 3 本示例、2 个空位；超过 5 本仍保存在完整列表。
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
npm run test:assets
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
| `public/assets/textures/` | 两张原创生成的木纹与灰泥图片 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

布局由 `apps/web/src/room-layout.json` 统一提供给 Blender 和网页。`Scene.jsx` 管理房间与镜头，`BookInteraction.jsx` / `book-animation.mjs` 统一驱动手、封面、弯曲纸页和成书归位；当前没有烘焙骨骼动画。开发时访问 `?inspect=opening` 可逐帧检查接触，生产包不包含该检查页。运行时书封色、标题、项目位置来自 `library-model.mjs`，无需按用户作品修改 Blender。

## 验收与限制

见 `design-qa.md`、`evidence/v02/` 与 `PLAN.md`。主要交互在 Chrome 运行验收，4 项领域测试、实际导出几何接触/时序检查及构建通过。3 份 GLB 共 6,739,340 bytes（约 6.43 MiB），图片嵌入模型。

新版本收紧家具关系，采用矮柜、书桌和壁炉休息角；保留夜间冷暖光，加入局部使用痕迹。造型、手指与布料仍是简化的样片精度。参考图仅用于研究，没有作为运行场景背景。

本机开发态加载约 1.2–2.6 秒；多测试视图时约 43–55 FPS，关闭测试视图后的主预览约 93–120 FPS。包含缓存，不是跨设备或冷启动性能保证。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。开发控制台仍有上游 `THREE.Clock` 弃用提醒，构建有较大单个 JS 分块提示，不影响本次已验证流程。环境音只有轻声合成和弦，未做音质验收。
