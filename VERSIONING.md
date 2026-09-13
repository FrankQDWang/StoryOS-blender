# 小样的版本管理

用户已实际体验并认可当前小样，要求保留它作为 baseline，再基于它调整。

## 当前约定

| 对象 | 含义 |
| --- | --- |
| `v0.1.0-baseline` | 第一个已认可小样的附注标签；不移动、不覆盖、不在原提交上 amend |
| `main` | 最近一次认可的版本；初始化时指向 baseline，后续可向前演进 |
| `iteration/next` | 基于 baseline 的 v0.2 生活感布局与接触修正，等待实际画面评审 |
| `v0.2.0-preview.1` | 当前可运行预览快照，尚未经用户审美认可，不合入 main |
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

1. 从已认可版本建立一个有具体目的的分支；本轮先使用 `iteration/next`。
2. 将代码、制作脚本、需要更新的 `.blend`/GLB/纹理一起提交，保持源资产和运行资产对应；生成脚本会覆盖输出，手工 Blender 修改先另存。
3. 按变更范围做 Chrome 验收并保留关键画面。已经与调整无关的测试不必反复跑。
4. 用户认可后合入 `main` 并打下一个附注标签；baseline 标签一直保留。

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

用户明确选择公开 GitHub 仓库：[https://github.com/FrankQDWang/StoryOS-blender](https://github.com/FrankQDWang/StoryOS-blender)，远程名 `origin`，默认分支 `main`。`main`、`iteration/next` 与 `v0.1.0-baseline` 保存在远程；后续里程碑标签需要显式推送。GitHub 仓库公开不等于已经部署可在线访问的网页。

参考：[Git 标签](https://git-scm.com/docs/git-tag)、[Git worktree](https://git-scm.com/docs/git-worktree)、[Git LFS](https://git-lfs.com/)。

## v0.2 对照运行

当前 `4173` 为新版本，`4175` 为固定的 `v0.1.0-baseline` worktree。两个 worktree 分别安装本地依赖；不共享 `node_modules/.vite` 缓存，以免两个开发服务反复覆盖依赖预构建。两处预览均是本机服务。
