# StoryOS · 私人藏书室

一个独立的桌面 Chrome 入口体验样片。一本书代表一个作品：可以在房间里点书、自由漫游，也可以直接从最近作品或列表进入。开书后的写作页面为占位工作区，数据仅保存在本浏览器。

公开仓库：[FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)。

当前预览：<http://127.0.0.1:4173/>。开发服务已启动。

## 版本管理

当前迭代为 `v0.1.1-preview.1`（`iteration/next`）：恢复第一版，只修复壁炉空隙。第二版 `v0.2.0-preview.1` 保留为历史，已认可小样 `v0.1.0-baseline` 与 `main` 不动。代码、Blender 源文件、GLB、纹理、参考来源和截图一起版本化；后续调整在独立分支进行。恢复/对比方法与边界见 [VERSIONING.md](VERSIONING.md)。

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
| `public/assets/textures/` | 两张原创生成的木纹与灰泥图片 |
| `assets/manifest.json` | 资源字节数、SHA256、三角形数量、版本和来源索引 |

`Scene.jsx` 管理第一版房间、镜头、手部和翻页动作；没有烘焙骨骼动画。书位与制作信息在 `scene.json` 中记录，脚本和网页保留 baseline 坐标。运行时书封色、标题与项目数据无需修改 Blender。第二版的桌面开书和开发检查页已随回滚移除。

## 验收与限制

见 `design-qa.md`、`evidence/v011/` 与 `PLAN.md`。Chrome 全景、近景、完整开书、返回、新建表单取消通过；4 项领域测试和构建通过。3 份 GLB 共 6,049,352 bytes（约 5.77 MiB），图片嵌入模型。

第一版布局、光影、阅读台与中央魔法圆台恢复，壁炉改为连续两侧炉身和拱口。保存模型的 330 个两侧抽查位置由原版 16 处漏空降为 0，炉膛仍开放。本轮只处理壁炉，手部造型和动作也恢复第一版，原有接触局限仍在。

本机开发态本次约 41–45 FPS，页面显示加载 1.9 秒。包含缓存与当前机器负载，不是跨设备或冷启动性能保证。

未集成真实 StoryOS、账户、云同步和编辑器；未验收移动端、其他浏览器和低端显卡。开发控制台仍有上游 `THREE.Clock` 弃用提醒，构建有较大单个 JS 分块提示，不影响本次已验证流程。环境音只有轻声合成和弦，未做音质验收。
