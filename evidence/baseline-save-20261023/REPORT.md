# 基线收敛 — 2026-10-23

用户批准保存候选、归档实验、推送并经CI合并到main、打标签和清理分支／worktree。保存与合并完成，最终交接随基线标签保存。

## 保留的运行改动

只合入创建光源常驻（闲置强度0）和开书已有资源分批准备。保持原帧率、画质、模型、动画、五书与Quick Access行为；30FPS代码不合入。运行提交6850a1a，工具与CI提交5474544。

## 验证

- 本次重新运行 `npm run check`：17项核心测试、生产构建、4项Sites包装测试通过；日志check.log。
- 本次正常生产包后台Chrome连续13步journey通过，页面错误0；证据journeys/smoke.json。
- 当前应用所有源码SHA与10月13日已验证候选一致，见source-verification.json。11张图像素差0及创建／开书性能收益是保留证据，本次没有重跑性能或重新声明用户视觉认可。
- 后台鼠标锁定冒烟在pointer-smoke/result.json；原生桌面验收未进行。全过程未接管用户桌面。
- GitHub的push与pull_request检查均通过；PR #4以合并提交eb2773c保存。

## 归档与恢复

451份完整原始证据已写入本地archives/interaction-evidence-20261023.tar.gz，每个成员SHA核对成功。原始文件仍在原路径。Git保留报告、汇总与关键截图；原始大文件仅本地，清单和归档SHA在archive-manifest.json。

两个实验的提交已保存于随Git同步的archives/cap-experiments-20261023.bundle：旧37b95db、复测ef94dd3。git bundle verify通过，需要的main历史仍在仓库。源码、实验结果与原提交可恢复，故清理不丢实验；node_modules及可重建缓存不保存。恢复命令在archives/README.md。

本次新截图也完整归档于archives/baseline-smoke-20261023.tar.gz，并逐文件SHA验证。Git只保留全景、开书和创建后的关键帧，完整连续截图本地可恢复。

## 最终收敛

- [PR #4](https://github.com/FrankQDWang/StoryOS-blender/pull/4)已合并，合并提交 `eb2773cc70acf15a24659ce42427af7a3ad39f6d`。
- [push CI](https://github.com/FrankQDWang/StoryOS-blender/actions/runs/39920979129)与[PR CI](https://github.com/FrankQDWang/StoryOS-blender/actions/runs/39921049124)均成功。
- 本地main快进至合并提交，三个工作分支和两个实验worktree已清理；远端工作分支已删除。只保留main和一个根worktree。
- 基线标签 `baseline-2026-10-23` 标记随后仅更新交接记录的最终提交，运行源码不再变化。历史三个标签保持。
- 本轮全程后台，无桌面接管。正常生产预览4420/preview.html保持，测量服务4421已停止。
- 传输中多次TLS／连接重置失败后成功；仅用了单次Git缓冲／HTTP传输参数，没有修改代理、路由或全局网络配置。
