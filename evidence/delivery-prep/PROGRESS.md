# 2026-10-13 后台交付准备

**四项工作完成。推荐继续使用已消除卡顿的原帧率候选；30FPS复测未通过，保留独立。** 全程后台，无桌面接管，无push／合并。

用户同意：下午15:00（Asia/Singapore）前，依次完成连续使用流程、30FPS重新评估、轻量CI、交接整理。原生桌面验收不再重试；最终体验由用户有空时进行。

| 工作 | 交付与验证 |
| --- | --- |
| 连续使用 | 扩展现有 `tools/book-check/smoke.mjs`，独立无界面Chrome。13步通过，页面错误0：空库、创建六本、补位、删除、刷新、正常／跳过开书、减少动态、键盘Quick Access、删除当前作品、取消及创建中刷新。未发现应用缺陷。证据 `journeys/smoke.json`。 |
| 30FPS重新评估 | 新独立工作区 `.worktrees/cap-30fps-recheck`，原cap不动。三组CPU与独立Metal一对表明每秒资源减少，但每帧成本未下降，开书／创建有约55–60ms间隔，原门槛失败。11张固定图片素差0、正常生产13步及后台锁定冒烟通过。见 `cap/REPORT.md`、`cap/resource-summary.json`。停止扩展，不采用到根候选。 |
| 轻量CI | `.github/workflows/check.yml` + `npm run check`，Node24。独立 `.cache/ci-smoke` 全新安装后17项核心测试、生产构建、4项Sites包装测试全过。YAML解析通过，GitHub未实际运行。证据 `ci-result.json`、`ci-install.log`、`ci-check.log`。没有新测试框架或Blender要求。 |
| 交接整理 | PLAN从151,534字节收敛为当前摘要、有效范围和按主题索引。原历史完整写入 `docs/history/PLAN-through-2026-10-13.md`，SHA在 `plan-archive.json`，所有当前链接存在。应用AGENTS记录后台验收要求。 |

本轮交付准备未进一步修改根应用源码：`application-unchanged.json` 与 `application-baseline.json` 保存核对。此前创建／开书优化及其所有成功、失败样本在 `../interaction-stalls/REPORT.md`。

## 保留入口与工作区

- 推荐：`http://127.0.0.1:4405/preview.html`，根工作区 `codex/interaction-stalls`，从同步main `f4979f7`开始的本地未提交改动。
- 可选对照：`http://127.0.0.1:4412/preview.html`，本地 `codex/cap-30fps-recheck`；严格验收失败，仅留作比较，不代表推荐。
- 原停止任务：`/Users/frankqdwang/.codex/worktrees/cap-30fps/StoryOS-blender`，`codex/cap-30fps`，`37b95db`，未修改。
- 测量端口4410/4411/4413收尾关闭，正常预览4405/4412保留。重启方式见工具README；可用冻结构建和已保存源码继续复现。

原生鼠标锁定仍未验收；后台成功不是原生通过。`cap/smoke/`、`cap/visual/` 失败样本与后续修正记录完整保留。收尾拒绝锁定负向用例在 `denied-lock/`，应退出非零，确认脚本不会把拖拽替代判为锁定通过。

当前未commit／push／合并，不改用户本地作品。下一步是用户有空体验推荐4405候选，再决定保存；没有未完成的后台实施步骤。
