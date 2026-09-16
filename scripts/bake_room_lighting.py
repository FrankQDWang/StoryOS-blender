"""Bake spatial direct/indirect illumination and local occlusion, preserving 3D geometry.
Base colour keeps its original UVs. The second UV set is unique across the room.
Run after build_library.py; the source .blend remains untouched.
"""
import bpy, math, json, time, argparse, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser();args.add_argument('--size',type=int,default=4096);args.add_argument('--samples',type=int,default=128)
args=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
started=time.time()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/source/storyos-library.blend'))
scene=bpy.context.scene;layout=json.loads((ROOT/'apps/web/src/room-layout.json').read_text())
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.refresh_devices()
for device in prefs.devices:device.use=device.type=='METAL'
scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=args.samples
scene.cycles.max_bounces=5;scene.cycles.diffuse_bounces=4;scene.cycles.glossy_bounces=1
scene.render.bake.margin=12
scene.world.color=(.02,.025,.04)
for collection_name in ['Book','Hands']:
 for asset in bpy.data.collections[collection_name].objects:asset.hide_render=True
# Bake the stable illumination; the runtime adds the changing fire contribution.
hearth=next(f for f in layout['fixtures'] if f['id']=='hearth')['center']
desk=next(f for f in layout['fixtures'] if f['id']=='desk')['center']
settings={
 'Window moon':((0,3.8,2.9),(.22,.36,.85),120,.8),
 'Hearth':((hearth[0]+.35,-hearth[1],.8),(1,.40,.12),190,.45),
 'Desk amber':((desk[0]-.68,-desk[1]-.06,1.70),(1,.63,.30),45,.20),
 'Left wall lamp':((-3.9,-2.1,2.5),(1,.60,.30),40,.3),
 'Right wall lamp':((3.9,-2.1,2.5),(1,.60,.30),45,.3),
 'Right rear lamp':((3.9,2.95,2.5),(1,.62,.35),45,.3),
 'Magic glow':((0,-.6,1.45),(.27,.55,.54),2,.3),
}
for name,(position,color,power,radius) in settings.items():
 o=bpy.data.objects.get(name)
 if o:o.location=position;o.data.color=color;o.data.energy=power;o.data.shadow_soft_size=radius
# Every input texture explicitly uses the pre-existing surface UV before unwrapping.
room=bpy.data.collections['Room']
materials=set()
for obj in room.objects:
 if obj.type!='MESH':continue
 uv=obj.data.uv_layers.active
 if not uv:uv=obj.data.uv_layers.new(name='SurfaceUV')
 uv.name='SurfaceUV';uv.active_render=True
 for extra in list(obj.data.uv_layers):
  if extra.name!='SurfaceUV':obj.data.uv_layers.remove(extra)
 materials.update(m for m in obj.data.materials if m)
for mat in materials:
 nodes=mat.node_tree.nodes;links=mat.node_tree.links
 uv=nodes.new('ShaderNodeUVMap');uv.uv_map='SurfaceUV'
 for node in list(nodes):
  if node.type=='TEX_IMAGE' and node.image:links.new(uv.outputs['UV'],node.inputs['Vector'])
# Global atlas, then split back by material at export for readable material ownership.
bpy.ops.object.select_all(action='DESELECT')
objects=[o for o in room.objects if o.type=='MESH']
for o in objects:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
obj=bpy.context.object;obj.name='RoomLightmap'
obj.data.uv_layers.new(name='LightingUV');obj.data.uv_layers.active=obj.data.uv_layers['LightingUV']
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(72),island_margin=.003,area_weight=.1,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
# All bake targets share one UV atlas. No front-view projection or raster backdrop.
images={}
for name,bake_type in [('room-occlusion','EMIT'),('room-illumination','DIFFUSE')]:
 image=bpy.data.images.new(name,width=args.size,height=args.size,alpha=False,float_buffer=bake_type=='DIFFUSE')
 image.colorspace_settings.name='Non-Color'
 for mat in materials:
  node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.name='BakeTarget_'+name;node.image=image
  mat.node_tree.nodes.active=node
 restore=[]
 if bake_type=='EMIT':
  for mat in materials:
   nodes=mat.node_tree.nodes;links=mat.node_tree.links
   output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
   restore.append((mat,output.inputs['Surface'].links[0].from_socket,output.inputs['Surface']))
   ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.65;ao.samples=32
   emission=nodes.new('ShaderNodeEmission');links.new(ao.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
 scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;scene.render.bake.use_pass_color=False
 print('BAKE_START',name,flush=True)
 bpy.ops.object.bake(type=bake_type)
 for mat,source,target in restore:mat.node_tree.links.new(source,target)
 image.filepath_raw=str(ROOT/'public/assets/textures'/f'{name}.png');image.file_format='PNG';image.save()
 images[name]=image
 print('BAKE_SAVED',name,time.time()-started,flush=True)
# Advertise the second UV through the standard glTF occlusion channel.
group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
for mat in materials:
 nodes=mat.node_tree.nodes;links=mat.node_tree.links
 uv=nodes.new('ShaderNodeUVMap');uv.uv_map='LightingUV'
 image_node=nodes.new('ShaderNodeTexImage');image_node.image=images['room-occlusion']
 links.new(uv.outputs['UV'],image_node.inputs['Vector'])
 output=nodes.new('ShaderNodeGroup');output.node_tree=group;links.new(image_node.outputs['Color'],output.inputs['Occlusion'])
obj.data.uv_layers['SurfaceUV'].active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
for o in room.objects:
 if o.type=='MESH':o.name='Room_'+o.active_material.name;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/models/library-room.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
report={'source':'scripts/bake_room_lighting.py','source_blend':'assets/source/storyos-library.blend','version':layout['version'],'atlas_size':args.size,'samples':args.samples,'device':'Metal','duration_seconds':round(time.time()-started,2),'passes':['local ambient occlusion (0.65 m)','direct and indirect diffuse illumination without albedo'],'uv':'LightingUV / TEXCOORD_1','image_paths':[f'public/assets/textures/{n}.png' for n in images],'room_is_full_3d':True}
(ROOT/'assets/source/room-lighting.json').write_text(json.dumps(report,indent=2)+'\n')
print('BAKE_FINISHED',json.dumps(report),flush=True)
