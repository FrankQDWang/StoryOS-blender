# 五款私人手稿的共用材质

用户已认可的视觉参考是 `design/round-10-five-book-materials/` 五款同族书本。此目录的 `atlas.png` 是 2026-10-04 用内置 ImageGen、以认可暖棕图为风格参照生成的一张生产材质图集，不是新的书房方案。

- [实际提示词](../manuscript-texture-prompt.txt)
- [来源、原输出路径、输入/输出 SHA256](provenance.json)
- 左半为皮革，右半为暖纸与抽象手写纹理；真实书名和简介由运行时绘制。装饰笔迹不代表作品正文。
- `node tools/book-check/prepare-textures.mjs` 分割图集、转换中性皮革、生成共用 768×768 WebP。正式资源是 `public/assets/textures/manuscript-leather.webp` 与 `manuscript-page.webp`。
- `book-materials.mjs` 保存五个固定身份、色调、纸色、粗糙度与细微凹凸强度。`BookAppearance.jsx` 将纹理和动态文字用于原 GLB；纹理不随作品重复下载。

该图集及运行贴图属于本轮新增生成素材。原书 GLB、房间、布局、人体资产和开书时间轴保持原有文件，不包含新的第三方下载。
