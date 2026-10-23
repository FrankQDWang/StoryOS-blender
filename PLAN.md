# StoryOS Library — 当前方案与交接

更新日期：2026-10-23（Asia/Singapore）。开工先读本文件；只有涉及相应主题时再读下方历史指针。

## 当前交接

- **2026-10-23：用户授权执行基线收敛方案**：保存实验快照、归档原始证据、复核主候选、推送并经CI合并到main、打基线标签、清理实验分支与worktree。覆盖此前“候选不push／合并、原cap工作区保持”的停点；这次保存授权不改写原生桌面验收未完成的事实。保存记录见 `evidence/baseline-save-20261023/REPORT.md`。
- **实验保全**：两实验Git提交完整保存于 `archives/cap-experiments-20261023.bundle`，已verify；451份原始证据逐文件SHA核对后完整归档，本地保留。恢复命令见 `archives/README.md`；30FPS不进入main运行源码。

### 10月13日实施与验证记录

- **工作方式**：用户上班期间只使用后台／无界面 Chrome，不打开或抢占桌面。原生鼠标锁定验收未完成，后台锁定测试不能替代它。
- **当前候选**：根工作区 `codex/interaction-stalls`，基于已同步 main `f4979f7`。创建灯常驻且闲置强度为 0；已有手部资源分批上传、异步编译、独立场景离屏准备。模型、灯光效果、动画、交互保持。尚未提交、合并或推送，等待用户体验。
- **已验证**：创建最大帧间隔三轮 283/233/233 → 17/17/17ms；开书 83/100/117 → 33/17/33ms。11 张固定画面对照像素差均为 0，助手实看通过。17 项既有测试、正式构建、后台主要交互通过。拒绝锁定的负向样本正确失败。
- **加载证据**：分开服务的两批失败样本仍保留；同服务、公共资源字节一致的三组配对通过，冷首屏中位 1471 → 1242ms，暖首屏 1252 → 1184ms。详细口径与限制见 [优化报告](evidence/interaction-stalls/REPORT.md)，不把旧／失败样本改写为通过。
- **可体验入口**：`http://127.0.0.1:4405/preview.html`，正式生产候选；首次仅在该 origin 没有作品时植入五书演示。保留服务，不自动打开用户浏览器。
- **本轮继续交付**：用户批准在 15:00 前依次做连续交互、独立 30FPS 复测、轻量 CI、交接瘦身。[进度](evidence/delivery-prep/PROGRESS.md) 是本轮工作入口。
- **连续交互已完成**：正常生产候选的 13 步后台 journey 通过，覆盖空库、新建超五本、删除补位、开书返回／跳过、减少动态、Quick Access、取消、创建中刷新、清空重建；页面错误 0。证据 [journeys/smoke.json](evidence/delivery-prep/journeys/smoke.json)。
- **30FPS 复测完成，不采用到当前候选**：独立 `.worktrees/cap-30fps-recheck`／`codex/cap-30fps-recheck`；基于本次卡顿修复。首页CPU三组中位20.00%→14.36%，但每帧3.33→4.79ms；独立Metal一对每帧12.42→13.07ms，开书／创建最大约55–60ms。旧严格门槛失败，停止扩展；11张固定图像素差0、正常生产包13步journey通过。详见[复测报告](evidence/delivery-prep/cap/REPORT.md)。原 `codex/cap-30fps`（`37b95db`）保持不动。
- **CI 与文档已完成**：`.github/workflows/check.yml` 在push／PR运行 `npm run check`。全新依赖安装后，17项测试、正式构建、4项Sites包装检查全部通过；YAML可解析，GitHub尚未实际运行。PLAN从151,534字节收敛为约8KB；历史逐字节保留，所有本页链接已核对。详见[本轮交付](evidence/delivery-prep/PROGRESS.md)。

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
