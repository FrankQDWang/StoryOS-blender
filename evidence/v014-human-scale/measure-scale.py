"""Read-only geometry measurements in metres; not a biomechanical simulation."""
import bpy,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
layout=json.loads((ROOT/'apps/web/src/room-layout.json').read_text())
profile=json.loads((ROOT/'apps/web/src/opening-anatomy.json').read_text())
rows=[]
for label,path in [('before','downloads/human-scale/before.blend'),('after','assets/source/makehuman-hands.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/path))
 rig=bpy.data.objects['RightHand'];mesh=bpy.data.objects['RightSkin']
 tip=max(v.co.y for v in mesh.data.vertices)
 ratio=tip/.22225145995616913
 # A reproducible mesh section behind knuckles, excluding thumb-weighted vertices.
 palm=[v.co for v in mesh.data.vertices if .09*ratio<v.co.y<.115*ratio and sum(g.weight for g in v.groups if mesh.vertex_groups[g.group].name.startswith('finger1'))<.15]
 width=max(v.x for v in palm)-min(v.x for v in palm)
 slots=[]
 for i,slot in enumerate(layout['slots']):
  scale=slot['scale'] if label=='before' else profile['referenceBookScale']
  slots.append({'slot':i+1,'book_length_m':slot['scale'],'hand_length_m':tip*scale,'palm_mesh_section_width_m':width*scale})
 rows.append({'version':label,'authoring_hand_length':tip,'source_rig_bones':len(rig.data.bones),'slots':slots})
result={'character_profile':profile,'method':'Skin rest-coordinate wrist origin to most distal middle-finger mesh vertex. Palm width is the documented mesh section, not a certified anthropometric landmark measurement. After uses runtime inverse-book-scale compensation. Sleeves remain camera-framed proxies, not a full shoulder/elbow body rig.','measurements':rows,'anthropometry_reference':'https://www.dinbelg.be/DINBelg%202005%20anthropometry%20table.PDF','selection':'19.5 cm hand length for this 1.70 m character, not a unique height-to-hand formula.'}
(ROOT/'evidence/v014-human-scale/dimensions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
