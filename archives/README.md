# 本地研究资料归档

2026-10-04保存用户认可的0.1.5-preview.5并清理分支时，将此前未提交的145份研究、旧概念和监督资料归档到本目录的`local-research-before-book-approval-20261004.tar.gz`。归档保留原相对路径，逐文件SHA256已核验，清单在`evidence/book-approved-save-20261004/inventory.json`。

该压缩包仅保留本地，不属于运行资产；当前认可版本的代码、素材、来源和验收证据已纳入Git并同步远端。历史PLAN中指向这些旧研究路径的记录可从包中恢复。

需要恢复时，在项目根目录运行：

```sh
tar -xzf archives/local-research-before-book-approval-20261004.tar.gz
```

清理缓存时保留本目录。历史Git标签保留。

## 2026-10-23 基线收敛

`cap-experiments-20261023.bundle` 随Git保存，包含旧30FPS和本次复测的独立提交。它是以main历史为前提的增量bundle；正常克隆本仓库后可恢复：

```sh
git bundle verify archives/cap-experiments-20261023.bundle
git fetch archives/cap-experiments-20261023.bundle refs/heads/codex/cap-30fps:refs/heads/codex/recovered-cap-30fps refs/heads/codex/cap-30fps-recheck:refs/heads/codex/recovered-cap-recheck
```

`interaction-evidence-20261023.tar.gz` 仅本地保留，包含10月13日两批证据的451份完整原文件，包括失败样本。所有成员与归档本身的SHA256见 `evidence/baseline-save-20261023/archive-manifest.json`。原始证据同时留在原位置，忽略文件阻止重复提交大体积采样；Git只保留报告、汇总和关键截图。

恢复原始证据到项目根目录：

```sh
tar -xzf archives/interaction-evidence-20261023.tar.gz
```

实验的node_modules软链接及可重建构建缓存不属于恢复内容；源码、工具、实验结果与历史提交已保存。清理缓存时保留archives目录。

本次10月23日的新连续截图完整保存在本地 `baseline-smoke-20261023.tar.gz`，清单同样记录在archive-manifest.json。Git只保留全景、开书与创建后的关键帧；恢复使用 `tar -xzf archives/baseline-smoke-20261023.tar.gz`。
