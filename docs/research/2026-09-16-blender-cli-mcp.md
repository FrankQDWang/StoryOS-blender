# Blender CLI 与 MCP 调研

调研日期：2026-09-16。资料核验范围为官方手册、项目维护者的 GitHub README，以及本仓库现有脚本。第三方能力均为 README 声明；本轮没有安装第三方工具、连接 MCP、执行建模或验证兼容性。

## 结论

Blender 自带官方命令行，本项目已经在使用。若要让 Agent 操作打开的 Blender 场景，可进一步评估社区 MCP；若要统一无界面任务的 JSON 输出，可评估社区 CLI 包装层。建议保留现有官方 CLI 制作链，将 MCP 作为交互迭代的补充。此建议是针对本项目的判断，不是第三方工具实测结论。

| 方案 | 已查到的能力 | 使用方式与适合场景 | 来源 |
| --- | --- | --- | --- |
| Blender 官方 CLI | 后台运行、执行 Python 脚本、命令行渲染 | 直接调用 Blender 可执行文件，配合 `bpy`；适合可重复构建与导出 | [官方命令行入口](https://docs.blender.org/manual/en/4.5/advanced/command_line/index.html)、[官方渲染说明](https://docs.blender.org/manual/en/5.1/advanced/command_line/render.html)、[官方 Python 参考中的脚本示例](https://docs.blender.org/api/blender_python_api_2_61_release/blender_python_reference_2_61_release.pdf) |
| `ahujasid/blender-mcp`（MCP for Blender） | 查询场景、创建/修改对象与材质、执行 Python、GLB/FBX 导出；有素材与模型生成服务集成 | Blender 插件中的 socket 服务连接 Python MCP server；适合与当前场景交互。明确属于第三方集成 | [维护者仓库](https://github.com/ahujasid/blender-mcp) |
| `renezander030/blender-cli` | `doctor`、`scene`、`exec/run`、`render`、`export`、`verify`、多视图 `snapshot`；结构化 JSON 输出 | 基于 Node.js 的社区包装层，每次启动 `blender --background`；不需要 MCP 或 Blender 插件 | [维护者仓库](https://github.com/renezander030/blender-cli) |

官方 latest/4.5 参数详情页本轮抓取失败，因此官方资料引用使用可检索到的文档入口、5.1 渲染页及旧版 Python 参考。旧版参考只用于证明后台 Python 调用方式，不作为当前 `bpy` API 兼容性依据。

## 当前项目已经使用什么

本轮实际执行 `blender --version`，确认 `/opt/homebrew/bin/blender` 为 **5.2.1 LTS**；`blender --help` 确认后台、Python 脚本与异常退出码参数存在。没有执行资产构建。

本地 `package.json:9` 的 `assets` 脚本已包含：

```sh
blender --background --factory-startup --python-exit-code 1 --python scripts/build_library.py
```

其后执行 `python3 scripts/asset_manifest.py`。`scripts/check_scene.py` 也记录了同样的后台调用模式。因此无需新增 CLI 工具，就能继续现有脚本制作与场景检查链。本轮只读取命令与代码，未重新运行资产构建。

## 第三方选型的实际区别

- **MCP for Blender**：需要同时配置客户端 MCP server 与 Blender 插件。README 要求 Blender 3.0+、Python 3.10+，推荐 `uv`；这些是声明的最低要求，不等同于本机版本已经通过验证。若接入，先验证场景查询、对象调整与导出这个最小闭环。[来源](https://github.com/ahujasid/blender-mcp)
- **MCP 数据选项**：README 表明遥测默认开启，可通过 `DISABLE_TELEMETRY=true` 关闭；采集数据可能用于研究与模型训练，接入前应明确采用的设置。[来源](https://github.com/ahujasid/blender-mcp#telemetry-control)
- **社区 blender-cli**：要求本机 Blender 与 Node.js 18+。README 的当前版本测试矩阵为 Blender 5.1.1；其他版本不能直接视为已验证。它适合希望获得 JSON 场景状态、预览与批量导出的流程。其可选 Meshy 生成命令另需 API key。[来源](https://github.com/renezander030/blender-cli)
- **对本项目的建议**：优先保留已存在的 `build_library.py` 与统一 `room-layout.json`。若新增 MCP，交互修改仍应回写制作脚本或布局源，避免下一次 CLI 构建覆盖手工场景修改。无需为了“有 CLI”而替换现有生产资产链。

本轮未变更应用、场景资产、MCP 配置、分支或标签。
