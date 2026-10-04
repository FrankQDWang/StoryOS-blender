# 软皮修正证据

2026-10-04。`cover.jpg`、`open.jpg`、`contact.jpg`为原生Chrome实际检查页截图；`cover-blue.jpg`为第三款闭合补查。最终分辨率恢复后重采cover/open，contact为同一几何与材质参数。用户尚未认可本轮效果。

`build-identity.json`记录最终代码、生产JS、纹理SHA和18项资产校验；构建成功、既有15项测试通过。没有改数据分配/删除逻辑，也未重跑上一轮完整生命周期套组。

`benchmark-before-texture-optimization.json`为初始三组冷/暖对照，`benchmark-status.json`保留中位数和失败状态。`benchmark-local.json`为最终复测的已取得样本，包括未完成配对的候选。warm-prime只用于暖缓存预热，不计入冷/暖中位数。

基线为 `.cache/five-books/baseline/` 中eedd745冻结生产构建；候选来自最终生产输出。测量以WebGL实际着色绘制/GPU完成为首屏，蒙皮着色首次绘制为手部，DOM工作区标题为进入。测试脚本通过静态服务器注入，仅4380/4382测试origin写五书fixture，4173用户作品不受影响。脚本副本为 `harness.js`。

最初冷首屏+11.12%超出门槛，暖首屏+8.03%。最终复测基线变慢并出现多次接口超时，未完成可靠配对，10%验收状态未通过。临时降低标题纹理分辨率的尝试已撤回；不可把前一版已通过的性能结论套用到本轮。
