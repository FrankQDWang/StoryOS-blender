# 免费 WebXR 双手 GLB 核查

日期：2026-09-17。仅研究官方上游，不操作浏览器、不购买、不安装、不修改运行代码。GLB 通过公开 raw URL 读入内存检查结构，未保存为项目运行资源；没有做 Blender 导入、视觉或性能验收。

## 可用候选及实际许可

**WebXR Input Profiles / `generic-hand` 左右手**是许可清晰、免注册的免费基础资源。来源是 [immersive-web/webxr-input-profiles](https://github.com/immersive-web/webxr-input-profiles)，不是第三方搬运站。

模型许可的依据并非仓库代码许可证推定：[assets 包 README](https://github.com/immersive-web/webxr-input-profiles/blob/main/packages/assets/README.md) 明确说明三维 assets 以 MIT 许可提供；它引用的 [assets/LICENSE.md](https://github.com/immersive-web/webxr-input-profiles/blob/main/packages/assets/LICENSE.md) 授予使用、修改、出版、分发等权利，要求随副本保留版权与完整许可通知。该文件版权行为 `Copyright (c) 2019 Amazon`。因此可把左右手及修改版本放进公开 GitHub、随 Three.js 网页分发，并保留上游许可；没有付费商店禁止独立素材再分发的相同限制。资产文档另提示设备商标不在许可范围内，本候选是 generic 手部。

不要把 glTF 的 `generator: Khronos glTF Blender I/O` 当作模型版权或“Khronos 制作”的证明：这只是导出器标识。模型直接来源以上述 immersive-web 资产包为准。

## 固定版本与实测结构

本次 API 查询显示 hand 目录最后一次变更为 [c5356912d0c3bc43c6db8aa3926d8951a7716449](https://github.com/immersive-web/webxr-input-profiles/commit/c5356912d0c3bc43c6db8aa3926d8951a7716449)，2022-12-02，说明为修正骨骼位置。以下数字来自读取该提交 GLB 的 JSON/accessor/skin，不是网页营销描述。

| 项目 | 左手 | 右手 |
|---|---:|---:|
| 文件 | [left.glb](https://raw.githubusercontent.com/immersive-web/webxr-input-profiles/c5356912d0c3bc43c6db8aa3926d8951a7716449/packages/assets/profiles/generic-hand/left.glb) | [right.glb](https://raw.githubusercontent.com/immersive-web/webxr-input-profiles/c5356912d0c3bc43c6db8aa3926d8951a7716449/packages/assets/profiles/generic-hand/right.glb) |
| 大小 | 94,572 bytes | 94,004 bytes |
| 顶点 / 三角 | 1,360 / 2,314 | 1,360 / 2,314 |
| 网格 / primitive / 材质 | 1 / 1 / 1 | 1 / 1 / 1 |
| 蒙皮关节 | 25 | 25 |
| 贴图 / 动画 | 0 / 0 | 0 / 0 |

两文件有 POSITION、NORMAL、TEXCOORD_0、JOINTS_0、WEIGHTS_0；均为普通 glTF 2.0，不需要压缩扩展。材质为中灰、非金属、roughness 约 0.553；**没有皮肤颜色、毛孔、指甲或法线贴图**。没有书、袖口配套或开书动画。

SHA-256：

```text
left.glb  bc67783144944ea1cda54d9247885825ea5fb9d4651469fe7d00be517a5c2b87
right.glb 291790c14f7f88a7f9bd35330c47392ed8e8d395ae6728f4bb7089f1bc1f2b96
```

## Three.js 使用方式及离线动画适配

[Three.js XRHandMeshModel 上游代码](https://github.com/mrdoob/three.js/blob/dev/examples/jsm/webxr/XRHandMeshModel.js) 默认从 WebXR Input Profiles CDN 的 `generic-hand/left.glb`、`right.glb` 加载，查找 SkinnedMesh，并按 WebXR 命名匹配 wrist 与各指关节；`updateMesh()` 根据跟踪关节复制 position、quaternion。这是 Three.js 已采用它作为骨骼手资产的直接证据。

**可以把网格用于普通桌面 Three.js，不需要头显才能显示或播放后来制作的动画。** 这项判断来自它是普通带蒙皮 GLB，而不是硬件专属封闭格式。但原有 XRHandMeshModel 更新机制读取控制器关节；不能把这个类直接加入当前开书流程就获得动作。

有一处重要适配成本：实查右手 25 个关节全部直接挂在 Armature 下，各指节没有通常的父子链。这便于 XR 每关节直接更新，却不是给动画师即用的手指 FK/IK 控制器。离线开书须在保持绑定姿势和权重正确的前提下增加控制骨架/父子链，或把完整逐关节位姿烘焙成 animation clip。只旋转掌指根关节不会自动带动后续独立关节。

## 选择建议与未验证边界

- **作为免费、可公开分发、轻量的骨骼手底稿：合适。** 双手合计 188,576 bytes、4,628 三角，源格式即 GLB，获取和许可阻力低。
- **作为本项目真人质感开书最终成品：目前不能确认。** 无皮肤贴图、无手书动作、没有动画制作控制 rig；人体造型、手指弯曲后的质量、镜头近景及接触仍要实际看。
- 主代理正在核对的 CC0 Blender 手或 MakeHuman/MPFB 若提供更完整的人体比例、手指控制链和材料，可能更适合近景制作；本记录没有检查那些资产，不作质量排名。

本轮没有宣称动画已自然、性能已达标或能直接替换已被用户否定的手。可在需要免登录的备用模型时使用本资源；最终动作仍必须以手、封面和页角共同接触为标准验收。
