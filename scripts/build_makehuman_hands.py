"""Adapt CC0 MakeHuman anatomy and its original skin weights, without remeshing.

Uses assets/vendor/makehuman/base-human.blend, produced with the pinned MPFB source.
No changes to the approved room or book assets. Metres, Z up in Blender.
"""
from pathlib import Path
import bpy, bmesh, json, math, hashlib, sys
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'scripts'))
from midnight_robe import build_robe, bake_robe_deformation
from refine_mage_hands import refine_hand_shape, configure_hand_material, add_hand_correctives, bake_hand_correctives, HAND_REFINEMENT_METADATA
# Mesh dimensions are authored for the first lectern; runtime cancels other book scales.
ANATOMY=json.loads((ROOT/'apps/web/src/opening-anatomy.json').read_text())
REFERENCE_BOOK_SCALE=ANATOMY['referenceBookScale']
HAND_LENGTH=ANATOMY['handLengthMetres']
ANATOMY_SCALE=HAND_LENGTH/(.22225145995616913*REFERENCE_BOOK_SCALE)
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
texture=bpy.data.images.load(str(ROOT/'assets/vendor/makehuman/Aksel_Skin_diffuse.png'))
texture.pack()
tex=skin.node_tree.nodes.new('ShaderNodeTexImage');tex.image=texture
skin.node_tree.links.new(tex.outputs['Color'],skin.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
# Fingernails are part of the original human topology/UV, not added primitive meshes.
hands=[];shape_changes=[];corrective_setup=[]
for side,label in [('R','Right'),('L','Left')]:
 wrist=source_rig.data.bones['wrist.'+side].head_local.copy()
 forward=(source_rig.data.bones['finger3-1.'+side].head_local-wrist).normalized()
 radial=source_rig.data.bones['finger2-1.'+side].head_local-source_rig.data.bones['finger5-1.'+side].head_local
 radial=(radial-forward*radial.dot(forward)).normalized()
 x=radial*(-1 if side=='R' else 1); z=x.cross(forward).normalized()
 basis=Matrix((x,forward,z)); transform=Matrix.Scale(1.3*ANATOMY_SCALE,4) @ basis.to_4x4() @ Matrix.Translation(-wrist)
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
 # Side cut excludes the rest of the body, retaining the original hand topology.
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
 shape_changes.append(refine_hand_shape(obj,arm,side))
 obj.data.materials.clear();obj.data.materials.append(skin)
 for f in obj.data.polygons:f.use_smooth=True
 modifier=obj.modifiers.new('Original MakeHuman skinning','ARMATURE');modifier.object=arm
 # One subdivision keeps the carefully authored knuckle loops smooth at close range.
 bpy.context.view_layer.objects.active=obj
 sub=obj.modifiers.new('Surface refinement','SUBSURF');sub.levels=1
 # Apply before export while retaining the source deformation weights.
 obj.modifiers.move(len(obj.modifiers)-1,0)
 bpy.ops.object.modifier_apply(modifier=sub.name)
 corrective_setup.append(add_hand_correctives(obj,arm,side))
 robes=build_robe(arm,side,label,ROOT)
 hands.append((arm,obj,robes))
# Remove body and helpers, retaining only both real hand/forearm meshes and rigs.
keep={o for arm,mesh,robes in hands for o in [arm,mesh,*robes]}
for obj in list(bpy.data.objects):
 if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
# Repack only the used hand skin; the full-body source stays offline.
uvnode=skin.node_tree.nodes.new('ShaderNodeUVMap');uvnode.uv_map='SourceUV'
skin.node_tree.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
atlas=bpy.data.images.new('MakeHuman hand atlas',width=2048,height=2048,alpha=False)
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
bpy.context.scene.render.bake.margin=12
bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'})
atlas.filepath_raw=str(ROOT/'assets/source/makehuman-hands-color.png');atlas.file_format='PNG';atlas.save();atlas.pack()
tex.image=atlas;uvnode.uv_map='HandAtlas';skin.node_tree.nodes.remove(atlas_node);bpy.data.images.remove(texture)
surface_changes=configure_hand_material(skin,ROOT)
for arm,mesh,sleeve in hands:mesh.data.uv_layers.remove(mesh.data.uv_layers['SourceUV'])
# Keep the lossless authored atlas offline; embed a JPEG colour derivative.
# Normal/roughness maps remain PNG so tangent-space data is not JPEG-compressed.
runtime_atlas=atlas.copy();runtime_atlas.filepath_raw=str(ROOT/'assets/source/makehuman-hands-color.jpg')
runtime_atlas.file_format='JPEG';runtime_atlas.save()
bpy.data.images.remove(runtime_atlas)
runtime_atlas=bpy.data.images.load(str(ROOT/'assets/source/makehuman-hands-color.jpg'));runtime_atlas.pack()
tex.image=runtime_atlas

from mage_opening_motion import pose
scene=bpy.context.scene;scene.render.fps=SEQUENCE['fps'];scene.frame_start=0;scene.frame_end=round(SEQUENCE['duration']*SEQUENCE['fps'])
for arm,mesh,sleeve in hands:
 for frame in range(scene.frame_end+1):
  side='R' if arm.name.startswith('Right') else 'L'
  pose(arm,side,frame/SEQUENCE['fps'])
  bake_hand_correctives(mesh,arm,side,frame)
 arm.animation_data.action.name='OpenBook'+arm.name
cloth_changes=[bake_robe_deformation(arm,robes,fps=SEQUENCE['fps'],frame_start=0,frame_end=scene.frame_end,root=ROOT) for arm,mesh,robes in hands]
scene.frame_set(0)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/makehuman-hands.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/models/makehuman-hands.glb'),export_format='GLB',export_image_format='AUTO',export_jpeg_quality=88,use_selection=True,export_apply=False,export_morph_normal=False,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_force_sampling=True,export_frame_range=True,export_skins=True,export_all_influences=False,export_cameras=False,export_lights=False)
provenance_path=ROOT/'assets/source/makehuman-hands.json'
provenance=json.loads(provenance_path.read_text())
provenance['atlas']=[2048,2048]
provenance['visual_target']='design/round-07-wizard-robes/02-midnight-tower-mage.png'
provenance['shape_refinement']=shape_changes
provenance['surface_refinement']=surface_changes
provenance['hand_refinement_design']=HAND_REFINEMENT_METADATA
provenance['skin_correctives']=corrective_setup
provenance['cloth_deformation']=cloth_changes
provenance['costume']='assets/source/midnight-robe-provenance.json'
provenance['adaptations']=[
 'CC0 MakeHuman topology and original weights retained; source UV correspondence rebaked into HandAtlas; one subdivision',
 'Anatomical dorsal/palmar sculpt and five flexion-driven skin corrective morphs per hand',
 '0.195 m hand length at reference book scale 0.824; runtime cancels per-lectern book scaling',
 'Single midnight-blue lined robe with celestial embroidery; rejected teal inner sleeve removed',
 '2K hand-only color atlas, roughness and subtle normal detail; standard glTF material channels',
 'Large-folio lower-edge support opening authored for existing 3.5 s cover/page timing; 24 gravity/inertia cloth bones per arm',
 'Proximal camera sleeve remains a proxy, not a complete shoulder/elbow body'
]
extra=[ROOT/'scripts/mage_opening_motion.py',ROOT/'scripts/refine_mage_hands.py',ROOT/'scripts/midnight_robe.py',ROOT/'assets/source/makehuman-hands-color.jpg',*sorted((ROOT/'assets/source').glob('mage-hand-*.png')),*sorted((ROOT/'assets/source').glob('mage-hand-*.jpg')),*(ROOT/entry['path'] for entry in json.loads((ROOT/'assets/source/midnight-robe-provenance.json').read_text())['textures']),ROOT/'assets/source/midnight-robe-provenance.json']
provenance['files']=[entry for entry in provenance['files'] if entry['path']!='assets/source/midnight-robe-inner-jacquard-color.png']
known={entry['path'] for entry in provenance['files']}
for path in extra:
 if path.exists() and str(path.relative_to(ROOT)) not in known:provenance['files'].append({'path':str(path.relative_to(ROOT))})
for entry in provenance['files']:
 data=(ROOT/entry['path']).read_bytes();entry.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
provenance['generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
provenance_path.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
print('HANDS',[(a.name,len(m.data.vertices),len(a.data.bones)) for a,m,s in hands])
# Optional anatomy capture: ordinary rebuilds must not overwrite historical QA evidence.
if '--anatomy-output' in sys.argv:
 for (arm,_,_),off in zip(hands,[.13,-.13]):
  arm.data.pose_position='REST';arm.location.x=off
 bpy.ops.object.camera_add(location=(0,.12,1.12));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-.03,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.62;bpy.context.scene.camera=camera
 for name,loc,power,size in [('Key',(-.5,.4,.8),45,.7),('Fill',(.5,-.2,.4),12,.6)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(-l.location).to_track_quat('-Z','Y').to_euler()
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.color=(.18,.18,.18)
 scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
 scene.render.filepath=str(ROOT/sys.argv[sys.argv.index('--anatomy-output')+1]);bpy.ops.render.render(write_still=True)
