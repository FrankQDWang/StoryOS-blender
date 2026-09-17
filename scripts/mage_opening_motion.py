"""Authored hand performance; shared book timing is the only external input."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[1]
SEQUENCE=json.loads((ROOT/"apps/web/src/opening-sequence.json").read_text())

# Reference-guided reach, opposing-pad grip, cover lift and relaxed withdrawal.
def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def angle(t):
 return SEQUENCE['coverLift'][2]*ease(t,*SEQUENCE['coverLift'][:2])+SEQUENCE['coverSettle'][2]*ease(t,*SEQUENCE['coverSettle'][:2])
def pose(arm,side,t):
 right=side=='R';reach=ease(t,*SEQUENCE['reach']);release=ease(t,*SEQUENCE['release'])
 retreat=ease(t,*SEQUENCE['retreat']) if right else ease(t,*SEQUENCE['supportRetreat'])
 grip=ease(t,*SEQUENCE['grip'])*(1-release if right else 1-ease(t,*SEQUENCE['supportRelease']))
 a=angle(min(t,SEQUENCE['coverLift'][1])) if right else 0
 cover=Matrix.Rotation(-a,4,'Y')
 # Oversized lectern folio: support the reader-facing lower cover edge
 # on the broad finger-pad group. The thumb guides the edge, not a pinch
 # through the entire book thickness. This is an authored adaptation,
 # not a copy of the previously researched hand-held small-book grasp.
 lift_pose=ease(t,.90,1.70)
 r=cover @ Matrix.Rotation(2.90,4,'Y') @ Matrix.Rotation(.30+.12*lift_pose,4,'Z') if right else Matrix.Rotation(-.90,4,'Y')
 contact=Vector((.48,-.425,.215)) if right else Vector((-.455,-.61,.17))
 hinge=Vector((-.365,0,.17))
 wrist=hinge+cover@(contact-hinge) if right else contact
 if right:
  wrist += Vector((.22*release+.62*retreat,-.18*release-.70*retreat,-.22*release-.72*retreat))
  relaxed=Matrix.Rotation(1.32,4,'Y') @ Matrix.Rotation(.55,4,'Z')
  r=r.to_quaternion().slerp(relaxed.to_quaternion(),ease(t,2.16,3.30)).to_matrix().to_4x4()
 else:
  wrist += Vector((-.17*retreat,-.43*retreat,-.30*retreat))
 wrist+=Vector(((.16 if right else -.10)*(1-reach),-.54*(1-reach),-.28*(1-reach)))
 fore=arm.pose.bones['lowerarm02.'+side];rest=fore.bone
 # Keep the right elbow on the character's right as the hand crosses the book.
 elbow=Vector((.55 if right else -.64,-1.03-.54*(1-reach)-.44*retreat,.08 if right else wrist.z*.25-.12))
 if right:
  lift=ease(t,SEQUENCE['coverLift'][0],1.65)*(1-retreat)
  elbow=elbow.lerp(Vector((.14,-.93,wrist.z-.28)),lift)
 direction=(wrist-elbow).normalized()
 restdir=(rest.tail_local-rest.head_local).normalized()
 rotation=restdir.rotation_difference(direction).to_matrix().to_4x4()
 # Share pronation through the forearm instead of twisting all of it at the wrist seam.
 current=rotation@Vector((0,0,1));desired=r@Vector((0,0,1))
 current=(current-direction*current.dot(direction)).normalized()
 desired=(desired-direction*desired.dot(direction)).normalized()
 twist=math.atan2(direction.dot(current.cross(desired)),current.dot(desired))
 rotation=Matrix.Rotation(twist*.75,4,direction)@rotation
 fore.matrix=Matrix.Translation(wrist-direction*rest.length) @ rotation @ rest.matrix_local.to_3x3().to_4x4()
 bpy.context.view_layer.update()
 wb=arm.pose.bones['wrist.'+side]
 wb.matrix=Matrix.Translation(wrist) @ r @ wb.bone.matrix_local.to_3x3().to_4x4()
 bpy.context.view_layer.update()
 for digit in range(1,6):
  for joint in range(1,4):
   b=arm.pose.bones[f'finger{digit}-{joint}.{side}']
   local=b.bone.matrix_local.to_quaternion().inverted()
   if right:
    # Rest phalanges already curve inward. The negative offsets straighten
    # them into an underside pad surface; adding flexion here made a claw.
    idle={1:[-.10,.02,0],2:[.01,.04,.02],3:[.02,.05,.02],4:[.05,.08,.02],5:[.08,.12,.04]}[digit][joint-1]
    closed={1:[-.30,-.05,-.03],2:[-.2695,-.0895,.0500],3:[-.0675,-.1000,-.0950],4:[-.027,-.076,-.093],5:[-.205,.005,.01]}[digit][joint-1]
    lifted={1:[-.30,-.05,-.03],2:[-.19,-.10,-.055],3:[-.055,-.10,-.13],4:[-.0345,-.10,-.09],5:[-.1405,-.10,.01]}[digit][joint-1]
    closed=closed+(lifted-closed)*lift_pose
    bend=idle+(closed-idle)*grip
   elif digit==1:
    bend=[.10,.10,.06][joint-1]+grip*[.04,.06,.04][joint-1]
   else:
    idle={2:[.05,.05,.02],3:[.05,.06,.03],4:[.10,.12,.06],5:[.18,.22,.12]}[digit][joint-1]
    close={2:[.03,.04,.03],3:[.03,.03,.02],4:[.02,.03,.02],5:[.05,.05,.03]}[digit][joint-1]
    bend=idle+grip*close
   b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(local@Vector((-1,0,0)),bend)
   if digit==1 and joint==1:
    opposition=(.04*(1-grip)) if right else .03*grip
    b.rotation_quaternion=Quaternion(local@Vector((0,-1 if right else 1,0)),opposition)@b.rotation_quaternion
    if right:
     # Rest topology has an abducted thumb; bring it beside the pad group
     # instead of holding an empty C shape throughout a broad lower-edge lift.
     b.rotation_quaternion=Quaternion(local@Vector((0,0,1)),-.70*grip-.50*(1-grip))@b.rotation_quaternion
   if digit>1 and joint==1:
    spread=({2:-.076,3:.060,4:.080,5:.180}[digit] if right else -{2:-.055,3:0,4:.055,5:.16}[digit])
    b.rotation_quaternion=Quaternion(local@Vector((0,0,1)),spread)@b.rotation_quaternion
 if right:
  # Fit the load-bearing pad group to the underside of the lower edge.
  # Keep a broad support, never force one thumb tip to tow a claw pose.
  bpy.context.view_layer.update()
  target=hinge+cover@(Vector((.265,-.46497-.00030*lift_pose,.15348+.00129*lift_pose))-hinge)
  target+=Vector((.22*release+.62*retreat+.16*(1-reach),-.18*release-.70*retreat-.54*(1-reach),-.22*release-.72*retreat-.28*(1-reach)))
  support=sum((arm.pose.bones[f'finger{d}-3.R'].tail for d in (2,3)),Vector())/2
  delta=target-support
  fm=fore.matrix.copy();wm=wb.matrix.copy()
  fm.translation+=delta;wm.translation+=delta
  fore.matrix=fm;bpy.context.view_layer.update();wb.matrix=wm
  bpy.context.view_layer.update()
 for b in arm.pose.bones:
  b.rotation_mode='QUATERNION'
  b.keyframe_insert(data_path='location',frame=round(t*SEQUENCE['fps']))
  b.keyframe_insert(data_path='rotation_quaternion',frame=round(t*SEQUENCE['fps']))
  b.keyframe_insert(data_path='scale',frame=round(t*SEQUENCE['fps']))
