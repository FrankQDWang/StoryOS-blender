from pathlib import Path
import sys, json, bpy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'downloads/mpfb2/src'))
# Isolate this headless research process: no global installation or user preferences.
original_path=bpy.utils.extension_path_user
bpy.utils.extension_path_user=lambda package, path='', create=False: str(ROOT/'downloads/mpfb-user'/path)
import mpfb
bpy.context.preferences.addons.new().module='mpfb'
mpfb.register()
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
macro=TargetService.get_default_macro_info_dict()
macro.update(gender=.75, age=.38, muscle=.45, weight=.47, height=.52)
human=HumanService.create_human(macro_detail_dict=macro)
arm=HumanService.add_builtin_rig(human,'default')
human.name='MakeHumanSource'; arm.name='MakeHumanRig'
bpy.context.view_layer.update()
report={'macro':macro,'mesh':len(human.data.vertices),'bounds':[list(v) for v in human.bound_box], 'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in arm.data.bones},'groups':[g.name for g in human.vertex_groups]}
(ROOT/'assets/vendor/makehuman/base-human.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/vendor/makehuman/base-human.blend'))
print('HUMAN_READY',len(human.data.vertices),len(arm.data.bones))
