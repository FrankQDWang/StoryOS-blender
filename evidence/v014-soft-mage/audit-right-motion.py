"""Read saved pose only; bone landmarks are not fingertip surface contacts."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'evidence/v014-soft-mage'
asset=ROOT/'assets/source/makehuman-hands.blend';digest=hashlib.sha256(asset.read_bytes()).hexdigest()
seq=json.loads((ROOT/'apps/web/src/opening-sequence.json').read_text());S=.824
bpy.ops.wm.open_mainfile(filepath=str(asset));arm=bpy.data.objects['RightHand'];samples=[]
def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def v(x):return [round(float(a),6) for a in x]
for frame in [24,30,39,45,51,55,58,63,69,78]:
 t=frame/30;bpy.context.scene.frame_set(frame)
 angle=sum(k[2]*ease(t,*k[:2]) for k in [seq['coverLift'],seq['coverSettle']]);hinge=Vector((-.365,0,.17));inv=Matrix.Rotation(angle,4,'Y')
 fore=arm.pose.bones['lowerarm02.R'];wrist=arm.pose.bones['wrist.R']
 wristrot=wrist.matrix@wrist.bone.matrix_local.inverted();palm_axis=(wristrot.to_3x3()@Vector((0,1,0))).normalized();foreaxis=(fore.tail-fore.head).normalized()
 tips={str(d):hinge+inv@(arm.pose.bones[f'finger{d}-3.R'].tail-hinge) for d in range(1,6)}
 samples.append({'time_s':t,'cover_angle_deg':math.degrees(angle),'wrist_m':v(wrist.head*S),'palm_forearm_long_axis_angle_deg':math.degrees(palm_axis.angle(foreaxis)),'finger_bone_tails_cover_authoring_m':{d:v(p) for d,p in tips.items()},'index_middle_tail_distance_runtime_cm':(tips['2']-tips['3']).length*S*100,'index_middle_tail_edgewise_y_difference_runtime_cm':abs(tips['2'].y-tips['3'].y)*S*100,'bone_joint_heads_cover_authoring_m':{str(d):[v(hinge+inv@(arm.pose.bones[f'finger{d}-{j}.R'].head-hinge)) for j in range(1,4)] for d in range(1,6)}})
result={'source_blend_sha256':digest,'method':'Read saved skeletal animation from source blend; transform bone landmark positions into full animated-cover local coordinates. Units authoring metres unless specified runtime scale 0.824. No reconstruction or asset save.','limitations':['Bone tails are not skin contact points or biometric joint landmarks.','Long-axis angle is orientation diagnostic, not anatomical wrist flexion.','After 1.83s the current hand generator freezes its cover carrier at lift endpoint while the cover keeps settling, so post-release values show designed separation.'],'samples':samples}
(OUT/'audit-right-motion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
assert hashlib.sha256(asset.read_bytes()).hexdigest()==digest
for s in samples:print(s['time_s'],round(s['cover_angle_deg'],1),'wrist-axis',round(s['palm_forearm_long_axis_angle_deg'],1),'index-middle cm',round(s['index_middle_tail_distance_runtime_cm'],2),'edgewise diff',round(s['index_middle_tail_edgewise_y_difference_runtime_cm'],2))
