# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前小样保存为 Git 标签 `v0.1.0-baseline`。代码、Blender 源文件、GLB、纹理、参考来源和截图一起版本化；后续调整在独立分支进行。恢复/对比方法与边界见 [VERSIONING.md](VERSIONING.md)。

## 体验

- 点击实体书 → 查看信息 → 打开这本书；约 2.6 秒的镜头、手部和翻页，可跳过。
- 点击「继续最近的写作」或「全部作品」直接进入；`⌘/Ctrl + K` 搜索。
- 点击中央魔法台或「新建作品」，输入书名和封面色；约 3.1 秒成书归位。默认 3 本示例、2 个空位；超过 5 本仍保存在完整列表。
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
| `public/assets/textures/` | 两张原创生成的木纹与灰泥图片 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

浏览器的相机、手部、封面、纸页和成书动画由 `apps/web/src/Scene.jsx` 的预制变换驱动，当前没有烘焙骨骼动画。运行时书封色、标题、项目位置来自 `library-model.mjs`，无需按用户作品修改 Blender。

## 验收与限制

见 `design-qa.md`、`evidence/` 与持续交接文件 `PLAN.md`。主要交互已在 Chrome 运行验收，4 项领域规则测试及构建通过。普通开发态加载约 1.1–2.1 秒、截图可见约 50–109 FPS；这是本机采样，含缓存，不是性能承诺。3 份 GLB 共 6,028,460 bytes（约 5.75 MiB），图片嵌入模型。

首版用于判断空间与入口交互。它采用简化立体家具和夜间冷暖光，雕刻、纸页弯曲及手部质感尚未达到电影参考的细致程度。参考图仅用于研究，未用作运行场景内容。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。开发控制台仍有上游 `THREE.Clock` 弃用提醒，构建有较大单个 JS 分块提示，不影响本次已验证流程。环境音只有轻声合成和弦，未做音质验收。
