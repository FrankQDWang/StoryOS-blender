"""Read-only saved support candidate: landmarks and local fingertip skin envelopes."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'evidence/v014-soft-mage'
asset=ROOT/'assets/source/makehuman-hands.blend';sha=hashlib.sha256(asset.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(asset));arm=bpy.data.objects['RightHand'];obj=bpy.data.objects['RightSkin'];seq=json.loads((ROOT/'apps/web/src/opening-sequence.json').read_text());S=.824

def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def vec(v):return [round(float(x),6) for x in v]
rows=[]
for frame in [24,30,39,45,51,55,58,63,69]:
 t=frame/30;bpy.context.scene.frame_set(frame);a=sum(v[2]*ease(t,*v[:2]) for v in [seq['coverLift'],seq['coverSettle']]);hinge=Vector((-.365,0,.17));inv=Matrix.Rotation(a,4,'Y')
 f=arm.pose.bones['lowerarm02.R'];w=arm.pose.bones['wrist.R'];R=w.matrix@w.bone.matrix_local.inverted();handaxis=(R.to_3x3()@Vector((0,1,0))).normalized();foreaxis=(f.tail-f.head).normalized();palmnormal=-(inv.to_3x3()@R.to_3x3()@Vector((0,0,1))).normalized()
 skin=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
 row={'t':t,'palm_forearm_axis_angle_deg':math.degrees(handaxis.angle(foreaxis)),'palm_normal_cover_space':vec(palmnormal),'wrist_cover_space':vec(hinge+inv@(w.head-hinge)),'digits':{}}
 for d in range(1,6):
  bn=arm.pose.bones[f'finger{d}-3.R'];tail=bn.tail;name=f'finger{d}-3.R';group=obj.vertex_groups[name].index
  ids=[v.index for v in obj.data.vertices if any(g.group==group and g.weight>.45 for g in v.groups)]
  cap=[hinge+inv@(skin.vertices[i].co-hinge) for i in ids if (skin.vertices[i].co-tail).length<.027]
  tip=hinge+inv@(tail-hinge)
  row['digits'][str(d)]={'bone_tail_cover_space':vec(tip),'bone_head_cover_space':vec(hinge+inv@(bn.head-hinge)),'cap_vertices':len(cap),'cap_bounds':[[min(p[j] for p in cap),max(p[j] for p in cap)] for j in range(3)] if cap else None,'cap_nearest_underside_absolute_z_cm':min((abs(p.z-.1595)*S*100 for p in cap if -.39<=p.x<=.39 and -.5<=p.y<=.5),default=None)}
 row['three_tip_z_spread_runtime_cm']=(max(row['digits'][str(d)]['bone_tail_cover_space'][2] for d in [2,3,4])-min(row['digits'][str(d)]['bone_tail_cover_space'][2] for d in [2,3,4]))*S*100
 row['three_tip_y_spread_runtime_cm']=(max(row['digits'][str(d)]['bone_tail_cover_space'][1] for d in [2,3,4])-min(row['digits'][str(d)]['bone_tail_cover_space'][1] for d in [2,3,4]))*S*100
 obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear();rows.append(row)
result={'source_sha256':sha,'source':'assets/source/makehuman-hands.blend','note':'Candidate1 read-only pose. Bone tips not skin contacts. Skin caps are distal-weighted vertices within 0.027 authoring m of bone tail; nearest underside distances omit lateral collisions and force. Palm normal uses authoring -Z, diagnostic only.','samples':rows}
(OUT/'audit-support-candidate1.json').write_text(json.dumps(result,indent=2)+'\n');assert hashlib.sha256(asset.read_bytes()).hexdigest()==sha
for r in rows:
 print('t',r['t'],'wrist angle',round(r['palm_forearm_axis_angle_deg'],1),'normal',r['palm_normal_cover_space'],'tipzspread cm',round(r['three_tip_z_spread_runtime_cm'],2))
 print([(d,q['bone_tail_cover_space'],q['cap_nearest_underside_absolute_z_cm']) for d,q in r['digits'].items()])
