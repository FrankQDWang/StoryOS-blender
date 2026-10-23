# 原生桌面验收状态

2026-10-13。

- 有界面Playwright点击未取得pointer lock，严格冒烟失败，结果在final-smoke/。
- 浏览器连接工具两次报request-header policy加载失败；尝试原生Chrome窗口。
- 工具检测到用户正在操作Chrome，先停止并询问独占一分钟；用户曾回复现在可以。
- 开始原生操作后用户要求“别抢占桌面可以吗”。立即停止所有桌面/UI操作，不再重试或抢占窗口。尚未完成原生点击、无按键环顾和重入证明，不报通过。
- 后台无界面Chrome严格冒烟两轮锁定/转向/退出/重入及全部核心流程通过，见final-smoke-headless/result.json；拒绝锁定的负向样本按预期失败，见denied-lock/。两类证据分开。
- 最终画面对照11张全部像素差0，见final-visual.json。原生检查前主动中断了正在运行的加载测量；final-loading/仅为部分样本，最终加载改用final-loading-complete/。
