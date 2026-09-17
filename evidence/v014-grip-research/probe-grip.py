"""Read current authored keyframes; no model mutation or saving."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
r=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(r/'assets/source/makehuman-hands.blend'))
a=bpy.data.objects['RightHand']; out=[]
for frame in [24,39,51]:
 bpy.context.scene.frame_set(frame)
 wb=a.pose.bones['wrist.R']; inv=wb.matrix @ wb.bone.matrix_local.inverted();inv=inv.inverted()
 row={'time':frame/30,'wrist':[round(x,5) for x in wb.head],'digit_positions_in_hand_rest_frame':{}}
 for i in range(1,6):
  bs=[a.pose.bones[f'finger{i}-{j}.R'] for j in range(1,4)]
  row['digit_positions_in_hand_rest_frame'][str(i)]={k:[[round(x,5) for x in inv@p] for p in ps] for k,ps in [('heads',[b.head for b in bs]),('tip',[bs[-1].tail])]}
 out.append(row)
(r/'evidence/v014-grip-research/current-grip-probe.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
