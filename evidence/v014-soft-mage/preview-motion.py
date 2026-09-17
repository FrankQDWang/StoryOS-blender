"""Fast motion candidate export from current authored surfaces; no source save."""
from pathlib import Path
import sys,bpy
ROOT=Path(__file__).resolve().parents[2];sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'scripts'))
from mage_opening_motion import pose
from midnight_robe import bake_robe_deformation
from refine_mage_hands import bake_hand_correctives
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/source/makehuman-hands.blend'))
scene=bpy.context.scene;scene.frame_set(0)
for side,label in [('R','Right'),('L','Left')]:
 arm=bpy.data.objects[label+'Hand'];mesh=bpy.data.objects[label+'Skin'];arm.animation_data_clear()
 for f in range(106):
  pose(arm,side,f/30);bake_hand_correctives(mesh,arm,side,f)
 arm.animation_data.action.name='OpenBook'+label+'Hand'
# Cloth bake writes provenance; copy metadata first and restore after this trial.
p=ROOT/'assets/source/midnight-robe-provenance.json';before=p.read_bytes()
for side,label in [('R','Right'),('L','Left')]:
 arm=bpy.data.objects[label+'Hand'];robes=[o for o in arm.children if o.type=='MESH' and not o.name.endswith('Skin')]
 bake_robe_deformation(arm,robes,root=ROOT)
p.write_bytes(before)
scene.frame_set(0);bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/models/makehuman-hands.glb'),export_format='GLB',export_image_format='AUTO',export_jpeg_quality=88,use_selection=True,export_apply=False,export_morph_normal=False,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_force_sampling=True,export_frame_range=True,export_skins=True,export_all_influences=False,export_cameras=False,export_lights=False)
