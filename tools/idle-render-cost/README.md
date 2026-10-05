# idle-render-cost 测量

仅测试构建通过 Vite 插件注入 Probe，应用的正常 `npm run build` 不含此入口、固定时钟或 GPU 查询。

```sh
node tools/idle-render-cost/build.mjs baseline
node tools/idle-render-cost/serve.mjs baseline 4191
node tools/idle-render-cost/capture.mjs evidence/idle-render-cost/baseline-a http://127.0.0.1:4191
node tools/idle-render-cost/capture.mjs evidence/idle-render-cost/baseline-b http://127.0.0.1:4191
node tools/idle-render-cost/compare.mjs evidence/idle-render-cost/baseline-a evidence/idle-render-cost/baseline-b evidence/idle-render-cost/repeatability.json
node tools/idle-render-cost/measure.mjs evidence/idle-render-cost/baseline-perf http://127.0.0.1:4191
```

CPU来自CDP Performance.ProcessTime增量/墙钟增量，百分比按单核计算。正常CPU采样不启用GPU/pass探针；被动探针、RAF采样代码基线与候选相同。GPU样本另测，使用EXT_disjoint_timer_query_webgl2，计时覆盖阴影及主场景、每个后处理render；异步收集且记录disjoint。RAF间隔是回调帧间隔，不冒充GPU完成时间。

固定视口1512×695、设备DPR2，保留应用DPR上限1.5、全部原画质参数；使用实际安装的Chrome硬件渲染。测试存储使用独立browser context的固定五书数据，不改用户Chrome。

画面对照：独立入口固定种子123456789；R3F从never启动，按1/60秒推进到指定时刻，同一生产场景、材质、灯光、后处理及动画函数。只有截图运行受手动时钟控制，正常CPU/GPU运行和正常应用都保持原连续帧。像素阈值提前定为RGB单通道最大2/255、全图平均0.01/255；超过即不通过。

GPU校准后采用原生Metal：

```sh
node tools/idle-render-cost/metal-scenarios.mjs evidence/idle-render-cost/baseline-metal http://127.0.0.1:4193
python3 tools/idle-render-cost/metal-window.py evidence/idle-render-cost/baseline-metal/idle
```

**本机WebGL timer query已被实测判定无效**，Probe原始GPU字段仅保留诊断，不可用其总和验收。Metal原始trace放`.cache/idle-render-cost/native-traces/`，每场景有trace-path.json、导出XML、场景墙钟窗口与实际场景render时间戳。用目标Chrome GPU进程的Active区间并集/该窗口实际render次数衡量每帧GPU活跃时间（包含浏览器合成）。Instruments“Frame #”实际按command buffer编号，不能直接当网页帧。CPU按原来未启用GPU查询的采样独立测量；分段CPU和绘制次数使用count-passes.mjs。

smoke.mjs仅走用户要求的主流程并保存图像，不是新业务测试套件。idle-pair.mjs交错采集上一保留状态和候选，各三轮；load.mjs交错测冷/暖首屏和首次手部，各三轮。所有生产页面使用独立Chromecontext。
