# preview.6 实际验证证据

**后续用户评审**：2026-09-17用户回复“可以，非常棒”，认可本版并授权提交、PR合main及分支清理。保存验证位于`evidence/v014-mage-save/`，最终Git状态见PLAN；以下保留当时采样条件和助手判断。

2026-09-17。修正被用户否定的preview.5，增加大书下沿托举、去绿色内袖、手部形体/皮肤修正和法袍变形。助手确认局部改善，仍待用户评审。详细判断与边界见`design/iterations/14-soft-mage-and-large-folio.md`。

## 最终证据

- `comparison-four-poses.jpg`：左preview.5、右preview.6，同机位0.80/1.30/1.70/2.15秒。原图为旧轮`after-*`和本轮根部`after-*`，只等比排版加标签，没有重绘或美化。
- `after-*.png` / `side-*.png`：最终正侧面各5张实际Chrome截图。
- `slots/`与`five-slots.jpg`：5个书位、各4关键姿态。
- `normal/` 23帧、`slow/` 118帧、`live/` 98帧：实际Chrome连续采样。`times.json`保存检查页可见时间或相对捕获起点的墙钟耗时，间隔不均匀，不等于逐渲染帧录像。UI时间和截图有工具调用间隔。
- `actual-opening.mp4`：由`live/`原截图按记录的墙钟间隔合成，缩至1000px宽、24fps编码，没有AI补帧或动作修饰。捕获起点在点击开书并读取界面状态之后，不是精准动画零点；末尾包含进入工作区。
- `normal/slow/live-contact-sheet.jpg`：覆盖相应采样起止的18格联系表。实际入口后半已经进入工作区，保留原图。
- `workspace.png`、`overview-returned.png`：第一位《星海余烬》完整进入并返回，原5书保持。
- `hand-before-after-same-light.png`：离线同灯光手模型对照，左preview.5右本轮形体；用于检查细节，不冒充Chrome画面。`hand-surface-details.json`与`hand-corrective-export-check.json`是该手部独立探针，不替代最终组合资产检查。
- `tests.log`：14项通过。`production-build.log`：构建通过，既有大分块提示。
- `asset-verification.json`：15项manifest、20份来源文件、4张服装纹理和13份生产文件；GLB3,835,100 bytes、73,680三角形、每手45关节和5个皮肤形态。
- `chrome-errors.json`：主入口、检查页及侧视页错误均0条。

## 过程证据，不能当最终状态

`trials/`、`after-material-model.png`、早期`fit-support-*`和`audit-support-candidate1*`记录被修正的中间候选。`fit-support-fk-final.json`记录最终拟合基础，后续中指接触目标微调以代码/最终导出为准。`robe-slanted-*-probe.png`是衣袖静态版型探针，不是最终运行图。`preview-motion.py`只用于临时导出测试；正式复现用`npm run assets:hands`。

旧preview.5备份在忽略的`downloads/soft-mage/baseline-preview5/`，哈希索引`baseline-files.json`。本目录未改变、覆盖或删除前轮证据。
