# preview.6 认可后的保存验证

2026-09-17。用户认可当前效果并授权提交、推送、通过PR合入main，删除本地/远端迭代分支，最终只保留同步的main。

- `before-save.json`：保存前87份代码/资产/选图文件哈希、Git标签和5个worktree的HEAD与状态；四个历史worktree均为detached，保存流程不清理它们。
- `precommit-parity.json`：批准的运行代码与资产未漂移；唯一变化是round-07的README更新认可状态。
- `tests.log`：保存前重新运行14项测试，通过。
- `build.log`：保存前生产构建通过，既有大分块提示保持。
- `assets.log`：15项manifest、20份来源文件、4张服装纹理和13份public生产产物一致性通过。

六张第三方服装参考原图留在本机原位置并精确忽略，来源、哈希和研究文字入库。现有选图、源模型、原创纹理、各轮验证以及被拒方案的历史证据完整保存。本轮不再调整用户已认可画面。

## 保存结果

[PR #3](https://github.com/FrankQDWang/StoryOS-blender/pull/3)已合并；成果提交`e4c64343b5c85fdadf8da407dc03ea92480d94a0`，合并提交`cf30f17b73f3eb4a390a4910e9fd63acd5fbe9ea`。本地与远端`codex/midnight-mage-hands`均已删除，只有main，三方SHA相同、ahead/behind为0/0、根工作区干净。三个历史标签与四个detached worktree的HEAD/草稿状态保持。

`pr-before-merge.json`、`pr-merged.json`是实际GitHub返回；没有仓库Actions工作流，Sourcery因650文件超过API限制而SKIPPED，不称远端审查通过。`merge-and-cleanup.json`是合并、同步、删除分支后且收尾文档提交前的快照；本README与PLAN随后在main保存并再次push，最终状态以Git引用为准，避免文件自引用其所属提交SHA。
