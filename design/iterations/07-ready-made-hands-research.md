# 现成手部资源与动作替换研究

> 2026-09-17 实验更新：已采用免费的 MakeHuman/MPFB 核心人体与原始权重、Mindfront Aksel CC0皮肤，导出 `makehuman-hands.glb`。下载无需登录或付费；开书动作是项目适配的烘焙动作，并非下载到的现成开书包。实际Chrome验证、修正及边界见 `design-qa.md` 最新节；固定版本、许可和文件见 `assets/vendor/makehuman/README.md` 与 `assets/source/makehuman-hands.json`。下方候选研究保留为历史，不再代表尚未选定。


2026-09-17。用户否定 0.1.4-preview.1 的自制双手：外形不像人、动作不符合人类动作并产生恐怖感。火焰有改善，明确先不继续调整。**手部视觉验收失败；撤回上一轮手部自检通过及没有剩余严重视觉问题的判断。** 本文是资源筛选，不是替换实现或用户选型确认。

## 最新方向：只考虑免费或开源

用户随后明确认为付费价格偏贵，要求免费或开源。下面付费推荐保留为历史，不再是当前采购方向；没有购买预算或购买任务。

- **现成手模型**：[SparrowHawk Hands Rigged](https://blendswap.com/blend/22269) 为免费 CC0，带 Blender 源文件和骨骼。2026-09-17 Chrome 实际点击 Download 后，文件页要求登录才能下载；证据 `evidence/ready-made-hands-20260917/blendswap-download-login.png`。未登录、创建账号或下载模型。需补皮肤材质、统一双手形态并制作动作。
- **开源人体模型路线**：[MakeHuman / MPFB](https://static.makehumancommunity.org/mpfb/about.html) 免费开源，MPFB 可在 Blender 内生成现有人体网格、自动绑定，支持 Rigify、IK/FK。按[官方许可](https://static.makehumancommunity.org/about/license.html)，核心图形资产为 CC0，MPFB 程序代码为 GPL、MakeHuman 代码为 AGPL；不能把软件代码许可证误套在输出模型上。[导出许可说明](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md)明确核心资产的修改、导出和部件复用可用，第三方另加素材仍逐项核查。可从完整人物取手臂，后续身体/脚也可同源；这是实施建议，尚未安装、导出或在本项目视觉验收。
- MakeHuman 的 [hands01](https://static.makehumancommunity.org/assets/assetpacks/hands01.html) 是手形修正 targets 集合，页面逐项标 CC0；不是独立手模型或开书动作包，不能误当可直接播放的动画。
- **轻量开源手模型**：[WebXR Input Profiles generic-hand](https://github.com/immersive-web/webxr-input-profiles/tree/main/packages/assets/profiles/generic-hand) 的资产专属 README/LICENSE 明确采用 MIT，保留版权许可可修改和再分发；GLB 结构实查每手约 94 KB、2,314 三角形、25 个蒙皮关节，无贴图或动作，关节平级排列。它是可直接获取的免费模型，但离线开书需要适配控制骨架或逐关节烘焙；未做视觉或实际导入验收。固定版本、哈希和来源见 [开源手模型核查](../reference-library/ready-made-hands/open-hand-assets.md)。
- 新检索到 [3DHaupt Rigged Hands](https://3dhaupt.com/3d-model-anatomy-rigged-hands-low-poly-vr-ar-game-ready-blender/) 虽免费，作者明确只供非商业/教育用途，不作为本项目主选。其他付费包和仅供个人使用的免费模型不再扩展。

免费现成模型路线成立；尚未确认免费的“自然双手＋闭书到打开全过程”完整动画包。下一步在免费候选里比较手形/绑定，先完成一个书位的自然开书样片。没有因免费降低视觉门槛；本轮仍为研究，没有替换当前运行手部。

## 结论与建议

现成真人比例、可绑定动画的双手确实存在，不应继续以当前程序生成手作为造型基础。模型和动作需要分别解决：现版 `OpeningHands.jsx` 仍让整只手跟着封面角度转、各指使用相似的弯曲曲线，没有可信的捏住、承重、松开过程。仅替换网格仍会保留动作问题。

找到的最接近配套成品包含手、书和翻页动作，但尚未确认闭书到打开的完整动作、可用导出及网页发布许可。**当前没有经过实际导入和连续动作验收的即插即用完整包。** 不把商品标注 rigged、animated 或静态漂亮图片当作我们的动作验收。

建议以真人比例现成模型替换自制造型；先做一个书位的完整近景样片，按真实开书参考制作或适配手、封面、书页的共同动画，验证正常速度和慢放，再推广五台。付费资源需要预算及与公开资产仓库匹配的许可；本轮没有购买或联系卖家。

## 优先候选

| 资源 | 官方列明的交付 | 当前判断 |
| --- | --- | --- |
| [Male Hands Rigged — sarojit / CGTrader](https://www.cgtrader.com/3d-models/character/man/male-hands-rigged) | 真人比例双手，Blender 源文件、FBX 和 glTF 均含变形骨骼；4,793 个四边面，五类 4K 贴图。Chrome 实页促销 US$39.60，原 US$99；Royalty Free (no AI)。没有列开书动作。 | **接入格式最合适的付费模型候选**。已目视第 1、4 张：掌指比例、拇指根部和指甲比现版可信；仍需检验关节变形、灯光和动作。不能由商品图保证落地质量。 |
| [Hands Rigged — SparrowHawk / BlendSwap](https://blendswap.com/blend/22269) | 免费 CC0；Blender 2.7x，8.83 MB，有骨骼。无纹理，作者明确左手偏女性、右手偏男性，需自行摆姿。 | **公开仓库方向的免费备选**。已目视作者预览，具有正常手形基础；需统一双手形态、制作皮肤材质、迁移旧版绑定及另做动作，不能称为现成完整方案。 |
| [Book with Male Hands Set Animated Rigged For Maya — 3dmi](https://www.cgtrader.com/3d-models/sports/book/book-with-male-hands-set-animated-rigged-for-maya) | 手、袖口、书，两段非循环翻页/检索动作，最长各 8 秒，30 fps。Chrome 实页 US$148.85，原 US$229；只列 Maya .ma，161 MB。 | **最贴近手书配套的候选，但不建议仅凭商品图购买**。从已打开的书开始；完整开书、FBX/GLB、连续动作自然度及当前网页交付许可未核实。 |

价格是检索时页面显示，未进入结账，不能作为后续价格保证。没有获取上述模型源文件，所有面数、大小、格式均为作者说明，未实测。

## 许可的实际影响

本项目为公开 GitHub 仓库，现有流程会把源模型及独立 GLB 一起提交。这与普通商业游戏只分发整合产品不同。[CGTrader 条款 21A/21B](https://www.cgtrader.com/pages/terms-and-conditions) 不能据 Royalty Free 标志推定允许公开再分发独立素材；no AI 附加限制针对机器学习/训练。付费候选必须先确认适合当前交付方式的许可，不通过压缩/改扩展名假装解决。免费 CC0 候选在再分发安排上更直接。

配套动作、其他阅读动捕及 [TurboSquid 许可](https://www.turbosquid.com/licensing) 的具体核查见 [动画资源研究](../reference-library/ready-made-hands/animation-sources.md)。未联系任何卖家。

## 未列为主推荐

- [Stylized Male Hands / ArtStation](https://www.artstation.com/marketplace/p/xK6Yj/stylized-male-hands)：US$4，Blender/FBX 骨骼与测试动作，每手 2,312 三角形；没有列开书动作。Chrome 商品图未成功显示，因此没有作手形质量判断；标准许可也不能直接当公开素材许可。
- [WRAD ARMS](https://wriks.itch.io/wrad-arms)：免费 CC0，但作者定位为复古 Half-Life/低面数 FPS 美术，不能仅因轻量就替代本次近景自然手目标。
- [anatomical-hand-model](https://github.com/emmalieker/anatomical-hand-model)：标注 CC BY-NC，不作为产品手部素材主路线。

## 视觉证据与下次验收

实际 Chrome 截图在 `evidence/ready-made-hands-20260917/`：

- `sarojit-male-hands-preview.png`：第 1 张、实时价格和许可标签。
- `sarojit-male-hands-grip.png`：第 4 张姿势，静态形体检查。
- `blendswap-cc0-preview.png`：作者手形预览及 CC0 标记。
- `artstation-stylized-preview.png`：记录图片没有载入，不能充当模型视觉证据。

这些是第三方商品页截图，只作研究引用，不是下载的模型、运行资产或新的选定效果图。没有 ImageGen 产物。配套手书包及全身动捕的演示观察详见动画研究；未把远景全身演示视作手指接触验收。

下一轮门槛：

1. 静态近景先通过：五指和拇指方向正确、指长与掌宽可信、腕部过渡正常，弯曲时无塌陷或橡皮感。
2. 真实动作逻辑：稳定书本→捏住封面边缘→抬起→放下→松手。手腕与指尖接触共同检查，不能整手机械贴着封面转。
3. 正常速度连续播放、慢放和多个中间帧一起评审；无漂移、穿插、突然换姿或反向关节。仅关键帧和构建通过不足以通过验收。
4. 一个书位局部样片满意后再推广五台，保持已认可房间、五位、Quick Access、跳过及低动态流程；录取实际 Chrome 截图和连续动作证据。
5. 资源优化以导入后实测为准；现有候选面数不等于已验证性能，4K 贴图也不直接全量用于网页。

本轮只进行了检索、作者页面目视和状态修正；火焰、房间及运行中的未通过手部资产保持原样，未重新建模、修改动作、安装工具、购买、提交或推送。
