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

# Small, asymmetric lived-in room. Layout metadata uses runtime Y-up coordinates.
layout=json.loads((R/'apps/web/src/room-layout.json').read_text())
paper=mat('Paper',(.69,.59,.39),.98)
cloth=mat('ThrowCloth',(.32,.235,.17),1)
ceramic=mat('Ceramic',(.28,.35,.30),.68)
# Group a piece of furniture before rotating it, preserving prop relationships.
def furniture(start,origin,angle=0):
 for o in set(ROOM.objects)-start:
  x,y,z=o.location;ox,oy=origin
  o.location.x=ox+x*math.cos(angle)-y*math.sin(angle)
  o.location.y=oy+x*math.sin(angle)+y*math.cos(angle)
  o.rotation_euler.z+=angle

def fabric(n,points,width,m):
 # A draped strip with a continuous surface and small folds, not a rigid slab.
 verts=[];faces=[];cols=16
 for j,(y,z) in enumerate(points):
  for i in range(cols+1):
   x=(i/cols-.5)*width
   verts.append((x,y,z+.017*math.cos(i*1.55+j*.18)))
 for j in range(len(points)-1):
  for i in range(cols):
   k=j*(cols+1)+i;faces.append((k,k+1,k+cols+2,k+cols+1))
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(n,mesh);ROOM.objects.link(o);mesh.materials.append(m)
 sub=o.modifiers.new('soft fabric folds','SUBSURF');sub.levels=2
 solid=o.modifiers.new('woven thickness','SOLIDIFY');solid.thickness=.007
 bpy.context.view_layer.objects.active=o
 for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 for f in o.data.polygons:f.use_smooth=True
 return o

cube('floor foundation',(0,-.55,-.18),(7.6,8.4,.25),dark)
for row in range(13):
 for seg in range(4):
  cube('floor plank',(-3.52+row*.585,-3.59+seg*2.03,-.025+random.uniform(-.004,.004)),(.57,2.014,.12),floor,.009)
cube('left wall',(-3.79,-.55,1.76),(.30,8.4,3.65),plaster,.04)
cube('right wall',(3.79,-.55,1.76),(.30,8.4,3.65),plaster,.04)
# One off-centre window; no axis running through the whole room.
cube('back below window',(0,3.61,.74),(7.8,.30,1.5),plaster,.025)
cube('back above window',(0,3.61,3.38),(7.8,.30,.47),plaster,.025)
cube('back left',(-1.79,3.61,2.3),(4.23,.30,1.65),plaster,.025)
cube('back right',(3.18,3.61,2.3),(1.43,.30,1.65),plaster,.025)
cube('ceiling',(0,-.55,3.62),(7.8,8.4,.22),plaster,.06)
for y in [-3.5,.3,3.42]:
 line('bent crossbeam',[(-3.61,y,2.92),(-2.65,y,3.33),(-.7,y,3.42),(1.5,y,3.4),(3.61,y,2.99)],.10,wood)
 for x in [-3.59,3.59]:line('wall post',[(x,y,.12),(x+.025,y,1.7),(x,y,3.02)],.09,wood)
for x in [-2.0,.1,2.3]:cube('ceiling runner',(x,-.55,3.48),(.11,8.1,.13),wood,.018)
for x in [-3.6,3.6]:
 for z in [.18,.89]:cube('wall rail',(x,-.50,z),(.12,8.2,.12),wood,.018)
for z in [.18,.89]:cube('back rail',(0,3.41,z),(7.25,.15,.12),wood,.018)
# Deep, slightly arched wooden frame. Cool glass is visible between thick jambs.
cube('night pane',(1.37,3.61,2.29),(2.08,.04,1.7),blue,.04)
for x in [.31,2.44]:cube('window jamb',(x,3.42,2.28),(.14,.38,1.86),wood,.035)
cube('window sill',(1.37,3.27,1.47),(2.44,.57,.15),wood,.035)
line('window crown',[(.32,3.33,2.88),(.62,3.33,3.14),(1.40,3.33,3.20),(2.15,3.33,3.12),(2.44,3.33,2.88)],.075,wood)
for x in [.85,1.38,1.91]:cube('window mullion',(x,3.40,2.29),(.034,.07,1.60),iron,.005)
for z in [2.02,2.55]:cube('window lead',(1.38,3.40,z),(2.06,.07,.031),iron,.004)
# A relaxed hanging curtain, gathered at one side, with actual folds.
curtain=fabric('gathered window curtain',[(0,3.16),(.03,2.98),(.09,2.60),(.20,2.28),(.16,1.86),(.04,1.47)],.42,teal)
curtain.location=(2.40,3.23,0)
# Low household cabinet: closed storage below, five books together above.
cx=-1.75;cy=3.03
for x in [cx-.87,cx+.87]:
 for y in [cy-.34,cy+.34]:cube('cabinet foot',(x,y,.15),(.16,.16,.27),wood,.03)
cube('cabinet lower',(cx,cy,.49),(1.97,.79,.61),wood,.035)
for x in [cx-.47,cx+.47]:
 cube('cupboard door',(x,cy-.414,.49),(.87,.055,.46),dark,.025)
 cube('door field',(x,cy-.449,.49),(.69,.027,.31),wood,.015)
 uv_sphere('cupboard knob',(x+(.30 if x<cx else -.30),cy-.50,.53),(.032,.026,.032),brass)
cube('book shelf',(cx,cy,.785),(2.10,.94,.075),wood,.023)
for x in [cx-1.0,cx+1.0]:cube('cabinet side',(x,cy,1.25),(.10,.9,.90),wood,.025)
cube('cabinet back',(cx,cy+.40,1.24),(1.97,.09,.9),dark,.016)
cube('cabinet crown',(cx,cy,1.71),(2.16,1.0,.13),wood,.033)
# Upper shelf has a small paper bundle and a jug, leaving the books readable.
for k in range(4):cube('stored manuscript',(-2.33+random.uniform(-.02,.02),3.02,1.794+k*.018),(.41,.29,.016),paper,.008,rot=(0,0,.04+k*.012))
line('bundle string',[(-2.55,3.02,1.855),(-2.33,3.02,1.88),(-2.11,3.02,1.855)],.008,trim)
uv_sphere('clay jug',(-.97,3.06,1.93),(.13,.13,.20),ceramic)
cyl('jug neck',(-.97,3.06,2.085),.057,.10,ceramic)
ring('jug mouth',(-.97,3.06,2.14),.060,.015,ceramic)
# Everyday desk, slightly away from the sill. The clear writing area is the magic surface.
start=set(ROOM.objects)
cube('desk top',(0,0,.91),(2.1,1.08,.14),wood,.047)
for x in [-.89,.89]:
 for y in [-.40,.40]:cube('desk leg',(x,y,.45),(.12,.13,.91),wood,.02,rot=(0,.035 if x>0 else -.035,0))
cube('desk apron',(0,-.46,.76),(1.94,.11,.25),wood,.025)
for x in [-.47,.47]:
 cube('desk drawer',(x,-.532,.765),(.82,.045,.17),dark,.014)
 uv_sphere('drawer pull',(x,-.572,.765),(.025,.02,.025),brass)
# Clear dark writing leather provides a calm focal area, no ritual pedestal.
cube('writing mat',(-.12,-.02,.985),(1.1,.77,.010),teal,.027)
lantern(.82,.31,1.00)
for k in range(5):cube('loose draft',(.66+random.uniform(-.03,.03),-.14+random.uniform(-.02,.02),.992+k*.008),(.36,.44,.006),paper,.003,rot=(0,0,-.17+k*.015))
cyl('inkwell',(.45,.35,1.08),.058,.13,iron)
line('quill',[(.45,.35,1.13),(.49,.37,1.34),(.57,.40,1.46)],.008,trim)
# Sculpted feather vane.
feather=uv_sphere('feather',(.535,.388,1.386),(.028,.013,.105),paper);feather.rotation_euler[1]=.39
cyl('cup base',(.88,-.39,1.015),.071,.012,ceramic)
cyl('tea cup',(.88,-.39,1.072),.076,.112,ceramic,r2=.086)
cyl('tea surface',(.88,-.39,1.129),.070,.005,dark)
ring('cup lip',(.88,-.39,1.13),.079,.007,ceramic)
handle=ring('cup handle',(.98,-.39,1.075),.045,.013,ceramic);handle.rotation_euler[0]=math.pi/2
furniture(start,(1.25,2.0),0)
# Tucked, turned writing chair.
start=set(ROOM.objects)
for x in [-.24,.24]:
 for y in [-.24,.24]:cube('writing chair leg',(x,y,.26),(.07,.08,.49),wood,.018)
cube('writing chair seat',(0,0,.51),(.65,.65,.14),teal,.07)
for x in [-.28,.28]:line('chair back',[(x,-.26,.43),(x,-.33,1.03),(x*.9,-.30,1.21)],.038,wood)
line('chair crest',[(-.27,-.31,1.16),(0,-.33,1.26),(.27,-.31,1.16)],.055,wood)
for x in [-.15,0,.15]:line('chair spindle',[(x,-.28,.6),(x,-.33,1.2)],.018,wood)
furniture(start,(1.98,.78),-.30)
# Continuous fireplace body with a carved arch opening: no floating masonry layers.
# Build facing forward in local coordinates, then turn onto the left wall.
start=set(ROOM.objects)
cube('hearth slab',(0,-.01,.115),(1.88,.90,.21),stone,.035)
cube('firebox back',(0,.34,.84),(1.53,.14,1.35),black,.015)
for x in [-.69,.69]:cube('solid hearth jamb',(x,0,.75),(.35,.67,1.29),stone,.018)
# Arch spandrel: continuous extrusion from curved underside up to a flat lintel.
verts=[];faces=[];n=24
for y in [-.34,.33]:
 for i in range(n+1):
  x=-.52+i/n*1.04;z=1.02+.32*math.sqrt(max(0,1-(x/.52)**2))
  verts.extend([(x,y,z),(x,y,1.51)])
for i in range(n):
 k=2*i;back=2*(n+1)
 faces.extend([(k,k+2,k+3,k+1),(back+k+1,back+k+3,back+k+2,back+k),
               (k,back+k,back+k+2,k+2),(k+1,k+3,back+k+3,back+k+1)])
faces.extend([(0,1,2*(n+1)+1,2*(n+1)),(2*n,4*n+2,4*n+3,2*n+1)])
mesh=bpy.data.meshes.new('continuous arch');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('continuous arch',mesh);ROOM.objects.link(o);mesh.materials.append(stone)
cube('hearth shoulder',(0,.04,1.51),(1.79,.74,.18),stone,.018)
cube('wood mantel',(0,-.04,1.655),(1.98,.91,.14),wood,.027)
cube('chimney hood',(0,.21,2.32),(1.42,.42,1.30),plaster,.048)
# Shallow lines in the stone add scale without breaking the continuous volume.
for x in [-.69,.69]:
 for z in [.48,.83,1.17]:cube('mortar seam',(x,-.343,z),(.31,.004,.012),dark,.002)
for x in [-.33,.17]:
 o=cyl('fire log',(x,-.07,.30),.095,.63,dark,10);o.rotation_euler[1]=math.pi/2;o.rotation_euler[2]=.22
 uv_sphere('ember',(x,-.11,.36),(.16,.10,.055),flame)
for i in range(4):
 uv_sphere('little flame',(-.33+i*.19,-.02,.44+(.03 if i%2 else 0)),(.055,.065,.16 if i%2 else .10),flame)
candle(-.65,-.07,1.74,.20)
# Unmatched personal items on mantel.
cube('small frame',(.40,.03,1.91),(.25,.09,.31),wood,.022,rot=(0,-.06,0))
cube('frame inset',(.40,-.024,1.91),(.18,.009,.23),teal,.008)
furniture(start,(-3.23,.88),math.pi/2)
# A few logs and a poker live by the fireplace.
for i in range(5):
 o=cyl('spare firewood',(-3.27,-.28+(i%3)*.12,.17+(i//3)*.14),.075,.40,dark,10);o.rotation_euler[1]=math.pi/2
line('fire poker',[(-3.4,-.43,.13),(-3.42,-.43,.78),(-3.34,-.43,.88)],.014,iron)
# Comfortable reading chair, a soft crooked silhouette instead of a display plinth.
start=set(ROOM.objects)
for x in [-.39,.39]:
 for y in [-.36,.36]:cube('armchair foot',(x,y,.18),(.13,.14,.30),wood,.024)
cube('armchair base',(0,0,.42),(1.07,.99,.25),wood,.055)
cube('armchair cushion',(0,-.08,.60),(.92,.87,.24),teal,.12)
cube('armchair back',(0,.36,1.02),(1.06,.23,.99),teal,.12,rot=(-.12,0,0))
for x in [-.49,.49]:
 cube('armchair arm',(x,-.01,.80),(.18,.96,.21),wood,.075)
 line('arm support',[(x,-.38,.46),(x,-.37,.75)],.045,wood)
cube('loose cushion',(.16,.10,.95),(.51,.22,.45),rug,.10,rot=(-.23,.09,-.14))
throw=fabric('draped throw',[(.39,1.53),(.26,1.51),(.18,1.33),(.12,1.12),(.04,.80),(-.10,.74),(-.42,.71),(-.55,.56),(-.59,.31)],.38,cloth);throw.location.x=-.22
furniture(start,(-2.54,-1.27),-.31)
# Low footstool sits within reach, off-axis.
start=set(ROOM.objects)
for x in [-.27,.27]:
 for y in [-.22,.22]:cube('footstool leg',(x,y,.19),(.075,.08,.34),wood,.016)
cube('footstool cushion',(0,0,.39),(.77,.65,.19),rug,.085)
furniture(start,(-1.12,-.69),.17)
# Small side table, adjacent to the chair, with one lamp.
start=set(ROOM.objects)
cyl('side table top',(0,0,.66),.33,.09,wood,32)
for a in range(3):
 t=a*math.tau/3;line('side table leg',[(.15*math.cos(t),.15*math.sin(t),.64),(.22*math.cos(t),.22*math.sin(t),.08)],.033,wood)
lantern(0,0,.72)
furniture(start,(-3.13,-2.35),0)
# The rug belongs to the seating area; its border and tassels move together.
start=set(ROOM.objects)
cube('rug',(0,0,.060),(3.39,2.80,.019),rug,.035)
for x in [-1.59,1.59]:cube('rug border',(x,0,.072),(.035,2.56,.004),trim,.002)
for y in [-1.27,1.27]:
 cube('rug border',(0,y,.072),(3.18,.035,.004),trim,.002)
 for i in range(23):line('rug tassel',[(-1.54+i*.14,y+(.12 if y>0 else -.12),.068),(-1.53+i*.14,y+(.18 if y>0 else -.18),.065)],.007,trim)
furniture(start,(-.66,-.74),.085)
# Sparse everyday wall items; varied grouping, not repeated symmetrical sconces.
cube('notes rail',(-1.70,3.38,2.27),(1.65,.09,.10),wood,.018)
for x,z,a in [(-2.12,2.09,-.07),(-1.80,2.02,.04),(-1.46,2.11,-.025)]:
 cube('pinned note',(x,3.32,z),(.22,.006,.29),paper,.004,rot=(0,a,0))
 uv_sphere('note pin',(x,3.305,z+.11),(.014,.008,.014),brass)
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
 pp=bpy.data.objects.new(f'PagePivot{k}',None);BOOK.objects.link(pp);pp.location=(-.345,0,.177+k*.003)
 verts=[];faces=[];steps=24
 for i in range(steps+1):
  x=.70*i/steps
  verts.extend([(x,-.4625,0),(x,.4625,0)])
 for i in range(steps):faces.append((2*i,2*i+2,2*i+3,2*i+1))
 me=bpy.data.meshes.new(f'PageMesh{k}');me.from_pydata(verts,[],faces);me.update()
 pg=bpy.data.objects.new(f'TurnPage{k}',me);BOOK.objects.link(pg);me.materials.append(pages);pg.parent=pp
# Sculpted relaxed gripping hands. One watertight mesh per hand, not separated tubes.
active=HANDS
skin=mat('HandSkin',(.49,.31,.20),.87)
sleeve=mat('HandSleeve',(.065,.105,.11),.97)
for side in [-1,1]:
 name='Left' if side<0 else 'Right'
 parent=bpy.data.objects.new(name+'Hand',None);HANDS.objects.link(parent)
 start=set(HANDS.objects)
 uv_sphere(name+'Palm',(0,0,0),(.078,.11,.035),skin)
 uv_sphere(name+'Wrist',(0,-.115,0),(.060,.073,.032),skin)
 for f in range(4):
  fx=(f-1.5)*.034;length=[.105,.14,.15,.118][f]
  line(name+'Finger',[(fx,.065,.003),(fx,.105,.001),(fx,.08+length*.70,-.009),(fx,.08+length,-.027)],.018,skin)
  uv_sphere(name+'Fingertip',(fx,.08+length,-.027),(.018,.020,.018),skin)
 line(name+'Thumb', [(-side*.055,-.028,-.002),(-side*.097,.014,-.027),(-side*.105,.060,-.055)],.025,skin)
 uv_sphere(name+'ThumbTip',(-side*.105,.060,-.055),(.025,.029,.025),skin)
 parts=[o for o in set(HANDS.objects)-start if o.type=='MESH']
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.join();hand=parts[0];hand.name=name+'SculptedHand'
 remesh=hand.modifiers.new('continuous skin','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.0065;remesh.use_smooth_shade=True
 bpy.ops.object.modifier_apply(modifier=remesh.name)
 smooth=hand.modifiers.new('soft knuckles','SMOOTH');smooth.factor=.5;smooth.iterations=3;bpy.ops.object.modifier_apply(modifier=smooth.name)
 cuff=cube(name+'Cuff',(0,-.177,0),(.147,.096,.082),sleeve,.022)
 # Forearms follow a prescribed curved path in the runtime assembly.
 for o in [hand,cuff]:o.parent=parent
# Merge static meshes per material to reduce renderer work; all transforms and UVs survive.
for material in list(bpy.data.materials):
 objects=[o for o in ROOM.objects if o.type=='MESH' and o.active_material==material]
 if len(objects)>1:
  bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();objects[0].name='Room_'+material.name
# Keep the animated hinges, but batch fixed book pieces sharing a parent/material.
book_batches={}
for o in list(BOOK.objects):
 if o.type=='MESH':book_batches.setdefault((o.parent,o.active_material),[]).append(o)
for (parent,material),objects in book_batches.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
 objects[0].name=('Cover_' if parent else 'Book_')+material.name
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
# Source preview has matching broad lighting; final acceptance uses Chrome.
light('Window moon',(1.37,3.1,2.8),(.25,.48,1),470,.8)
light('Desk amber',(2.07,2.31,1.4),(1,.47,.15),100,.3)
light('Hearth',(-2.9,.88,.62),(1,.29,.055),110,.45)
light('Reading lamp',(-3.13,-2.35,1.1),(1,.52,.22),95,.35)
light('Soft warm fill',(2.7,-1.8,2.8),(1,.56,.28),65,1)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.11,.19,1);world.node_tree.nodes['Background'].inputs[1].default_value=.24
p=layout['home'];look=layout['homeLook']
bpy.ops.object.camera_add(location=(p[0],-p[2],p[1]));cam=bpy.context.object;cam.name='OverviewCamera';cam.rotation_euler=(Vector((look[0],-look[2],look[1]))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=27;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'evidence/v02/blender-room-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/source/storyos-library.blend'))
metadata={**layout,'blender':bpy.app.version_string,'materials':{m.name:list(m.get('runtimeTint',[])) for m in [wood,floor,plaster,stone]},'source':'scripts/build_library.py','layoutSource':'apps/web/src/room-layout.json'}
(R/'public/assets/models/scene.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('STORYOS_ASSETS_READY',json.dumps(metadata))
if '--render' in __import__('sys').argv:bpy.ops.render.render(write_still=True)
