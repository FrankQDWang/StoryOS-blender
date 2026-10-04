# 细软皮纹来源

2026-10-04，内置ImageGen一次生成。参考为用户认可的 `design/round-10-five-book-materials/warm-umber.png`，用于修正preview.1材质偏硬的反馈。

- 原始输出：[leather.png](leather.png)
- 实际提示词：[prompt.txt](prompt.txt)
- 工具来源、尺寸处理和SHA：[provenance.json](provenance.json)
- 生产导出：`tools/book-check/prepare-soft-leather.mjs`
- 运行输出：`public/assets/textures/manuscript-soft-leather.webp`，768×768，141,648字节。

原输出保留。生产版仅缩放、转中性色以供五色染色、WebP编码；旧图集在 `../manuscript/` 保留，纸页继续使用旧图集导出的纸纹理。
