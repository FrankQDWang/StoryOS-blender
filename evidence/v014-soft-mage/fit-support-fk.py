from pathlib import Path
import bpy,json,math,hashlib,time
import numpy as np
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'evidence/v014-soft-mage';asset=ROOT/'assets/source/makehuman-hands.blend';sha=hashlib.sha256(asset.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(asset));arm=bpy.data.objects['RightHand'];skin=bpy.data.objects['RightSkin'];seq=json.loads((ROOT/'apps/web/src/opening-sequence.json').read_text())
# Inspection only: simulate pose in memory; never save the source blend.
print('MODIFIERS',[(m.type,m.name) for m in skin.modifiers])
print('BONES',[(b.name,b.parent.name if b.parent else None) for b in arm.data.bones])
def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def array(m):return np.array(m,dtype=float)
rest={b.name:b.matrix_local.copy() for b in arm.data.bones};bones={b.name:b for b in arm.data.bones}
# Vertices influenced by distal bones. Linear blend skinning matches armature evaluator.
V=np.array([(*v.co,1) for v in skin.data.vertices]);N=np.array([v.normal[:] for v in skin.data.vertices]);weight={g.index:g.name for g in skin.vertex_groups}
W={n:np.zeros(len(V)) for n in bones}
for v in skin.data.vertices:
 for g in v.groups:
  if weight[g.group] in W:W[weight[g.group]][v.index]=g.weight
caps={d:np.where(W[f'finger{d}-3.R']>.65)[0] for d in range(1,6)}
print('CAPS',[len(caps[d]) for d in caps])
for d in range(1,6):
 b=bones[f'finger{d}-3.R'];print('REST',d,'head',list(b.head_local),'tail',list(b.tail_local))
rows=[]
for t in [.8,1.7]:
 bpy.context.scene.frame_set(round(t*30));M={p.name:p.matrix.copy() for p in arm.pose.bones};a=sum(v[2]*ease(t,*v[:2]) for v in [seq['coverLift'],seq['coverSettle']]);h=Vector((-.365,0,.17));C=Matrix.Translation(h)@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-h)
 # Fixed wrist cover orientation requested by root; translations irrelevant to relative fit.
 wrist=arm.pose.bones['wrist.R'];Mw=Matrix.Translation(wrist.head)@Matrix.Rotation(-a,4,'Y')@Matrix.Rotation(2.90,4,'Y')@Matrix.Rotation(.30 if t==.8 else .42,4,'Z')@rest['wrist.R'].to_3x3().to_4x4();M['wrist.R']=Mw
 spread={2:-.08 if t==.8 else 0,3:0,4:.08,5:.18}
 def calc(d,q,opp=.08,add=-.7):
  mats={'wrist.R':Mw}
  # Traverse anatomical chain to digit, including fixed metacarpal.
  chain=[];b=bones[f'finger{d}-3.R']
  while b.name!='wrist.R':chain.append(b);b=b.parent
  for b in reversed(chain):
   basis=Matrix.Identity(4)
   if b.name.startswith('finger'):
    j=int(b.name.split('-')[1][0]);local=b.matrix_local.to_quaternion().inverted();Q=Quaternion(local@Vector((-1,0,0)),float(q[j-1]))
    if j==1:
     if d==1:Q=Quaternion(local@Vector((0,0,1)),add)@Quaternion(local@Vector((0,-1,0)),opp)@Q
     else:Q=Quaternion(local@Vector((0,0,1)),spread[d])@Q
    basis=Q.to_matrix().to_4x4()
   mats[b.name]=mats[b.parent.name]@rest[b.parent.name].inverted()@rest[b.name]@basis
  bn=bones[f'finger{d}-3.R'];bd=mats[bn.name];tip=C@(bd@Vector((0,bn.length,0)));head=C@bd.translation;axis=(tip-head).normalized();angle=math.degrees(math.asin(abs(axis.z)))
  ids=caps[d];vv=np.zeros((len(ids),4))
  for name,weights in W.items():
   ww=weights[ids]
   if np.any(ww):vv+=(V[ids]@array(C@(mats.get(name,M[name])@rest[name].inverted())).T)*ww[:,None]
  return np.array(tip),np.array(axis),vv[:,:3],mats,angle
 # Print all-zero and uniform bends.
 for d in range(1,6):
  for q in [[0,0,0],[-.2,0,0],[.1,-.35,-.25]]:
   tip,axis,vv,_,ang=calc(d,q);print('PROBE',t,d,q,'tip',tip.tolist(),'axis',axis.tolist(),'angle',ang)
 # Fit two pads against lip, with third nearby and natural actual joint curvature.
 def stats(d,q):
  tip,axis,vv,mats,ang=calc(d,q)
  # Palmar upper surface; use top 20% of distal skin vertices for contact centroid.
  z95=float(np.quantile(vv[:,2],.97));top=vv[vv[:,2]>=np.quantile(vv[:,2],.80)]
  pt=np.mean(top,axis=0);pt[2]=z95
  axes=[]
  for j in range(1,4):
   mm=C@mats[f'finger{d}-{j}.R'];axes.append((mm.to_3x3()@Vector((0,1,0))).normalized())
  # Signed planar bend relative source local flexion axis, actual axes.
  joint=[]
  for j in range(2):
   cr=axes[j].cross(axes[j+1]);sg=1 if cr.dot(C.to_3x3()@Mw.to_3x3()@Vector((-1,0,0)))>=0 else -1
   joint.append(math.degrees(axes[j].angle(axes[j+1]))*sg)
  return pt,ang,joint,tip,axis,vv,mats
 z0=.043 if t==.8 else .050
 x=np.array([-.10,-.13,-.13, .15,-.25,-.2, .20,-.25,-.2, .28,-.20,-.13,-.037,z0,-.06,0.0])
 def score(x,details=False):
  spread[2]=x[14];spread[3]=x[15]
  data=[stats(d,x[(d-2)*3:(d-1)*3]) for d in range(2,6)];dy,dz=x[12:14];cost=0
  for i,(pt,ang,joint,tip,ax,vv,_) in enumerate(data):
   yy,zz=pt[1]+dy,pt[2]+dz;ww=[1,1,.35,.1][i]
   # Pad centroid in cover lip. Third/fourth may lie outside front, not deeply behind lip.
   desiredy=[-.480,-.469,-.464,-.500][i]
   cost+=ww*((yy-desiredy)*100)**2
   desiredz=[.1595,.1595,.1565,.145][i]
   cost+=ww*((zz-desiredz)*120)**2
   cost+=max(0,ang-22)**2*.5
   cost+=max(0,5-ang)**2*.003
   # Positive resting curve remains permissible; avoid concave reversal of adjacent segments.
   # Numeric q regularization prevents gratuitous compensated folds.
   cost+=.3*sum(float(v)**2 for v in x[i*3:i*3+3])
  cost+=.15*sum((x[j]-x[j+3])**2 for j in range(9))
  return (cost,data) if details else cost
 # Small, deterministic, derivative-free optimization; pose final is checked with Blender below.
 for j in range(12):
  lo,hi=[(-.5,.5),(-.10,.3),(-.22,.3)][j%3];x[j]=max(lo,min(hi,x[j]))
 best=score(x)
 for step in [.12,.06,.03,.015,.0075,.003]:
  for iteration in range(30):
   changed=False
   for j in range(len(x)):
    delta=step if j<12 or j>=14 else step*.035
    options=[]
    for sign in [-1,1]:
     xx=x.copy();xx[j]+=sign*delta
     if j<12:
      lo,hi=[(-.5,.5),(-.10,.3),(-.22,.3)][j%3]
      if not lo<=xx[j]<=hi:continue
     if j>=14 and not -.08<=xx[j]<=.06:continue
     c=score(xx);options.append((c,xx))
    if options:
     c,xx=min(options,key=lambda p:p[0])
     if c<best:best,x,changed=c,xx,True
   if not changed:break
 _,data=score(x,True)
 print('FIT',t,'q',x.tolist(),'score',best)
 rr={'t':t,'hand_y':2.90,'hand_z':.30 if t==.8 else .42,'cost':best,'finger_angles':{str(d):x[(d-2)*3:(d-1)*3].tolist() for d in range(2,6)},'additional_cover_translation_yz':x[12:14].tolist(),'spreads':dict(spread),'digits':{}}
 for d,(pt,ang,joint,tip,ax,vv,mats) in zip(range(2,6),data):
  pt[1:]+=x[12:14];tip[1:]+=x[12:14];vv[:,1:]+=x[12:14]
  rr['digits'][str(d)]={'pad_top_centroid':pt.tolist(),'distal_angle':ang,'actual_joint_axis_angle_signed':joint,'tip':tip.tolist(),'skin_bounds':[[float(vv[:,j].min()),float(vv[:,j].max())] for j in range(3)]}
  print('FITDIGIT',d,rr['digits'][str(d)])
 # Blender evaluated mesh verification of the analytical linear skin estimate.
 saved_action=arm.animation_data.action;arm.animation_data.action=None
 arm.pose.bones['wrist.R'].matrix=Mw;bpy.context.view_layer.update()
 for d in range(2,6):
  for j in range(1,4):
   b=arm.pose.bones[f'finger{d}-{j}.R'];local=b.bone.matrix_local.to_quaternion().inverted();Q=Quaternion(local@Vector((-1,0,0)),float(x[(d-2)*3+j-1]))
   if j==1:Q=Quaternion(local@Vector((0,0,1)),spread[d])@Q
   b.rotation_mode='QUATERNION';b.rotation_quaternion=Q
 bpy.context.view_layer.update()
 ev=skin.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();errors={}
 for d in range(2,6):
  vv=calc(d,x[(d-2)*3:(d-1)*3])[2]
  actual=np.array([(C@mesh.vertices[int(i)].co)[:] for i in caps[d]])
  errors[str(d)]=float(np.max(np.linalg.norm(actual-vv,axis=1)))
  actual[:,1:]+=x[12:14];top=actual[actual[:,2]>=np.quantile(actual[:,2],.80)]
  pp=np.mean(top,axis=0);pp[2]=np.quantile(actual[:,2],.97)
  rr['digits'][str(d)]['actual_skin_pad_top_centroid']=pp.tolist()
  rr['digits'][str(d)]['actual_skin_max_z']=float(actual[:,2].max())
 ev.to_mesh_clear();rr['actual_blender_skin_max_error_author_m']=errors
 arm.animation_data.action=saved_action
 # Thumb uses no pad-contact obligation: relaxed beside fingers, clear from cover.
 thumbs=[]
 for add in [-.4,-.55,-.7]:
  for opp in [0,.08]:
   q=[-.12,-.05,-.03];tip,axis,vv,_,ang=calc(1,q,opp,add);vv[:,1:]+=x[12:14];tip[1:]+=x[12:14]
   thumbs.append({'angles':q,'adduction':add,'opposition':opp,'tip':tip.tolist(),'distal_angle':ang,'skin_bounds':[[float(vv[:,j].min()),float(vv[:,j].max())] for j in range(3)]})
 rr['thumb_trials']=thumbs
 rr['bone_tip_mean_target']=np.mean([rr['digits'][str(d)]['tip'] for d in [2,3]],axis=0).tolist()
 rr['bone_tip_mean_target'][0]=.265
 print('BLENDER_SKIN_ERROR',errors)
 rows.append(rr)
(OUT/'fit-support-fk-result.json').write_text(json.dumps({'sha':sha,'samples':rows},indent=2))
