# 封面字体来源

2026-10-04。用户指出系统替代字体与深色1/浅色3参考不符后，通过同文案字形对照选取以下实际字库；字体是对生成字形风格的可排版实现，不把生成图声称为现成字体文件。

| 用途 | 字库 | 实际字重 | 本地 CSS family |
| --- | --- | --- | --- |
| 深色中文 | Ma Shan Zheng | 400 | Cover Brush |
| 深色英文 | Klee One（仅 Latin / Latin Extended） | 400 | Cover Hand Latin |
| 浅色中文 | Noto Serif SC | 600 | Cover Serif CN（CSS 500，使用原600文件，不合成笔画） |
| 浅色英文 | EB Garamond | 500 | Cover Serif Latin |

上游来自 Google Fonts CSS2（Google Fonts 官方字体服务），原始CSS保存在本目录；逐文件下载地址、字节数和SHA256在`manifest.json`，OFL原文一并保存。WOFF2原文件未修改，运行副本在`public/assets/fonts/cover/`。Klee One不携带日文字形，避免覆盖中文毛笔字库。字体按上游unicode-range分片，运行只请求书名所需的片段，不整包下载；`document.fonts.load`完成后才绘制标题，防止先画系统字再不更新。

字体来源与授权：
- https://github.com/googlefonts/mashanzheng
- https://github.com/google/fonts/tree/main/ofl/kleeone
- https://github.com/google/fonts/tree/main/ofl/notoserifsc
- https://github.com/google/fonts/tree/main/ofl/ebgaramond

字形比较证据：`evidence/cover-typography-focus-fix-20261004/font-study.png`、`latin-study.png`。实际选中态和用户评审状态见PLAN与design-qa。
