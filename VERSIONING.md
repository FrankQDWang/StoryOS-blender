# 小样的版本管理

用户已实际体验并认可当前小样，要求保留它作为 baseline，再基于它调整。

## 当前约定

| 对象 | 含义 |
| --- | --- |
| `v0.1.0-baseline` | 第一个已认可小样的附注标签；不移动、不覆盖、不在原提交上 amend |
| `main` | 用户认可的当前版本；2026-09-17已将0.1.4-preview.2经PR #1合入本地及远端同步主分支，成果提交4b00539、合并提交3ee0af0 |
| 迭代分支 | 旧迭代已合入并删除；当前codex/wrist-motion-step的preview.4已获认可，正在按授权提交、push并合入main；完成后清理迭代分支 |
| `v0.2.0-preview.1` | 已被用户否定的第二版预览，仅为历史标签；其后通过新提交恢复，当前main不采用该版本画面 |
| `v0.1.1-preview.1` | 第一版恢复 + 壁炉结构修复，保留为历史 |
| 后续标签，如 `v0.2.0` | 每轮体验确认后的完整里程碑；不是每次小改都打标签 |

标签约定由协作流程遵守；本地 Git 本身并未提供禁止强制移动标签的服务端保护。

当前采用普通 Git，不引入 Git LFS。首次快照约 60 MB，最大文件约 6.4 MB，这个规模可以直接保存完整资产。以后如果频繁修改大模型/高分辨率纹理导致仓库明显增长，再评估 LFS；不要为迁移存储方式擅自重写已认可历史。

## 保存哪些内容

- 前端、领域规则、测试、制作脚本、依赖锁文件和运行配置。
- `.blend`、实际运行的 `.glb` 和纹理。即使以后 Blender 的导出结果变化，仍能取回当时真正展示的模型。
- 方案、素材来源、参考研究与关键截图；拒绝过的研究方案继续标记为历史，不能因入库而当作新目标。
- `assets/manifest.json` 的资产哈希与版本记录。

不保存 `node_modules`、构建目录、缓存、下载暂存、Blender 自动备份文件、临时对比工作目录和 `.env`。依赖通过锁文件重新安装。

**浏览器 localStorage 不属于 Git 文件。** 本标签保留代码里的三本初始示例；用户在浏览器里新建的书和设置仍留在对应 origin 中，Git 切换不会替这些数据做备份或回滚。

## 每轮调整

1. 从已认可的main建立一个有具体目的的codex/分支。
2. 将代码、制作脚本、需要更新的 `.blend`/GLB/纹理一起提交，保持源资产和运行资产对应；生成脚本会覆盖输出，手工 Blender 修改先另存。
3. 按变更范围做 Chrome 验收并保留关键画面。已经与调整无关的测试不必反复跑。
4. 用户认可后按当次授权保存。2026-09-17已授权将0.1.4-preview.2提交、推送并通过PR合入main，再删除本地/远端迭代分支，仅保留同步的main；已有标签保持，不额外创建新标签。本次保存不代表部署网站。

## 看差异与打开旧版

只查看当前迭代相对 baseline 的文件差异：

```sh
git diff --stat v0.1.0-baseline...HEAD
git log --oneline --decorate --all
```

需要运行旧版对比时，用独立 worktree，避免切换当前正在修改的目录。以下路径保留在本项目内，已加入忽略规则；仅按需执行：

```sh
git worktree add --detach .worktrees/baseline v0.1.0-baseline
npm --prefix .worktrees/baseline/apps/web ci
npm --prefix .worktrees/baseline/apps/web run dev -- --host 127.0.0.1 --port 4175 --strictPort
```

旧版在 `http://127.0.0.1:4175/`；当前预览使用 `4173`。两端口的浏览器数据各自独立，适合用初始示例对比画面和操作。结束后先停止旧版服务，再用 `git worktree remove .worktrees/baseline` 清理；不使用强制清理忽略其中的改动。

用户明确选择公开 GitHub 仓库：[https://github.com/FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)，远程名 `origin`，默认分支 `main`。本次收尾后，本地及远端仅保留main分支；既有远端标签保留。后续里程碑标签需要显式推送。GitHub 仓库公开不等于已经部署可在线访问的网页。

参考：[Git 标签](https://git-scm.com/docs/git-tag)、[Git worktree](https://git-scm.com/docs/git-worktree)、[Git LFS](https://git-lfs.com/)。

## 当前对照运行

当前 `4173` 为基于已保存 `0.1.4-preview.2` 的人体尺寸与侧边夹持改进 `0.1.4-preview.4`，用户已认可并授权保存，正在从 `codex/wrist-motion-step` 合入main，交接见PLAN。需要对照时，`4175` 使用固定的 `v0.1.0-baseline` worktree。两个 worktree 分别安装本地依赖；不共享 `node_modules/.vite` 缓存，以免两个开发服务反复覆盖依赖预构建。两处预览均是本机服务。
