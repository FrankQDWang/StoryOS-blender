import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/source/makehuman-hands.blend'))
r=bpy.data.objects['RightHand'];m=bpy.data.objects['RightSkin']
r.data.pose_position='REST';bpy.context.view_layer.update()
verts=[v.co for v in m.data.vertices]
palm=[v.co for v in m.data.vertices if .09<v.co.y<.115 and sum(g.weight for g in v.groups if m.vertex_groups[g.group].name.startswith('finger1'))<.15]
report={'rest_mesh_hand_tip_y':max(v.y for v in verts),'palm_width':max(v.x for v in palm)-min(v.x for v in palm),'palm_depth':max(v.z for v in palm)-min(v.z for v in palm),'wrist_middle_tip_bone':r.data.bones['finger3-3.R'].tail_local.length,'gltf_nodes':[]}
print(json.dumps(report,indent=2))
(root/'evidence/v014-human-scale/before-dimensions.json').write_text(json.dumps(report,indent=2))
