# StoryOS Library — 当前方案与交接

更新日期：2026-10-23（Asia/Singapore）。开工先读本文件；只有涉及相应主题时再读下方历史指针。

## 当前交接

- **2026-10-23基线已合并**：用户授权保存、推送、合并与清理；[PR #4](https://github.com/FrankQDWang/StoryOS-blender/pull/4)经两次GitHub CI成功后合并，运行合并提交 `eb2773c`。只保留本地／远端main和根worktree；三个工作分支、两个实验worktree已清理。基线标签 `baseline-2026-10-23` 标记本次最终交接状态。
- **保留实现**：创建光源常驻且闲置强度0；开书前分批准备已有手部GPU资源。保持原帧率、模型、动画、画质、五位与交互。30FPS未达到原标准，不进入main。
- **本次新验证**：17项核心测试、正式构建、4项Sites包装检查、正常生产包13步连续操作、后台锁定／无按键环顾／WASD／Esc／重入通过。PR的push和pull_request检查均成功，见[保存报告](evidence/baseline-save-20261023/REPORT.md)。
- **保留证据**：应用源码SHA与10月13日验证版本一致。该轮创建最大帧间隔283/233/233→17/17/17ms，开书83/100/117→33/17/33ms，11张固定图像素差0；这些是历史性能／视觉测量，本次没有重复测量。[详细报告](evidence/interaction-stalls/REPORT.md)保留加载失败样本及最终同服务配对通过的口径。
- **30FPS实验可恢复**：旧37b95db与复测ef94dd3的源码／历史提交保存在随Git同步的 `archives/cap-experiments-20261023.bundle`，已verify。CPU每帧与GPU每帧未下降，动作仍有55–60ms间隔；结论见[复测报告](evidence/delivery-prep/cap/REPORT.md)。
- **证据归档**：451份旧原始证据及本次完整连续截图均逐文件SHA校验，归档仅本地保留；Git保存报告、汇总和关键帧。恢复方式见[archives/README](archives/README.md)，清理缓存时保留archives目录。历史PLAN完整归档保持。
- **后台工作方式**：继续使用无界面Chrome，不抢占桌面。原生桌面鼠标锁定验收未进行，保存授权不改写这一事实。生产预览为 `http://127.0.0.1:4420/preview.html`，只在该origin无本地作品时初始化五书演示，不自动打开浏览器。
- **下一步**：从此main基线开小范围功能分支；继续保持当前画面与交互，按实际产品需求推进，不默认恢复30FPS或开启视觉改版。兄弟StoryOS仍只读。

## 已接受范围

- 独立桌面 Chrome 体验样片，一本书代表一个小说项目；开书进入可返回的占位工作区。真实 StoryOS 集成仍属后续阶段，兄弟目录 `../StoryOS` 只读。
- 私人、低密度、夜间魔法藏书室，五个稳定独立展示位，留出行走空间。可选漫游和可见的直接 Quick Access 都保留；不要把漫游设为必经步骤。
- 初始正式书库为空；本地创建持久化，刷新恢复；已有作品保持。开发五书预览在副本中补演示书，`?preview=off` 显示存储库。
- 新建按序分配空位；删除留下空位；已分配位置和外观稳定。五位不是作品数量上限，超额作品保留在完整列表，不挤走现有书。取消不生成作品。
- 鼠标／WASD 漫游，Esc 退出；按钮可完成主要流程，Cmd/Ctrl+K 打开搜索。保留减少动态、跳过动画及 DOM 项目入口降级。
- 保留书名的中英／混排和长短标题适配；书名来自项目数据。无真实编辑器、账户、云同步或生产发布。

## 当前视觉与资产基线

| 涉及修改 | 必读材料与已接受决定 |
| --- | --- |
| 房间／站位／碰撞 | [iteration 05](design/iterations/05-a-hearth-study-selected.md)、`design/round-05/A-hearth-study/final.png`；已认可 preview.3。五位与书桌位置保持，`apps/web/src/room-layout.json` 同时驱动 Blender、书锚点与碰撞。 |
| 手部模型／动作 | [design-qa](design-qa.md)、[MakeHuman 来源](assets/vendor/makehuman/README.md)、[动作审查](design/iterations/08-opening-motion-audit.md)。保留 CC0 MakeHuman 替换，不恢复被拒绝的自制手；按一次一个可见问题增量修正。 |
| 封皮／翻页／内页 | [iteration 28](design/iterations/28-cover-sag-and-manuscript-fill.md)。已认可 preview.5 `3093181`：有挺度的薄皮、持握中段向下凹、连续多页翻动、填满中央的原风格手稿；不恢复软塌或额外中文字覆盖。 |
| 标题字体／书色 | [selection](design/round-11-cover-readability/selection.json)、`assets/vendor/cover-fonts/`。深色原图 1、浅色原图 3；只采用字体排版，不采用生成图比例。棕色已批准提浅至 `#b09b80`，无悬停／选中专属补光，真实首页暗氛围保持。 |
| 窗景 | [iteration 29](design/iterations/29-moonlit-window-plan.md)、[窗景证据](evidence/moonlit-window/)。已认可最终月夜树林与天空边缘修复，停止美术探索；助手视觉与用户认可分别记录。 |
| 渲染优化 | [阴影缓存报告](evidence/idle-render-cost/REPORT.md)、[本轮卡顿报告](evidence/interaction-stalls/REPORT.md)。新增动态投影物／投影光源需同步 ShadowUpdates 失效条件；视觉与加载独立验收。 |

## 执行与验收

1. 用最小实现保持当前画面与交互；运行既有核心测试和针对改动的主路径冒烟，不扩建庞大测试体系。
2. 视觉改动须实际检查 Chrome 全景和相关局部／连续动作，报告助手判断，用户认可另记。概念图不替代实际可漫游效果。
3. 性能用同机、同视口／DPR、同数据／构建身份配对；保留所有失败样本。加载增幅原门槛 ≤10%。CPU、GPU、帧时间分别记录，不把降低帧率当作每帧效率提高。
4. 30FPS 的旧严格门槛保持：所有活动状态约 30FPS、均匀间隔，动作／相机时长误差 ≤1 帧，首页三对 CPU/GPU 每帧均下降，加载 ≤10%，主流程与连续画面通过；详细旧停止理由见历史索引。原生 GPU 与 WebGL 查询口径分开。
5. 常规实现自主推进；涉及实质产品取舍、付费／外部承诺或新增安装位置再问。项目资产、下载和验证资料在本目录；依赖用项目本地或既有包管理器。Blender 源／生成脚本与资产来源一起保留。
6. 按10月23日授权收敛到同步main，历史标签与实验恢复包保持。后续从该基线开启小范围分支，每次有意义进展后更新当前交接。

## 历史索引（按主题读取）

[完整原始 PLAN](docs/history/PLAN-through-2026-10-13.md) 保留重组前全部字节；其中路径相对仓库根目录，旧授权／状态由本页与后续用户指令覆盖。[归档校验](evidence/delivery-prep/plan-archive.json) 保存 SHA256。

- **范围／起源与早期探索**：归档的“开工基线”“需求来源与已确认决定”“执行顺序与验收”；早期被否定概念仅供追溯。
- **房间和站位**：归档 9 月 13–17 日记录、iteration 05 和 `evidence/v013-side-balance/`。
- **手部／书本迭代**：归档 9 月 17 日至 10 月 4 日记录、iteration 08/26/28、`evidence/book-approved-save-20261004/`。
- **五书／字体／窗景保存**：归档 10 月 4–5 日记录、`evidence/cover-typography-focus-fix-20261004/`、`evidence/moonlit-window/save-checkpoint/`。
- **阴影缓存与原生鼠标锁定纠正**：归档 10 月 5 日记录、`evidence/idle-render-cost/pointer-lock/`、`evidence/idle-render-cost/save-main.md`。
- **旧 30FPS 停止记录**：[已归档停止记录](docs/history/cap-30fps-20261005.md)，旧构建创建同步约 233ms，不能仅靠限帧消除；旧证据不是当前复测结果。
- **本轮复盘／卡顿优化／连续检查**：`evidence/interaction-stalls/REPORT.md` 与 `evidence/delivery-prep/PROGRESS.md`。
