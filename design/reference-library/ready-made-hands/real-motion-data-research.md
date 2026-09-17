# 真实手—书交互动作数据核查

日期：2026-09-17。针对用户再次否定右手开书动作的反馈，核查已有真实运动数据，而非继续寻找手模型。已读当前 `PLAN.md`；本轮只读官方项目、作者仓库、数据卡和许可，未注册、接受协议、下载动作数据或修改运行代码。下列“可用”特指是否适合本项目公开 GitHub / 浏览器 GLB 分发，不等同于研究者可免费下载。

## 结论

**本轮没有找到已经核实能直接使用的、免费且许可兼容的 Blender 手臂开书成品动画。** 真实三维参考确实存在：ARCTIC 的 notebook 铰接交互最贴近封面翻转，但禁止无授权再分发；GigaHands 明确包含开书文本任务，允许非商业改编/分发，仍需确认具体序列与完成动作适配；OakInk2 数据许可最宽松，但本轮未确认有书本动作。不能把“论文有手”“代码公开”“网站 CC 许可”当作可发布的开书资产。

| 来源 | 书本动作证据 | 三维时序与 Blender 可用性 | 公开 GLB 的判断 |
| --- | --- | --- | --- |
| **ARCTIC** | 官方论文补充材料明确列 `Notebook`，包含 use 与 grasp；项目以开书为铰接交互例子。不是仅有泛用抓握 | MANO 双手、SMPL-X 身体、物体整体位姿及一维铰接角；需导入与重定向，非现成 FBX | **当前许可不允许直接分发**，即便非商业网页也不能直接假定获准 |
| **GRAB** | 未核实书本序列；其物体表示明确为刚体，不能提供封面相对书身的铰接运动 | 120 FPS，全身/独立左右手参数、物体轨迹和接触；需 MANO/SMPL-X 与转换 | **当前许可不允许直接分发**；也不适合作为封面开合的首选 |
| **OakInk2** | 未在已读官方页面、数据格式和论文信息中确认 book/open-book 片段，不等于证明整个数据集不存在 | 双手 MANO、上身 SMPL-X、各物体/部件矩阵及多视角；有作者 Blender 渲染工具 | 作者**数据卡**是 CC BY-SA 4.0；数据改编可有条件分享，但第三方 MANO/SMPL-X 模型另受许可约束，不能连模型一起直接导出 |
| **H2O**（补充） | 官方标签明确 `grab book`、`place book`、`read book`；未单列 open-book，不把 read 自动当完整闭书→开书 | 双手 21 点与 MANO、物体 6D、四外部视角+一第一人称；书体没有独立封面角字段 | ETH 条款只允许学术用途，禁止交给第三方，**不选为公开资产** |
| **GigaHands**（补充） | 论文图 5 的 GigaHands 测试文本包括 “Open the book to page 200”；图中是生成结果，**不是已查看真实源片段** | 已发布三维手点、MANO 参数、多视角视频及部分物体 6D；未核实该书片段 ID、完整封面轨迹或 Blender 导出 | CC BY-NC 4.0；可作为**非商业研究/原型候选**，不能覆盖后续商业 StoryOS 用途；模型许可仍需单独处理 |
| **BlendSwap Book Rig (Full)** | 作者只声称书本/书页动画，没有真人手或手书配合 | 原生 `.blend`，12 页、6 页已动画，老版 2.7x 且使用脚本 driver | CC-BY，但只解决书本机械结构，**不解决当前右手动作** |

上述表格依据分别见下方一手来源；许可判断是针对当前发布方式的保守实施筛选，不把动作重定向视为自动解除源数据许可。

## ARCTIC：参考价值最高，部署许可不满足

[官方项目](https://arctic.is.tue.mpg.de/)明确研究同步的双手—铰接物体运动；[作者补充材料，表 2](https://pure.uva.nl/ws/files/163521335/Fan_ARCTIC_A_Dataset_CVPR_2023_supplemental.pdf)列出 Notebook 的 use/grasp 数据。可据此确认不是“开书”只出现在泛泛背景中的数据集。但本轮没有打开具体 notebook 真实序列，不能评价它是否与当前立式书台角度、握持方法或右手角色一致。

[官方数据格式](https://github.com/zc-alexfan/arctic/blob/master/docs/data/data_doc.md)提供逐帧左右 MANO 旋转/45 维手指姿态/平移、SMPL-X 姿态、物体 7 维参数（1 个铰接角、3 个整体旋转、3 个平移）；物体模板分 top/bottom。此表示能研究抬封面时的手指—掌—肘联动，但不意味着含独立纸页弯曲。[下载说明](https://github.com/zc-alexfan/arctic/blob/master/docs/data/README.md)要求 ARCTIC、MANO、SMPL-X 账号；原始参数 215 MB、meta 91 MB，做运动分析不必下载全部 649 GB 图像。上述大小为官方目录标注，未下载验证。

[真正的数据许可](https://arctic.is.tue.mpg.de/license.html)在 License Grant 与 No Distribution 中限制为非商业研究/教育/艺术，并禁止未经书面许可向第三方提供、复制或分发全部或部分数据。页脚 CC BY-SA 明确修饰 **website**，不能替换数据许可。因此不能直接把采样姿态或转换 GLB 放入公开仓库；本轮没有点击接受或下载。

## GRAB：真实全身接触，但缺少本题需要的铰接表示

[作者仓库 README 的 Contents of each sequence](https://github.com/otaheri/GRAB#contents-of-each-sequence)说明每条序列包含 body、lhand、rhand、object、table、contact；物体仅作刚体旋转和平移。这能提供真实抓握、拿放及全身协作参考，不能从该物体字段得到封面铰链运动。已查资料没有验证可直接用的书本开合序列，不建议为了当前单个开书问题先拉整包。

[官方入口](https://grab.is.tue.mpg.de/)要求注册并接受协议，另需 MANO/SMPL-X；[数据许可](https://grab.is.tue.mpg.de/license.html)禁止无书面许可向第三方分发，并有参与者逐项限制。因此它是研究数据，不是可直接发布的免费 mocap 商用包。

## OakInk2：数据许可可分享，但没有确认书动作

[官方项目](https://oakink.net/v2/)直接链接作者 [kelvin34501/OakInk-v2 数据卡](https://huggingface.co/datasets/kelvin34501/OakInk-v2)。本轮实际读取其 [README 原文](https://huggingface.co/datasets/kelvin34501/OakInk-v2/raw/main/README.md)，front matter 明确 `license: cc-by-sa-4.0`；这是数据集发布声明，不是网页模板声明。按 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，受此许可覆盖的数据允许改编和分发，须署名、说明修改，并按相同许可分享改编部分。

[官方工具说明](https://github.com/oakink/OakInk2#dataset-format)给出逐帧 `raw_mano`、`raw_smplx`、`obj_transf`；双手姿态使用 `[w,x,y,z]` 四元数，可作为重定向输入。下载至少需选定序列的图像与 preview 标注、物体包、program 包；文档未要求接受专门数据协议，实际大文件下载/是否限速未试。

[作者 Blender Tools](https://github.com/oakink/mocap_blender)用于论文渲染，说明基于 Blender 3.6.9、Python 3.10、数据 pickle、示例场景和脚本，并非带现成人体控制骨骼的开书 `.blend` 包。其当前公开树未看到独立 LICENSE 文件，本轮未将它称为许可已核实的 MIT/Apache 工具；工具可复用权限与数据卡许可不能混为一谈。

此外，[MANO 自身许可](https://mano.is.tue.mpg.de/license.html)限制第三方分发及商业用途。OakInk2 的数据卡不能为外部 MANO 模型授予新权限。若后续发现合适动作，应单独核实“仅动作参数/点位重定向到现有 CC0 MakeHuman 手”的产物许可，不能直接把 MANO 模型或其参数化模板烘焙导出后声称无限制。

## 两个有书动作的补充来源

**H2O。** [作者数据说明](https://github.com/taeinkwon/h2odataset)列出书本动作及双手点位/MANO 格式，[作者论文](https://openaccess.thecvf.com/content/ICCV2021/papers/Kwon_H2O_Two_Hands_Manipulating_Objects_for_First_Person_Interaction_Recognition_ICCV_2021_paper.pdf)确认第一人称和多视角采集。[ETH 注册与条款页](https://h2odataset.ethz.ch/)已实际读取：仅学术、不可商用、不可转交第三方；同意后由邮件给出 7 天有效凭据。本轮没有填写或接受。技术上可用于读书手势研究，但许可比本项目公开资产需要的更窄。

**GigaHands。** [作者论文图 5](https://openaccess.thecvf.com/content/CVPR2025/papers/Fu_GigaHands_A_Massive_Annotated_Dataset_of_Bimanual_Hand_Activities_CVPR_2025_paper.pdf)给出了开书测试文本；须明确该图显示的是文字生成动作，不是源动作质量证明。[作者仓库](https://github.com/brown-ivl/GigaHands)现已链接真实三维点、MANO 参数、多视角、物体位姿与示例数据。其 License 节明确 CC BY-NC 4.0，按[正式许可说明](https://creativecommons.org/licenses/by-nc/4.0/)可在署名及非商业条件下分享改编数据；比 ARCTIC 的禁止再分发宽松，但不是商业通用来源。访问使用 Globus 及作者直接链接，具体目标片段是否无需登录、大小和质量均未实测；没有启动下载。若以后专门开展研究，先查开书源片段和原始三角化手点，比先训练 text-to-motion 更直接；不需要为了复用已有动作训练模型。

## Blender-ready 免费来源的边界

有界搜索查到作者发布的 [Book Rig (Full) / nyxzimus](https://blendswap.com/blend/16962)：CC-BY、原生 Blender、封面和书页可动。它只有书本，不含真实手—封面配合，因此即使下载成功也不能解决此次问题。本轮没有验证该具体文件的登录下载、Blender 5.2 兼容性或脚本安全性，也未运行其 driver。没有用这个“有动画”搜索结果凑成“找到现成开书手”。

## 对当前项目的具体建议

1. **不要立即引入上述研究数据为正式 GLB。** 当前最相关的 ARCTIC 有许可障碍；可分享的 OakInk2 尚无确认的书动作；GigaHands 仍有非商业及具体片段边界。免费完整成品本轮未找到，不能对用户承诺“换包就好”。
2. **用真人可见动作验证整个接触链。** 主线程正在找真人参考；至少标记接近、指尖/拇指接触、封面离开书身、约中段交接/滑动、释放和退手。不要只再优化一个肘点，然后用腕夹角降低代替真人观感判断。
3. **若后续投入动作数据适配，先做一个短片段。** 按原始坐标/关节定义恢复双手与物体同步，重定向到已有 CC0 手，并针对当前书的厚度、书脊、阅读台角度重建接触约束，再烘焙。研究数据不是免调参动画；小小的尺寸差也会改变指尖接触，这是基于上述数据格式的实现推断，尚未实跑。

本轮未对当前右手作新的视觉通过判断。模型质量、动作可信度、许可与网页可用性分别记录，不能互相替代。

## 补充：免费视频转手部动画是否值得下一步尝试

**值得作为短片段的辅助实验，不适合直接替代真人参考和手书接触制作。** 建议先在现有真人参考上确定接触、释放等关键姿态，再考虑用离线检测提供可见手指的运动草稿；不建议把安装 BlendArMocap 作为下一步主线。

- **BlendArMocap：功能存在，维护已停止。** [作者仓库](https://github.com/cgtinker/BlendArMocap)明确支持摄像头或视频的手/身体/脸检测、将旋转结果转给骨骼，官方预设面向生成后的 Rigify；GPL-3.0-or-later。当前 `__init__.py` 声明插件 1.6.1、最低 Blender 3.0，但 README 已明确 `Discontinued`。这不能证明兼容本项目 Blender 5.2.1，更不能直接套上当前 MakeHuman 手骨架；需映射和烘焙。未安装验证。
- **直接 MediaPipe 离线检测更适合小实验。** [Google 官方 Python 指南](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python)支持视频文件逐帧输入、`VIDEO` 模式和时间戳，可设置检测双手，输出左右手类别与每手 21 点。其所谓 world landmarks 以**每只手自己的几何中心**为原点，并非已经标定到书台的共同世界坐标；它不输出封面铰链、接触力或可信的书面接触点。可以在 Blender 外运行后再导入点位，避免依赖老插件，但这只是可实施路径，本轮未实现。
- **许可与遮挡边界。** [MediaPipe 官方代码许可](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE)是 Apache-2.0；这不自动授予源视频版权，也不代表本轮已核实并下载具体模型包。宜用自拍或明确授权的素材。根据上述输入/输出设计，封面遮住拇指或指尖时，单目检测可能失跟、重新检测或给出不可靠估计；即便每帧仍有 21 点，也没有证明指尖贴在封面上。双手交叉、深度与整体移动仍需检查，不能据此宣称无误差动捕。

**实验收束条件（建议，未执行）**：只选一段短开书视频，先查看关键接触阶段的点位覆盖与连续性；若恰好在抬封面/释放处失真，就停止将其作为动作来源，回到真人逐姿态制作。工具可节省可见手指的初始标记工作，最终接触、隐藏关节、肘腕协作和动作节奏仍需要人工约束与视觉验收。本补查未安装工具、下载模型或改运行代码。
