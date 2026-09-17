"""Adapt CC0 MakeHuman anatomy and its original skin weights, without remeshing.

Uses assets/vendor/makehuman/base-human.blend, produced with the pinned MPFB source.
No changes to the approved room or book assets. Metres, Z up in Blender.
"""
from pathlib import Path
import bpy, bmesh, json, math, hashlib
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1]
SEQUENCE=json.loads((ROOT/'apps/web/src/opening-sequence.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/vendor/makehuman/base-human.blend'))
source=bpy.data.objects['MakeHumanSource']; source_rig=bpy.data.objects['MakeHumanRig']
# Bake macro shape keys and the helper mask, preserving source UV/deform layers.
deps=bpy.context.evaluated_depsgraph_get()
body=bpy.data.meshes.new_from_object(source.evaluated_get(deps), preserve_all_data_layers=True, depsgraph=deps)

def material(name,color,roughness):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness
 return m
skin=material('Human skin',(.50,.285,.18),.69)
skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.07
cloth=material('Slate woven sleeve',(.035,.060,.064),.88)
trim=material('Cuff facing',(.052,.082,.086),.82)
texture=bpy.data.images.load(str(ROOT/'assets/vendor/makehuman/Aksel_Skin_diffuse.png'))
texture.scale(2048,2048);texture.pack()
tex=skin.node_tree.nodes.new('ShaderNodeTexImage');tex.image=texture
skin.node_tree.links.new(tex.outputs['Color'],skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
# Fingernails are part of the original human topology/UV, not added primitive meshes.
hands=[]
for side,label in [('R','Right'),('L','Left')]:
 wrist=source_rig.data.bones['wrist.'+side].head_local.copy()
 forward=(source_rig.data.bones['finger3-1.'+side].head_local-wrist).normalized()
 radial=source_rig.data.bones['finger2-1.'+side].head_local-source_rig.data.bones['finger5-1.'+side].head_local
 radial=(radial-forward*radial.dot(forward)).normalized()
 x=radial*(-1 if side=='R' else 1); z=x.cross(forward).normalized()
 basis=Matrix((x,forward,z)); transform=Matrix.Scale(1.3,4) @ basis.to_4x4() @ Matrix.Translation(-wrist)
 arm=source_rig.copy();arm.data=source_rig.data.copy();bpy.context.collection.objects.link(arm);arm.name=label+'Hand'
 arm.data.transform(transform)
 bpy.context.view_layer.objects.active=arm
 bpy.ops.object.mode_set(mode='EDIT')
 for bone in list(arm.data.edit_bones):
  if not (bone.name.endswith('.'+side) and (bone.name.startswith(('finger','metacarpal','wrist','lowerarm02')))):
   arm.data.edit_bones.remove(bone)
 forearm=arm.data.edit_bones['lowerarm02.'+side]
 forearm.parent=None; forearm.use_connect=False
 # Same rest axis, extended proximally so sleeves can follow the forearm independently.
 forearm.head=forearm.tail+(forearm.head-forearm.tail).normalized()*1.2
 bpy.ops.object.mode_set(mode='OBJECT')
 obj=source.copy();obj.data=body.copy();bpy.context.collection.objects.link(obj);obj.name=label+'Skin';obj.parent=arm
 obj.modifiers.clear();obj.data.transform(transform)
 bm=bmesh.new();bm.from_mesh(obj.data)
 # Side cut excludes the rest of the body; original hands remain unmodified.
 bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y < -.13 or v.co.y>.30 or abs(v.co.x)>.20 or abs(v.co.z)>.18],context='VERTS')
 bm.to_mesh(obj.data);bm.free()
 keep={b.name for b in arm.data.bones}
 # Forearm vertices also reference the upstream arm bone. Combine those weights at the new proximal root.
 root_group=obj.vertex_groups['lowerarm02.'+side]
 unwanted={g.index for g in obj.vertex_groups if g.name not in keep}
 for v in obj.data.vertices:
  missing=sum(g.weight for g in v.groups if g.group in unwanted and obj.vertex_groups[g.group].name.startswith(('lowerarm','upperarm')))
  if missing:root_group.add([v.index],missing,'ADD')
 for g in list(obj.vertex_groups):
  if g.name not in keep:obj.vertex_groups.remove(g)
 obj.data.materials.clear();obj.data.materials.append(skin)
 for f in obj.data.polygons:f.use_smooth=True
 modifier=obj.modifiers.new('Original MakeHuman skinning','ARMATURE');modifier.object=arm
 # One subdivision keeps the carefully authored knuckle loops smooth at close range.
 bpy.context.view_layer.objects.active=obj
 sub=obj.modifiers.new('Surface refinement','SUBSURF');sub.levels=1
 # Apply before export while retaining the source deformation weights.
 obj.modifiers.move(len(obj.modifiers)-1,0)
 bpy.ops.object.modifier_apply(modifier=sub.name)
 direction=arm.data.bones['lowerarm02.'+side].head_local.normalized()
 # Sleeve has a quiet tailored taper and two inset cuff rows, ending behind the wrist.
 verts=[];faces=[];rings=[(1.20,.072,.060),(.65,.067,.057),(.40,.060,.050),(.25,.052,.044),(.145,.047,.038),(.107,.044,.035),(.10,.044,.035)]
 axis=-direction;xx=Vector((1,0,0));xx=(xx-axis*xx.dot(axis)).normalized();zz=xx.cross(axis)
 for j,(distance,w,d) in enumerate(rings):
  center=direction*distance
  for i in range(24):
   a=i*math.tau/24;ripple=1+.025*math.sin(3*a+j*.6)
   verts.append(center+xx*math.cos(a)*w*ripple+zz*math.sin(a)*d*ripple)
 for j in range(len(rings)-1):
  for i in range(24):faces.append((j*24+i,j*24+(i+1)%24,(j+1)*24+(i+1)%24,(j+1)*24+i))
 mesh=bpy.data.meshes.new(label+'Sleeve');mesh.from_pydata(verts,[],faces);mesh.materials.append(cloth);mesh.materials.append(trim)
 sleeve=bpy.data.objects.new(label+'Sleeve',mesh);bpy.context.collection.objects.link(sleeve);sleeve.parent=arm
 for p in mesh.polygons:p.use_smooth=True;p.material_index=int(p.index>=24*4)
 vg=sleeve.vertex_groups.new(name='lowerarm02.'+side);vg.add(list(range(len(verts))),1,'REPLACE')
 mod=sleeve.modifiers.new('Forearm','ARMATURE');mod.object=arm
 hands.append((arm,obj,sleeve))
# Remove body and helpers, retaining only both real hand/forearm meshes and rigs.
keep={o for parts in hands for o in parts}
for obj in list(bpy.data.objects):
 if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
# Repack only the used hand skin into a 1K atlas; the full-body source stays offline.
uvnode=skin.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='SourceUV'
skin.node_tree.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
atlas=bpy.data.images.new('MakeHuman hand atlas',width=1024,height=1024,alpha=False)
atlas_node=skin.node_tree.nodes.new('ShaderNodeTexImage');atlas_node.image=atlas
skin.node_tree.nodes.active=atlas_node
bpy.ops.object.select_all(action='DESELECT')
for arm,mesh,sleeve in hands:
 mesh.data.uv_layers.active.name='SourceUV'
 mesh.data.uv_layers.new(name='HandAtlas');mesh.data.uv_layers.active_index=1
 mesh.data.uv_layers['HandAtlas'].active_render=True
 mesh.select_set(True)
bpy.context.view_layer.objects.active=hands[0][1]
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1
bpy.context.scene.render.bake.margin=8
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'})
atlas.filepath_raw=str(ROOT/'assets/source/makehuman-hands-color.png');atlas.file_format='PNG';atlas.save();atlas.pack()
tex.image=atlas;uvnode.uv_map='HandAtlas';skin.node_tree.nodes.remove(atlas_node);bpy.data.images.remove(texture)
for arm,mesh,sleeve in hands:mesh.data.uv_layers.remove(mesh.data.uv_layers['SourceUV'])

# Bake authored reach, support, lift, release and retreat onto the original bones.
def ease(t,a,b):
 u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def angle(t):
 return SEQUENCE['coverLift'][2]*ease(t,*SEQUENCE['coverLift'][:2])+SEQUENCE['coverSettle'][2]*ease(t,*SEQUENCE['coverSettle'][:2])
def pose(arm,side,t):
 right=side=='R';reach=ease(t,*SEQUENCE['reach']);release=ease(t,*SEQUENCE['release'])
 retreat=ease(t,*SEQUENCE['retreat']) if right else ease(t,*SEQUENCE['supportRetreat'])
 grip=ease(t,*SEQUENCE['grip'])*(1-release if right else 1-ease(t,*SEQUENCE['supportRelease']))
 a=angle(min(t,SEQUENCE['coverLift'][1])) if right else 0
 r=Matrix.Rotation(-a,4,'Y') if right else Matrix.Rotation(-.90,4,'Y')
 contact=Vector((.34,-.575,.285)) if right else Vector((-.455,-.61,.17))
 hinge=Vector((-.365,0,.17))
 wrist=hinge+r@(contact-hinge) if right else contact
 # Right hand stops following the cover as it passes vertical, then withdraws to its own side.
 if right:
  wrist += Vector((.26*release+.32*retreat,-.05*release-.44*retreat,-.03*release-.68*retreat))
  r=Matrix.Rotation(-a*(1-.82*retreat),4,'Y') @ Matrix.Rotation(.09*release,4,'X')
 else:
  wrist += Vector((-.17*retreat,-.43*retreat,-.30*retreat))
 wrist+=Vector(((1 if right else -1)*.10*(1-reach),-.54*(1-reach),-.28*(1-reach)))
 # The proximal arm keeps reaching out of the bottom of the frame; wrist orientation is independent.
 fore=arm.pose.bones['lowerarm02.'+side];rest=fore.bone
 elbow=Vector(((.24+wrist.x*.45 if right else -.64),-1.03-.54*(1-reach)-.44*retreat,wrist.z*.25-.12))
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
   if digit==1:
    bend=[.10,.10,.06][joint-1]+grip*([.22,.12,.10] if right else [.04,.06,.04])[joint-1]
   else:
    idle={2:[.05,.05,.02],3:[.05,.06,.03],4:[.10,.12,.06],5:[.18,.22,.12]}[digit][joint-1]
    close={2:[.03,.04,.03],3:[.03,.03,.02],4:[.02,.03,.02],5:[.05,.05,.03]}[digit][joint-1]
    bend=idle+grip*close
   b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(local@Vector((-1,0,0)),bend)
   if digit==1 and joint==1:
    b.rotation_quaternion=Quaternion(local@Vector((0,-1 if right else 1,0)),grip*(.65 if right else .03))@b.rotation_quaternion
   if digit>1 and joint==1:
    spread={2:-.055,3:0,4:.055,5:.16}[digit]*(1 if right else -1)
    b.rotation_quaternion=Quaternion(local@Vector((0,0,1)),spread)@b.rotation_quaternion
 for b in arm.pose.bones:
  b.rotation_mode='QUATERNION'
  b.keyframe_insert(data_path='location',frame=round(t*SEQUENCE['fps']))
  b.keyframe_insert(data_path='rotation_quaternion',frame=round(t*SEQUENCE['fps']))
  b.keyframe_insert(data_path='scale',frame=round(t*SEQUENCE['fps']))
scene=bpy.context.scene;scene.render.fps=SEQUENCE['fps'];scene.frame_start=0;scene.frame_end=round(SEQUENCE['duration']*SEQUENCE['fps'])
for arm,mesh,sleeve in hands:
 for frame in range(scene.frame_end+1):pose(arm,'R' if arm.name.startswith('Right') else 'L',frame/SEQUENCE['fps'])
 arm.animation_data.action.name='OpenBook'+arm.name
scene.frame_set(0)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/makehuman-hands.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/models/makehuman-hands.glb'),export_format='GLB',export_image_format='JPEG',export_jpeg_quality=88,use_selection=True,export_apply=False,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_force_sampling=True,export_frame_range=True,export_skins=True,export_all_influences=False,export_cameras=False,export_lights=False)
provenance_path=ROOT/'assets/source/makehuman-hands.json'
provenance=json.loads(provenance_path.read_text())
for entry in provenance['files']:
 data=(ROOT/entry['path']).read_bytes();entry.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
provenance['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print('HANDS',[(a.name,len(m.data.vertices),len(a.data.bones)) for a,m,s in hands])
# Neutral-light anatomy evidence, posed side by side with no book to hide the silhouette.
for (arm,_,_),off in zip(hands,[.13,-.13]):
 arm.data.pose_position='REST';arm.location.x=off
bpy.ops.object.camera_add(location=(0,.12,1.12));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-.03,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.62;bpy.context.scene.camera=camera
for name,loc,power,size in [('Key',(-.5,.4,.8),45,.7),('Fill',(.5,-.2,.4),12,.6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.18,.18,.18)
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'evidence/v014-free-hands/01-source-anatomy.png');bpy.ops.render.render(write_still=True)
