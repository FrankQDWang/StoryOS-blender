"""Render real hand/sleeve geometry for shape review; never saves runtime assets."""
from pathlib import Path
import bpy, sys, json
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
baseline='baseline' in args
clay='clay' in args
source=ROOT/('downloads/mage-hands/baseline/assets/source/makehuman-hands.blend' if baseline else 'assets/source/makehuman-hands.blend')
bpy.ops.wm.open_mainfile(filepath=str(source))
scene=bpy.context.scene
scene.frame_set(0)
for arm in [o for o in bpy.data.objects if o.type=='ARMATURE']:
    arm.data.pose_position='REST'
    arm.animation_data_clear()
    arm.matrix_world=Matrix.Identity(4)
for o in list(bpy.data.objects):
    if not o.name.startswith('Right'):
        bpy.data.objects.remove(o,do_unlink=True)
    elif o.type=='MESH':
        o.modifiers.clear()
        o.matrix_world=Matrix.Identity(4)
        if clay:
            m=bpy.data.materials.new('Review clay '+o.name);m.use_nodes=True
            p=m.node_tree.nodes.get('Principled BSDF')
            p.inputs['Base Color'].default_value=(.48,.37,.29,1) if o.name.endswith('Skin') else (.06,.085,.12,1)
            p.inputs['Roughness'].default_value=.7
            o.data.materials.clear();o.data.materials.append(m)
            for f in o.data.polygons:f.material_index=0
scene.world=bpy.data.worlds.new('Review studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.12,.15,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
target=Vector((0,-.08,0))
bpy.ops.object.camera_add(location=(.20,.19,.91))
camera=bpy.context.object;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=.68;scene.camera=camera
for loc,power,size in [((-.4,.25,.7),45,.55),((.5,.0,.55),25,.5),((-.2,-.5,.5),18,.35)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size
    lamp.rotation_euler=(target-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
name=('before' if baseline else 'after')+('-clay' if clay else '-material')+'-model.png'
scene.render.filepath=str(OUT/name)
bpy.ops.render.render(write_still=True)
print('Rendered',name)
