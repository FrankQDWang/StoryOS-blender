# 鼠标直接环顾恢复记录

2026-10-05，Chrome现有4395页面。

此前以拖拽可用证明体验一致的结论撤回。原smoke.mjs只检查W/A位移，没有检查pointerLock或无按键环顾，存在验收遗漏。

同页临时包装requestPointerLock记录结果：
- 自动化tab.click：请求已发出，WrongDocumentError: The root document of this element is not valid for pointer lock.；pointerLockElement为空，界面降级拖拽。
- 页面document.hasFocus=true、visibility=visible、top层。
- 原生Chrome click：请求resolved，pointerLockElement===document.body，界面“鼠标环顾”。
- 两次Input.dispatchMouseEvent(mouseMoved, buttons=0)：截图从窗户正面变为天花板/侧面，证明无需按键可转动。
- 原生Esc返回全景，再次原生点击自由漫游：第二次resolved且body锁定。

恢复原始requestPointerLock函数，删除临时变量。运行源未改；此次恢复的是被自动化点击留在回退模式的页面状态，不将其描述为代码修复。已保留当前成功锁定页面。截图restored.png。
