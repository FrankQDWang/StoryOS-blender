"""Reproducible sculpted room, reusable book and hands. Blender 5.x, metres.
Blender world: X right, Y into room, Z up. glTF converts to Y up.
Generated texture provenance is in assets/source/*-texture.json.
"""
import bpy, math, random, json, os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]; random.seed(24)
OUT=R/'public/assets/models'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection': bpy.data.collections.remove(c)
root=bpy.context.scene.collection

def collection(n):
 c=bpy.data.collections.new(n);root.children.link(c);return c
ROOM=collection('Room'); BOOK=collection('Book'); HANDS=collection('Hands'); active=ROOM

def put(o,n,mat=None):
 o.name=n
 for c in list(o.users_collection):c.objects.unlink(o)
 active.objects.link(o)
 if mat:o.data.materials.append(mat)
 return o

def mat(n,c,rough=.8,metal=0,tex=None,emit=0):
 m=bpy.data.materials.new(n);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'public/assets/textures'/tex),check_existing=True)
  m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  # glTF supports image textures; runtime applies the tint recorded here.
  m['runtimeTint']=list(c)
 return m
wood=mat('Timber',(.37,.21,.105),.92,tex='sculpted-wood.png')
floor=mat('FloorWood',(.54,.37,.215),.92,tex='sculpted-wood.png')
plaster=mat('WarmPlaster',(.54,.43,.32),.96,tex='sculpted-plaster.png')
stone=mat('Stone',(.20,.24,.255),.98,tex='sculpted-plaster.png')
dark=mat('DarkTimber',(.10,.064,.038),.9)
brass=mat('OldBrass',(.43,.29,.105),.35,.72)
iron=mat('Iron',(.055,.065,.071),.7,.45)
rug=mat('WovenRug',(.18,.087,.056),1)
trim=mat('RugBorder',(.33,.24,.135),1)
teal=mat('Velvet',(.065,.14,.135),1)
wax=mat('Wax',(.68,.46,.23),.9)
flame=mat('Flame', (1,.49,.13),.5,emit=4)
blue=mat('NightGlass',(.025,.11,.19),.7,emit=.9)
black=mat('Black',(.008,.014,.02),1)

# Low-sided, bevelled silhouettes keep the material and shape readable.
def cube(n,p,s,m,bevel=.025,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=put(bpy.context.object,n,m);o.scale=s
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if rot:o.rotation_euler=rot
 if bevel:
  mod=o.modifiers.new('soft carved edges','BEVEL');mod.width=bevel;mod.segments=2
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('weighted corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return o

def uv_sphere(n,p,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=p);o=put(bpy.context.object,n,m);o.scale=s
 for f in o.data.polygons:f.use_smooth=True
 return o

def cyl(n,p,r,depth,m,vertices=24,r2=None):
 if r2 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p)
 else:bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r2,depth=depth,location=p)
 return put(bpy.context.object,n,m)

def line(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=8;c.bevel_depth=r;c.bevel_resolution=2
 sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for b,co in zip(sp.bezier_points,pts):b.co=co;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);active.objects.link(o);c.materials.append(m)
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def ring(n,p,r,t,m):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=t,major_segments=48,minor_segments=6,location=p);return put(bpy.context.object,n,m)

def light(n,p,color,power,radius):
 data=bpy.data.lights.new(n,'POINT');data.color=color;data.energy=power;data.shadow_soft_size=radius
 o=bpy.data.objects.new(n,data);root.objects.link(o);o.location=p

def candle(x,y,z,h=.20):
 cyl('candle holder',(x,y,z),.085,.045,brass)
 cyl('candle',(x,y,z+h/2),.037,h,wax)
 uv_sphere('flame',(x,y,z+h+.035),(.014,.014,.042),flame)

def lantern(x,y,z):
 cyl('lantern base',(x,y,z),.16,.065,iron)
 cyl('lantern crown',(x,y,z+.36),.20,.17,iron,r2=.06)
 for a in range(4):
  ang=a*math.pi/2+math.pi/4;line('lantern cage',[(x+.13*math.cos(ang),y+.13*math.sin(ang),z),(x+.13*math.cos(ang),y+.13*math.sin(ang),z+.31)],.011,iron)
 candle(x,y,z+.04,.19)
 ring('lantern loop',(x,y,z+.49),.05,.012,iron).rotation_euler[0]=math.pi/2

# Plank floor with controlled rhythm and a few slightly uneven joints.
cube('floor foundation',(0,-1.2,-.18),(9.8,12,.25),dark)
for row in range(15):
 x=-4.48+row*.64
 for seg in range(4):
  y=-5.95+seg*2.9
  cube('floor plank',(x+random.uniform(-.008,.008),y, -.025+random.uniform(-.004,.004)),(.62,2.875,.12),floor,.018)
# Side walls and back wall, back has an architectural window opening.
cube('left wall',(-4.8,-1.25,2.2),(.35,12,4.6),plaster,.08)
cube('right wall',(4.8,-1.25,2.2),(.35,12,4.6),plaster,.08)
cube('back lower',(0,4.55,.64),(9.8,.35,1.36),plaster,.065)
cube('back upper',(0,4.55,4.05),(9.8,.35,1.25),plaster,.07)
cube('back left',(-3.06,4.55,2.42),(3.68,.35,2.25),plaster,.065)
cube('back right',(3.06,4.55,2.42),(3.68,.35,2.25),plaster,.065)
# Ceiling and mildly bent beams.
cube('ceiling',(0,-1.25,4.58),(9.85,12,.3),plaster,.12)
for y in [-6.7,-3.8,-.9,2.0,4.35]:
 line('bent crossbeam',[(-4.55,y,3.55),(-3.8,y,4.08),(-2.1,y,4.28),(0,y,4.32),(2.1,y,4.28),(3.8,y,4.08),(4.55,y,3.55)],.125,wood)
 for x in [-4.55,4.55]:
  line('upright',[(x,y,.12),(x+.035,y,1.9),(x,y,3.6)],.125,wood)
  cube('post foot',(x,y,.22),(.37,.34,.4),wood,.04)
for x in [-3,-1.5,0,1.5,3]:cube('ceiling runner',(x,-1.2,4.43),(.13,11.75,.15),wood,.02)
for x in [-4.55,4.55]:
 for z in [.25,1.0,3.45]:cube('wall rail',(x,-1.25,z),(.18,11.65,.14),wood,.03)
for z in [.23,1.04,3.64]:cube('back rail',(0,4.31,z),(9.2,.2,.13),wood)
# Window: rounded arch with leaded panes and a deep sill.
cube('night pane',(0,4.49,2.48),(2.4,.06,2.25),blue,.06)
for x in [-1.22,1.22]:cube('window jamb',(x,4.25,2.48),(.18,.38,2.46),wood,.045)
cube('window sill',(0,4.12,1.30),(2.85,.64,.18),wood,.05)
for x in [-.6,0,.6]:cube('window mullion',(x,4.23,2.5),(.045,.08,2.2),iron,.008)
for z in [1.95,2.7,3.45]:cube('window lead',(0,4.23,z),(2.4,.08,.038),iron,.006)
# Arch shaped frame inset within the architectural opening.
line('window arch',[(-1.2,4.10,2.45),(-1.06,4.10,3.22),(0,4.10,3.56),(1.06,4.10,3.22),(1.2,4.10,2.45)],.09,wood)
# A small writing nook below the window.
cube('writing desk',(0,3.66,.94),(2.6,.86,.16),wood,.055)
for x in [-1.08,1.08]:
 for y in [3.35,3.97]:cube('desk leg',(x,y,.45),(.15,.14,.90),wood,.025,rot=(0,.07 if x>0 else -.07,0))
cube('desk apron',(0,3.25,.75),(2.32,.1,.25),wood,.04)
cube('drawer',(0,3.17,.76),(.75,.06,.18),dark,.025)
uv_sphere('drawer pull',(0,3.11,.76),(.03,.03,.03),brass)
lantern(-.94,3.60,1.06)
# Ink and an unlettered paper, no litter across the floor.
cyl('inkwell',(.81,3.67,1.07),.065,.12,iron)
line('quill',[(.81,3.67,1.13),(.90,3.73,1.46),(.99,3.77,1.60)],.007,trim)
paper=mat('Paper',(.69,.59,.39),.98)
cube('writing paper',(.17,3.58,1.035),(.50,.36,.006),paper,.003,rot=(0,0,.08))
# Chair, padded but sculptural.
for x in [-.28,.28]:
 for y in [2.35,2.84]:cube('chair leg',(x,y,.25),(.09,.09,.48),wood,.02)
cube('chair seat',(0,2.60,.51),(.73,.69,.16),teal,.085)
for x in [-.33,.33]:line('chair back post',[(x,2.28,.38),(x,2.20,1.2),(x*.85,2.27,1.45)],.05,wood)
line('chair back crown',[(-.3,2.25,1.35),(0,2.21,1.5),(.3,2.25,1.35)],.065,wood)
for x in [-.16,0,.16]:line('chair spindle',[(x,2.26,.6),(x,2.22,1.36)],.022,wood)
# A low stone hearth on the left; only a few logs and embers.
cube('hearth plinth',(-4.14,.9,.14),(1.13,1.85,.25),stone,.085)
cube('hearth back',(-4.55,.9,1.22),(.16,1.58,2.2),black,.02)
for y in [.08,1.72]:
 for z in [.48,.9,1.32,1.74]:cube('hearth stone',(-4.24+random.uniform(-.025,.025),y,z),(.66+random.uniform(-.04,.04),.28,.39),stone,.085,rot=(0,random.uniform(-.025,.025),random.uniform(-.018,.018)))
cube('mantel',(-4.21,.9,1.99),(.99,2.05,.19),wood,.05)
for y in [.35,.86,1.34]:
 o=cyl('log',(-4.19,y,.37),.10,.69,dark,10);o.rotation_euler[1]=math.pi/2
 uv_sphere('ember',(-4.14,y,.43),(.16,.105,.055),flame)
candle(-4.05,.22,2.10,.22);candle(-4.03,1.50,2.10,.30)
# Modest broad rug, geometry border instead of a dense patterned surface.
cube('rug',(0,-.58,.057),(3.68,3.50,.025),rug,.12)
for x in [-1.73,1.73]:cube('rug border',(x,-.58,.074),(.028,3.22,.006),trim,.003)
for y in [-2.2,1.03]:cube('rug border',(0,y,.074),(3.46,.028,.006),trim,.003)
# Central magic writing table, original reusable sculpted piece.
cyl('magic foot',(0,-.6,.19),.64,.22,wood,12,r2=.43)
cyl('magic stem',(0,-.6,.58),.23,.65,wood,10,r2=.32)
cyl('magic table edge',(0,-.6,.98),.92,.13,wood,48)
cyl('magic table inset',(0,-.6,1.057),.82,.036,dark,48)
ring('brass table ring',(0,-.6,1.08),.73,.011,brass)
ring('brass table ring',(0,-.6,1.08),.52,.006,brass)
for a in range(12):
 t=a*math.tau/12
 line('table radial',[(.64*math.cos(t),-.6+.64*math.sin(t),1.08),(.70*math.cos(t),-.6+.70*math.sin(t),1.08)],.006,brass)
# Five stable lecterns; positions are also exported to application metadata.
slots=[(-2.85,1.55,0),(-2.02,3.52,.15),(2.02,3.52,-.15),(3.02,1.22,-.22),(3.02,-1.34,-.32)]
for i,(x,y,ang) in enumerate(slots):
 cyl(f'lectern {i} base',(x,y,.15),.37,.15,wood,8,r2=.30)
 cyl(f'lectern {i} stem',(x,y,.66),.11,1.0,wood,8,r2=.16)
 for dx in [-.24,.24]:line('lectern support',[(x,y,.7),(x+dx,y,1.08),(x+dx*1.4,y,1.16)],.045,wood)
 cube(f'lectern {i} top',(x,y,1.18),(1.02,.81,.10),wood,.055,rot=(math.radians(16),0,ang))
 cube('book rest lip',(x,y-.38,1.13),(1.04,.07,.09),brass,.015)
# Restrained sconces with pools of warm light.
for x,y in [(-4.47,-2.1),(4.47,-2.1),(4.47,2.95)]:
 cube('sconce back',(x,y,2.3),(.10,.25,.46),wood,.08)
 inward=-1 if x>0 else 1
 line('sconce arm',[(x,y,2.1),(x+inward*.2,y,2.03),(x+inward*.35,y,2.16)],.025,iron)
 candle(x+inward*.35,y,2.17,.27)
# Reusable book, articulated cover and page groups; local origin at centre.
active=BOOK
leather=mat('BookLeather',(.16,.255,.23),.74)
gold=mat('BookGold',(.66,.43,.16),.34,.7)
pages=mat('BookPages',(.72,.61,.40),.93)
cube('BookBack',(0,0,.025),(.78,1.0,.065),leather,.018)
cube('BookBlock',(0,0,.105),(.71,.94,.115),pages,.013)
cube('BookSpine',(-.38,0,.12),(.075,1,.22),leather,.035)
for y in [-.36,-.18,.18,.36]:cube('SpineBand',(-.42,y,.12),(.025,.035,.20),gold,.01)
for z in [.060,.075,.09,.11,.13,.15]:
 cube('PageEdges',(.361,0,z),(.002,.88,.003),trim,.001)
 bpy.ops.object.select_all(action='DESELECT')
# Parent cover decoration preserving transforms, pivot at the spine.
pivot=bpy.data.objects.new('CoverPivot',None);BOOK.objects.link(pivot);pivot.location=(-.365,0,.17)
coverparts=[]
coverparts.append(cube('FrontCover',(0,0,.192),(.78,1.0,.065),leather,.022))
for x in [-.30,.30]:coverparts.append(cube('CoverInlay',(x,0,.229),(.009,.83,.008),gold,.003))
for y in [-.41,.41]:coverparts.append(cube('CoverInlay',(0,y,.229),(.60,.009,.008),gold,.003))
for x in [-.31,.31]:
 for y in [-.42,.42]:coverparts.append(cube('CoverCorner',(x,y,.232),(.13,.13,.015),gold,.009))
coverparts.append(ring('CoverSeal',(0,0,.237),.105,.008,gold))
for a in range(4):
 t=a*math.pi/2
 coverparts.append(line('CoverStar',[(0,0,.245),(.06*math.cos(t),.11*math.sin(t),.245)],.006,gold))
bpy.context.view_layer.update()
for o in coverparts:
 world=o.matrix_world.copy();o.parent=pivot;o.matrix_world=world
for k in range(3):
 pg=cube(f'TurnPage{k}',(-.004,0,.173+k*.003),(.70,.925,.002),pages,.001)
 # Keep each page hinged at the spine through an empty.
 pp=bpy.data.objects.new(f'PagePivot{k}',None);BOOK.objects.link(pp);pp.location=(-.345,0,.177+k*.003)
 bpy.context.view_layer.update();world=pg.matrix_world.copy();pg.parent=pp;pg.matrix_world=world
# Prebuilt simplified sculpted hands; finger segments and palm, no physics or IK.
active=HANDS
skin=mat('HandSkin',(.49,.28,.15),.92)
sleeve=mat('HandSleeve',(.07,.105,.115),.95)
for side in [-1,1]:
 name='Left' if side<0 else 'Right';x=side*.33
 uv_sphere(name+'Palm',(x,0,.02),(.083,.13,.040),skin)
 cube(name+'Cuff',(x,-.16,.02),(.19,.12,.09),sleeve,.025)
 for f in range(4):
  fx=x+(f-1.5)*.04;length=[.13,.17,.18,.145][f]
  line(name+'Finger',[(fx,.08,.025),(fx,.08+length*.55,.015),(fx,.08+length,-.01)],.021,skin)
 line(name+'Thumb',[(x-side*.065,-.018,.02),(x-side*.118,.035,.025),(x-side*.14,.09,.014)],.026,skin)
# Merge static meshes per material to reduce renderer work; all transforms and UVs survive.
for material in list(bpy.data.materials):
 objects=[o for o in ROOM.objects if o.type=='MESH' and o.active_material==material]
 if len(objects)>1:
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Room_'+material.name
# Export each collection independently; room is static, book hierarchy retained.
def export(c,file):
 bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/file),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
export(ROOM,'library-room.glb');export(BOOK,'story-book.glb');export(HANDS,'opening-hands.glb')
# Keep source collections organised; move reusable assets away for source preview.
for c in [BOOK,HANDS]:
 for o in c.objects:
  if not o.parent:o.hide_render=True
active=ROOM
# Blender preview lighting approximates browser lighting; all final verification is in Chrome.
light('Window moon',(0,3.8,3.1),(.25,.48,1),750,.8)
light('Desk amber',(-.94,3.45,1.4),(1,.47,.15),100,.4)
light('Hearth',(-3.8,.9,.65),(1,.29,.055),170,.45)
light('Left wall lamp',(-3.9,-2.1,2.5),(1,.52,.22),100,.4)
light('Right wall lamp',(3.9,-2.1,2.5),(1,.52,.22),90,.4)
light('Right rear lamp',(3.9,2.95,2.5),(1,.52,.22),90,.4)
light('Magic glow',(0,-.6,1.45),(.27,.55,.54),24,.3)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.11,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.24
bpy.ops.object.camera_add(location=(0,-6.5,2.15));cam=bpy.context.object;cam.name='OverviewCamera';cam.rotation_euler=(Vector((0,1.4,1.75))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'evidence/blender-room-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/source/storyos-library.blend'))
metadata={'blender':bpy.app.version_string,'room':{'width':9.6,'depth':12,'height':4.6},'slots':[{'index':i,'position':[x,1.25,-y],'yaw':-a} for i,(x,y,a) in enumerate(slots)],'materials':{m.name:list(m.get('runtimeTint',[])) for m in [wood,floor,plaster,stone]},'source':'scripts/build_library.py'}
(R/'public/assets/models/scene.json').write_text(json.dumps(metadata,indent=2))
print('STORYOS_ASSETS_READY',json.dumps(metadata))
if '--render' in __import__('sys').argv:bpy.ops.render.render(write_still=True)
