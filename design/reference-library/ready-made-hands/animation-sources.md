# 现成手与书动作资源核查

核查日期：2026-09-17。范围：只研究可购买或下载的三维手臂与拿书、开书、翻页动作，不改房间、炉火、手模型或运行代码；未购买、未下载模型、未联系卖家。网页产品说明和售价会变化，以下区分卖家声明、实际目视结果与尚未验证内容。

## 结论

找到一套很接近需求的“真实外形双手＋书＋两段翻页动作”商业资源，但它仅列 Maya 源文件，且没有确认完整闭书→打开动作或适合当前 Three.js 发布方式的许可。因此它适合作为优先洽询对象，**还不是已验证的即插即用替换件**。另两类现成阅读动捕可减少人体动作工作，却没有证据证明包含第一人称精细手指和书页接触。本轮没有找到能够同时确认“真实手、完整开书、FBX/Blender、公开 WebGL 适用”的完整成品包。

## 候选比较

| 优先级 | 资源 | 已核实内容 | 未核实及限制 | 判断 |
|---|---|---|---|---|
| 1 | [Book with Male Hands Set Animated Rigged For Maya — 3dmi / 3d_molier](https://www.cgtrader.com/3d-models/sports/book/book-with-male-hands-set-animated-rigged-for-maya) | 作者列两段非循环动作：手动翻一两页并指读、快速检索成批书页；各最长 8 秒，30 fps。配手、袖口和书。Chrome 实页现价 **US$148.85**，原价 US$229；Royalty Free License **(no AI)**。源格式仅 `.ma`，161 MB；39,672 polygons，40,926 vertices；14 张 4K PNG。 | 没列 FBX/GLB/Blender。文字说与已打开的书互动，不能认定含从闭书掀封面。未取得可播放连续演示或源文件；未验证手指接触、导出后变形与性能。 | 最接近实际需求，先看完整视频并确认烘焙导出；不建议仅凭封面图购买。 |
| 2 | [Reading Animations — RBStudio / Fab](https://www.fab.com/listings/60ca91e9-f720-4882-b042-4c0c3c5b8aea) | 面向坐姿 NPC；Manny、Quinn 各 7 种风格，含读书、卷轴、报纸、坐下起身。Chrome 实页列 UE 5.0–5.5 Asset package、Windows/Mac、Fab 标准许可。 | 仅列 UE 格式，没有独立 FBX。不是第一人称专用手臂包，未证明书、纸页骨骼或手指捕捉一起交付。 | 动作参考/全身重定向备选，不能声称解决手书接触。 |
| 3 | [RPG Locomotion Animation Pack Mocap — Mocap Factory / Fab](https://www.fab.com/listings/891c4776-b02a-4380-9f8f-7f4b0f366db3) | 作者列 49 段动作，其中确有 `unarmed-read-book-start_FM`、`idle_FM`、`end_FM` 三段读书状态；仅列 Unreal Engine 格式。 | 未确认手指动作精度、道具动画、第一人称观感、FBX 交付或当前售价。动作名的 start 不等于已证明“手掀封面”。 | 只有在需要全身阅读状态时再评估；当前手部近景优先级低。 |

Fab 的价格受网页地区与档位影响。第二项 Chrome 实页显示个人/专业均 ¥3,119，当前浏览地区为日本；本记录不把该符号误写成人民币，也不换算为未经核验的美元价。第三项未操作价格选择器。

## 演示核查

- 第一项：在 Chrome 打开并目视检查画廊第 1、2 张图。可见合理的五指、指关节、指甲与袖口，手指正在触碰翻起页边或指读。这证明其静态外形比本项目程序拼装手更有可信基础；**不证明连续动作自然**。当前画廊标示 27 张媒体，已查看的 DOM 没有模型动作视频，仅图片；不能据此断言卖家完全没有视频。原作者也在 [TurboSquid 商品页](https://www.turbosquid.com/3d-models/3d-book-with-male-hands-set-animated-rigged-for-maya-model-2548093) 销售同名资源，但后续页面抓取不稳定。
- 第二项：[作者链接的 Reading 演示](https://www.youtube.com/watch?v=5AyOjE6v9wM) 已实际在 Chrome 播放并抽看开头和约 1:33。显示多名 UE 全身人偶坐姿动作，展示距离较远；该观察不足以评审指尖压页、捏页或封面接触。演示是全身动作展示，不能当作第一人称手部近景验收。
- 第三项：已确认商品页存在作者 Video 链接，但未播放，不能宣称已目视验证。

## 许可与公开网页边界

1. **CGTrader**：本商品 Chrome 实页是 Royalty Free License (no AI)。[官方条款 21B](https://www.cgtrader.com/pages/terms-and-conditions) 将其限制为相同 royalty-free 权利但禁止机器学习/训练用途；21A 要求作为 Incorporated Product 使用，并采取合理措施防止用户取得原资产。把转换后的独立 GLB 直接放进公开仓库/公开资源目录不能仅凭“royalty free”标签视为已获许可。应在购买前明确当前网页交付方式，取得匹配许可；本轮未联系卖家或平台。
2. **TurboSquid**：[官方许可 II.7(b) 及 WebGL 说明](https://www.turbosquid.com/licensing) 对模型可提取性和格式有明确限制；列举允许的 Unity/Unreal/Lumberyard WebGL，不把其他 WebGL 引擎一概放行。Three.js＋公开 GLB 未获本轮确认，应由平台先批准相应使用方式。此限制真实影响本项目，不能用压缩 GLB 当作许可问题已解决。
3. **Fab**：[官方标准许可摘要](https://www.fab.com/eula) 允许商业项目、修改及兼容工具，不限 UE，同时不允许单独再分发素材。第二项页面确认为标准许可；跨引擎权利不等于附赠 FBX 或已证明公开独立资产文件可再分发。第三项本轮只核实产品内容，没有核实所选许可档位。

上述是对已读条款的实施边界判断，没有替平台作批准，也没有把一般游戏许可当作公开资产源文件许可。

## 已排除的容易误选资源

- [Cartoon hands reading book — Creasheeps / Envato](https://elements.envato.com/cartoon-hands-reading-book-FLR4JMU)：虽然同时有手和书且提供 FBX/BLEND，官方明确 **Rigged: No / Animated: No**，164K polygons。是静态图标造型，不能解决真实手动作。
- [Reading Rigged and Animated Book — Creature Guard](https://creaturesguard.com/products/reading-rigged-and-animated-book-3d-model)：官方提供 Blender 书本及开合、六页翻动，说明其 rig 不支持 FBX/OBJ。它解决书，不提供已确认的双手联动。
- [Interactive Book — ThatLittleSpider 官方文档](https://www.thatlittlespider.com/interactive-book-documentation/)：的确为第一人称使用设计，但列出的双骨骼网格、Actor 和动画属于书/页系统，不能凭“first person”推断含真人手臂。
- [Sit and reading book — Animation Shopee](https://www.animationshopee.com/product-page/he-sat-and-reading-book-in-conversation)：卖家列 US$1、FBX、30 fps、65 骨和商业使用；但它是坐姿读书 idle，未确认真人手模型、配套书页、精细手指动画及公开 WebGL 条款，不列为主推荐。
- 同一 3dmi 作者的 [Hands Searching Through Pages](https://www.cgtrader.com/3d-models/sports/book/hands-searching-through-pages-animated-rigged-for-maya) 是近似内容的单项商品，不把它重复算作独立可替代方案。

## 下一步建议

优先向第一项核对四件具体事项：两段完整无剪辑视频；是否另含闭书到打开；可否提供带骨骼、蒙皮、手书共同动画和烘焙变形的 FBX/GLB；能否授权当前 Three.js 网页交付。随后先在隔离检验场景测试原配套手与书，再考虑更换本项目封面和尺寸。手、封面、页角是共同设计的接触关系，直接把现成手换进原有程序摆动时间轴仍会保留不自然动作。

未验证任何候选的实际导入、贴图还原、动作兼容、网页帧率或用户接受度。本轮研究不能恢复上一轮手部“视觉通过”的结论。
