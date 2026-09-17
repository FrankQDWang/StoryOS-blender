from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/source/makehuman-hands.blend'))
a=bpy.data.objects['RightHand'];samples=[]
for frame in (24,39,51):
 t=frame/30;u=max(0,min(1,(t-.82)/(1.83-.82)));angle=1.55*u*u*(3-2*u);bpy.context.scene.frame_set(frame)
 hinge=Vector((-.365,0,.17));inv=Matrix.Rotation(angle,4,'Y')
 samples.append({'time':t,'cover_angle':angle,'finger_bone_tails_in_cover_space':{str(d):list(hinge+inv@(a.pose.bones[f'finger{d}-3.R'].tail-hinge)) for d in (1,2,3)}})
(ROOT/'evidence/v014-human-scale/contact-samples.json').write_text(json.dumps({'note':'Bone-tail samples are pose controls, not skin collision or force measurements. Thumb is outside cover; middle finger approaches underside in the raised pose.','samples':samples},indent=2)+'\n')
