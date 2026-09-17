"""Compare saved Blender poses; baseline is the ignored pre-change snapshot.

If needed, restore it from Git before running this with Blender:
git show e8bd23e:assets/source/makehuman-hands.blend > downloads/wrist-step/before.blend
"""
from pathlib import Path
import bpy, math, json
ROOT=Path(__file__).resolve().parents[2]

def capture(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 arms=[o for o in bpy.data.objects if o.type=='ARMATURE']
 frames=[]
 for frame in range(106):
  bpy.context.scene.frame_set(frame)
  states={}
  for arm in arms:
   for bone in arm.pose.bones:
    states[bone.name]=[v for row in bone.matrix for v in row]
  right=next(a for a in arms if a.name.startswith('Right'))
  wrist=right.pose.bones['wrist.R'];fore=right.pose.bones['lowerarm02.R'];middle=right.pose.bones['finger3-1.R']
  angle=math.degrees((wrist.head-fore.head).angle(middle.head-wrist.head))
  frames.append({'frame':frame,'seconds':frame/30,'angle':angle,'bones':states})
 return frames

before=capture(ROOT/'downloads/wrist-step/before.blend')
after=capture(ROOT/'assets/source/makehuman-hands.blend')
max_unchanged=max(abs(x-y) for a,b in zip(before,after) for name in a['bones'] if name!='lowerarm02.R' for x,y in zip(a['bones'][name],b['bones'][name]))
assert max_unchanged<1e-5,max_unchanged
rows=[{'seconds':a['seconds'],'before_bend_degrees':a['angle'],'after_bend_degrees':b['angle']} for a,b in zip(before,after)]
lift=[r for r in rows if .8<=r['seconds']<=2.1]
assert max(r['after_bend_degrees'] for r in lift)<=45
report={'measurement':'forearm-to-palm long-axis angle, not a medical joint angle or visual acceptance',
 'max_other_bone_world_matrix_difference':max_unchanged,
 'left_hand_and_right_wrist_finger_poses_unchanged':True,
 'lift_peak_before_degrees':max(r['before_bend_degrees'] for r in lift),
 'lift_peak_after_degrees':max(r['after_bend_degrees'] for r in lift),
 'samples':rows}
(ROOT/'evidence/v014-wrist-step/kinematics.json').write_text(json.dumps(report,indent=2)+'\n')
print('HAND_MOTION',json.dumps({k:v for k,v in report.items() if k!='samples'}))
