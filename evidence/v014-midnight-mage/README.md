# 午夜蓝手部与袍袖验证

2026-09-17，0.1.4-preview.5。选图为`design/round-07-wizard-robes/02-midnight-tower-mage.png`；本目录是实际模型/Chrome证据，不能用概念图替代。

**后续状态：用户已否定本版的绿色内袖、手形、右手动作及僵硬材质，原助手视觉通过撤回。** 本目录作为历史证据保留；继续改进的preview.6已获用户认可，见`evidence/v014-soft-mage/`与PLAN当前交接。

- `comparison-main.jpg`：同机位0.80/1.30/1.70/2.15秒，左旧右新；原图`before-*`、`after-*`。截图未修饰，只等比缩放并加标签。
- `five-slots-sheet.jpg`与`slot-*-*.png`：五位四姿态；首次快速seek的旧帧残留已重截，最终第四位0.80s为正确的闭合状态。
- `side-sheet.jpg`、`side-*.png`：侧面四姿态；侧面窗口宽828px，主检查窗口1512px，不能跨视图作像素比例测量。
- `normal/`、`slow/`、`live/`：14/75/81张连续过程截图与各自times.json。检查页时间取显示控件；正式入口为点击后墙钟近似时间，不是精确动画时间。各联系表供快速查看，原图用于局部判断。
- `before/after-overview.png`、`entered-workspace.png`：房间全景保持及真实进入《星海余烬》；返回后原5书/最近作品保持。
- `before/after-material-model.png`：真实Blender模型同相机/灯光静态渲染，不是Chrome截图；`before/after-skin-detail.png`为同中心/灯光皮肤对照。棚光比书房明亮，不将两者混作材质一致性证明。
- `candidate-01/02/03-1.70.png`、`candidate-stale-seek.png`：中间问题追溯，不代表最终交付。
- `baseline-files.json`、`model-verification.json`、`asset-verification.json`、构建/测试日志、`browser-errors.json`：实际哈希、骨骼动作保持、生产一致性及控制台结果。
- `render-model.py`、`verify-model.py`、`verify-assets.py`、`make-boards.py`：可复查脚本；baseline模型保存在忽略的`downloads/mage-hands/baseline/`。联系表使用现有Codex运行时Pillow，没有安装新依赖。

当时的助手视觉结论及剩余限制见`design/iterations/13-midnight-mage-implementation.md`。本轮新增双层袍袖与手部表面，房间/书本/火焰与运行组件保持；外袍开口还略硬，皮肤细节比概念图简化。随后的用户否定以上方更新为准。
