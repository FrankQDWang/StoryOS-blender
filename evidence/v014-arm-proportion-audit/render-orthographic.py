"""Render saved rest meshes at identical physical scale. No asset save/export."""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/v014-arm-proportion-audit'
paths=['assets/source/makehuman-hands.blend','assets/vendor/makehuman/base-human.blend','public/assets/models/makehuman-hands.glb']
checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
profile=json.loads((ROOT/'apps/web/src/opening-anatomy.json').read_text());S=profile['referenceBookScale']
bpy.ops.wm.open_mainfile(filepath=str(ROOT/paths[0]))

def mat(name,color,roughness=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness
 return m
skin=mat('Neutral anatomical clay',(.48,.37,.29));cloth=mat('Neutral dark sleeve',(.075,.14,.17),.85)
keep=[]
for name in ['RightSkin','RightSleeve']:
 old=bpy.data.objects[name];new=old.copy();new.data=old.data.copy();new.name='Audit '+name;new.parent=None;new.matrix_world=Matrix.Identity(4);new.animation_data_clear();new.modifiers.clear()
 new.data.transform(Matrix.Scale(S,4));new.location.x=-.145
 new.data.materials.clear();new.data.materials.append(skin if name.endswith('Skin') else cloth)
 for p in new.data.polygons:p.material_index=0;p.use_smooth=True
 bpy.context.collection.objects.link(new);keep.append(new)
for obj in list(bpy.data.objects):
 if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
with bpy.data.libraries.load(str(ROOT/paths[1]),link=False) as (src,dest):
 dest.objects=['MakeHumanSource','MakeHumanRig']
for obj in dest.objects:
 bpy.context.collection.objects.link(obj)
human=bpy.data.objects['MakeHumanSource'];rig=bpy.data.objects['MakeHumanRig']
rig.data.pose_position='REST';bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(human.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
wrist=rig.data.bones['wrist.R'].head_local.copy();forward=(rig.data.bones['finger3-1.R'].head_local-wrist).normalized()
radial=rig.data.bones['finger2-1.R'].head_local-rig.data.bones['finger5-1.R'].head_local;radial=(radial-forward*radial.dot(forward)).normalized()
x=-radial;z=x.cross(forward).normalized();basis=Matrix((x,forward,z))
factor=1.3*profile['handLengthMetres']/(.22225145995616913*S)*S
transform=Matrix.Scale(factor,4)@basis.to_4x4()@Matrix.Translation(-wrist)
allowed={v.index for v in mesh.vertices if sum(g.weight for g in v.groups if human.vertex_groups[g.group].name.endswith('.R') and human.vertex_groups[g.group].name.startswith(('lowerarm','upperarm','wrist','finger','metacarpal')))>.5}
indices=sorted(allowed);remap={i:j for j,i in enumerate(indices)}
verts=[transform@mesh.vertices[i].co for i in indices]
faces=[tuple(remap[i] for i in p.vertices) for p in mesh.polygons if all(i in remap for i in p.vertices)]
bare_mesh=bpy.data.meshes.new('Source bare arm rest');bare_mesh.from_pydata(verts,[],faces);bare_mesh.materials.append(skin)
bare=bpy.data.objects.new('Source bare arm rest',bare_mesh);bpy.context.collection.objects.link(bare);bare.location.x=.145
for p in bare_mesh.polygons:p.use_smooth=True
bpy.data.objects.remove(human,do_unlink=True);bpy.data.objects.remove(rig,do_unlink=True)
# Orthographic top view. Camera cropping, not altered mesh, limits the proximal sleeve.
scene=bpy.context.scene
scene.world=bpy.data.worlds.new('Audit world');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.13,.14,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
bpy.ops.object.camera_add(location=(0,-.045,2.0));camera=bpy.context.object;camera.rotation_euler=(Vector((0,-.045,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=.55;scene.camera=camera
for loc,power,size in [((-.35,.1,.75),38,.7),((.5,-.1,.6),20,.6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size;lamp.rotation_euler=(Vector((0,-.05,0))-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(OUT/'orthographic-current-vs-source.png');bpy.ops.render.render(write_still=True)
assert checks=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
(OUT/'orthographic-render.json').write_text(json.dumps({'left':'Current saved RightSkin and RightSleeve rest mesh, runtime reference scale 0.824. Modifiers removed on in-memory copies to display rest vertices.','right':'Evaluated MakeHumanSource right arm mesh, same transform and hand scale, same-side arm-weight filter >0.5. No anatomy edits.','camera':'Orthographic dorsal projection, same physical scale in both columns, proximal sleeve/body crop is camera framing only.','materials':'Uniform neutral clay for both skins and dark plain cloth to compare geometry, no baked skin color texture.','image':'orthographic-current-vs-source.png','limits':['This is a diagnostic neutral-pose model render, not the runtime camera, animation or accepted design.','Current hand is pre-subdivided while source body keeps its evaluated topology; both have smooth shading.','The far proximal proxy continues beyond frame; image crop does not imply a complete fitted anatomical sleeve.'],'inputs_unchanged':True},ensure_ascii=False,indent=2)+'\n')
print('AUDIT_RENDER_COMPLETE')
