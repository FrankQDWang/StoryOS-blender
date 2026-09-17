# MPFB2 后台生成真人比例基础手臂：实现资料

日期：2026-09-17。范围：官方源码和脚本样例核查；不安装、不改运行代码、不制作开书动画。本次读取项目内 `downloads/mpfb2`，固定官方提交 `817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5`。下列链接固定到此提交，避免 `master` 后续变化影响行号。

## 最短可用路径

采用 **基础人体 → 成年男性宏观比例 → default 骨骼与原始权重 → 后续裁切手臂**。MPFB 自带的基础人体、形变目标、骨骼和权重足够完成这一步，不需要购买资产、MakeHuman 联机服务、自动权重求解或 Rigify。[基础网格加载源码 L791–816](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/objectservice.py#L791-L816)、[创建人体源码 L1485–1549](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/humanservice.py#L1485-L1549)、[骨骼及权重加载源码 L1552–1624](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/humanservice.py#L1552-L1624)。

以下片段的前提是 MPFB 已在本次 Blender 进程完成注册；可用项目内 `src` 加入 `sys.path` 后的普通 `mpfb` 导入名。

```python
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService

macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, age=0.5, muscle=0.5, weight=0.5,
             proportions=0.5, height=0.5)

body = HumanService.create_human(
    mask_helpers=True,
    detailed_helpers=True,
    extra_vertex_groups=True,
    feet_on_ground=True,
    scale=0.1,
    macro_detail_dict=macro,
)
rig = HumanService.add_builtin_rig(body, "default", import_weights=True)
assert body.parent == rig
assert any(m.type == "ARMATURE" and m.object == rig for m in body.modifiers)
```

`gender=1.0` 是男性，`0.0` 是女性；官方旧样例中的女性注释与实际数据定义不一致，不应照抄注释。`age=0.5` 是 `young` 锚点，不能说成精确年龄。其它宏观值保持默认中性；种族混合沿用默认参数，没有为本任务擅选人种。[gender 定义](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/entities/objectproperties/humanproperties/gender.json#L4)、[age 定义](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/entities/objectproperties/humanproperties/age.json#L4)、[默认宏观参数 L839–863](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/targetservice.py#L839-L863)。

`add_builtin_rig` 自动按当前人体拟合骨骼，设置父子关系，加载相应 JSON 权重，加入 Armature modifier。官方样例和测试也使用相同两步调用。[官方 default 示例 L23–39](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/script_samples/03_adding_a_default_rig.py#L23-L39)、[官方测试 L104–112](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/test/tests/bbb_services/humanservice_test.py#L104-L112)。

## 项目隔离与本次验证边界

MPFB 的 `LocationService` 在读取用户目录覆盖配置前，先调用 `bpy.utils.extension_path_user(__package__)`。因此普通 `sys.path` 导入与正式 Blender extension 安装不是完全相同的初始化方式，不能只给一个 `import mpfb` 就声称后台可运行。[目录服务 L26–60](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/locationservice.py#L26-L60)。

主代理已回报本项目的最短调用链实际成功：在**单个 Blender 后台进程**内临时将 `extension_path_user` 指向项目 `downloads/mpfb-user`，同时用项目路径的 `BLENDER_USER_RESOURCES` 隔离 Blender 用户资源；没有修改系统安装或保存用户 preferences。生成的基础对象有 19,158 个顶点、163 根骨骼，基础 `.blend` 与记录 JSON 已在 `downloads`。这是主代理的执行结果，本研究代理未重复运行。基础人体生成成功仅证明 API、形变和蒙皮链可用，不证明裁切后的手形、材质、关节变形或开书动作已通过视觉验收。

`mask_helpers=True` 创建的是隐藏辅助几何的 MASK modifier，不是立即物理删除辅助顶点；上述原始顶点数不能直接作为最终手部成本。裁切前须区分 `body` 与 helpers，并保留原来的手部拓扑、骨骼权重和需要的父级骨骼。[MASK 源码 L1535–1539](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/humanservice.py#L1535-L1539)。

## 手形、素材与可选 Rigify

先保留官方成年男性默认手形。必要时再在建骨骼前使用 `TargetService.load_target(body, full_path, weight=...)`；此服务支持 `.target.gz`，并生成对应 shape key。核心 `hands` 目录已包含左右手大小、手指长度、粗细、间距、位置及腕围目标；没有必要重新生成简化指头。具体权重应由实际视觉检查决定，不能把随意调参当作解剖改进。[load_target L778–828](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/targetservice.py#L778-L828)、[官方手形目标目录](https://github.com/makehumancommunity/mpfb2/tree/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/data/targets/hands)。

最少所需核心资产随官方源码位于 `src/mpfb/data/`：`3dobjs/base.obj`、`mesh_metadata` 的基础顶点组、宏观/手部 `targets`、`rigs/standard/rig.default.json` 与 `weights.default.json`。皮肤贴图不是上面最短生成链的必要条件；若采用官方 `.mhmat` 皮肤，官方样例另要求 `makehuman_system_assets` 资产包，并通过 `AssetService.find_asset_absolute_path(..., asset_subdir="skins")` 与 `HumanService.set_character_skin(...)` 装入。实际皮肤选择、许可记录和网页材质适配由主代理另验。[核心数据目录](https://github.com/makehumancommunity/mpfb2/tree/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/data)、[官方皮肤样例 L24–42](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/script_samples/05_setting_skin.py#L24-L42)。

当前标准预设为 `default`、`default_no_toes`、`cmu_mb`、`game_engine`、`game_engine_with_breast`、`mixamo`、`mixamo_unity`、`openpose`；不要直接传入未列出的 `mhx` 名称。`default` 是这次最直接且已经回报实跑成功的路径。[官方预设目录](https://github.com/makehumancommunity/mpfb2/tree/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/data/rigs/standard)。

若后续需要控制器式动画制作，官方 Rigify 调用如下；前提是 Rigify 已可用。这条分支本次没有运行，也不作为当前手形实验的依赖。

```python
from mpfb.services.rigservice import RigService
from mpfb.services.systemservice import SystemService

assert SystemService.check_for_rigify()
# 在另一个尚未加 default rig 的 body 上使用此分支。
metarig = HumanService.add_builtin_rig(body, "rigify.human")
rig = RigService.generate_rigify_rig(metarig, meta_rig_action="delete")
assert rig is not None
```

生成服务负责选择 metarig、检查有效性、调用 Rigify、调整子物体和设置元数据；此 API 不是现成开书动画，也不消除网页导出前烘焙实际变形骨骼动画的工作。[官方 Rigify 示例 L23–55](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/script_samples/04_adding_and_generating_rigify.py#L23-L55)、[生成服务 L1071–1147](https://github.com/makehumancommunity/mpfb2/blob/817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5/src/mpfb/services/rigservice.py#L1071-L1147)。
