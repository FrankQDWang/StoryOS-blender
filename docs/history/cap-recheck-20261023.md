# 30FPS recheck — 2026-10-13

**复测完成，严格验收失败，停止扩展，不采用到根候选。**

本分支基于f4979f7 + 根工作区本轮创建／开书卡顿修复，再复制旧37b95db的FrameCap，只接入never/manual advance。根工作区4405原帧率候选保持；旧cap工作区未修改。项目依赖软链接仅本地复用，不提交。

权威报告：主工作区 `evidence/delivery-prep/cap/REPORT.md`（绝对根 `/Users/frankqdwang/MLE/StoryOS-blender`）。三组CPU每秒中位20.00%→14.36%，每帧3.33→4.79ms；一对Metal每帧12.42→13.07ms。开书／创建仍约55–60ms最大间隔，不符合旧严格门槛。11张固定画面差0、正常生产13步journey和后台鼠标锁定／无按键环顾主流程通过。

原始性能构建 `.cache/idle-render-cost/cap-recheck`；修正固定时钟测试入口 `.cache/idle-render-cost/cap-visual-fixed`。正常生产产物在apps/web/dist/client，4412/preview.html保留用于可选对照。没有push／合并，源码未提交。

本工作区PLAN是根目录当前交接副本，其中相对证据／归档路径需到主工作区读取。新工作首先读本文件与主工作区PLAN。后续采纳30FPS需要用户接受每秒省资源但每帧不更快的明确取舍；不能把本轮评估误写成所有验收通过。
