"""Reproducible sculpted room, reusable book and hands. Blender 5.x, metres.
Blender world: X right, Y into room, Z up. glTF converts to Y up.
Generated texture provenance is in assets/source/*-texture.json.
"""
import bpy, math, random, json, os
from mathutils import Vector, Euler
from pathlib import Path
R=Path(__file__).resolve().parents[1]; random.seed(24)
LAYOUT=json.loads((R/'apps/web/src/room-layout.json').read_text())
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
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'public/assets/textures'/tex),check_existing=True)
  m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
  # glTF supports image textures; runtime applies the tint recorded here.
  m['runtimeTint']=list(c)
 return m
wood=mat('Timber',(.37,.21,.105),.92,tex='a-study-wood.png')
furniture=mat('ReadingWood',(.47,.29,.15),.84,tex='a-study-wood.png')
floor=mat('FloorWood',(.54,.37,.215),.92,tex='a-study-wood.png')
plaster=mat('WarmPlaster',(.54,.43,.32),.96,tex='sculpted-plaster.png')
stone=mat('Stone',(.20,.24,.255),.98,tex='sculpted-plaster.png')
dark=mat('DarkTimber',(.10,.064,.038),.9)
table_slate=mat('TableSlate',(.075,.13,.19),.58,.1)
brass=mat('OldBrass',(.43,.29,.105),.35,.72)
iron=mat('Iron',(.055,.065,.071),.7,.45)
rug=mat('WovenRug',(.18,.087,.056),1)
trim=mat('RugBorder',(.33,.24,.135),1)
teal=mat('Velvet',(.065,.14,.135),1)
wax=mat('Wax',(.68,.46,.23),.9)
flame=mat('Flame', (1,.49,.13),.5,emit=4)
lamp_glass=mat('LanternGlow',(1,.56,.21),.5,emit=2.2)
blue=mat('NightGlass',(.025,.11,.19),.7,emit=.9)
black=mat('Black',(.008,.014,.02),1)
decor=mat('HearthDecor',(1,1,1),1,tex='hearth-decor-atlas.png')
rug_art=mat('HearthRug',(1,1,1),1,tex='a-study-rug.png')
ember=mat('HearthEmber',(.42,.065,.008),.95,emit=.7)
ceramic=mat('GlazedUmber',(.065,.052,.035),.38)
foliage=mat('DryFoliage',(.11,.13,.047),.98)
night_far=mat('NightSilhouetteFar',(.025,.051,.074),1,emit=.6)
night_near=mat('NightSilhouetteNear',(.009,.025,.036),1,emit=.35)
blue.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.35

def fixture(n):return next(f for f in LAYOUT['fixtures'] if f['id']==n)

def local_point(center,offset,rotation):
 return Vector(center)+Euler(rotation).to_matrix()@Vector(offset)

def atlas_panel(n,center,size,quadrant,rotation=(math.pi/2,0,0),material=None):
 """Flat albedo on a real mesh; quadrant UVs retain the original generated atlas."""
 w,h=size;verts=[(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)]
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],[(0,1,2,3)]);mesh.update()
 obj=bpy.data.objects.new(n,mesh);ROOM.objects.link(obj);obj.location=center;obj.rotation_euler=rotation
 mesh.materials.append(material or decor);uv=mesh.uv_layers.new(name='AtlasUV')
 u0,v0,u1,v1=[(0,.5,.5,1),(.5,.5,1,1),(0,0,.5,.5),(.5,0,1,.5)][quadrant]
 inset=2/1254;uvs=[(u0+inset,v0+inset),(u1-inset,v0+inset),(u1-inset,v1-inset),(u0+inset,v1-inset)]
 for loop in mesh.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
 return obj

def picture(n,center,size,quadrant,rotation=(math.pi/2,0,0)):
 w,h=size
 cube(n+' backing',local_point(center,(0,0,-.026),rotation),(w+.08,h+.08,.05),dark,.012,rotation)
 atlas_panel(n+' image',center,size,quadrant,rotation)
 for x in [-w/2-.018,w/2+.018]:cube(n+' frame',local_point(center,(x,0,.009),rotation),(.044,h+.09,.055),wood,.009,rotation)
 for y in [-h/2-.018,h/2+.018]:cube(n+' frame',local_point(center,(0,y,.009),rotation),(w+.08,.044,.055),wood,.009,rotation)

def vase(n,x,y,z,scale=1,plant=True):
 profile=[(0,.12),(.04,.19),(.19,.24),(.33,.18),(.39,.10),(.45,.10),(.47,.13)]
 verts=[];faces=[];sides=16
 for height,radius in profile:
  for i in range(sides):
   a=i*math.tau/sides;verts.append((x+scale*radius*math.cos(a),y+scale*radius*math.sin(a),z+scale*height))
 for j in range(len(profile)-1):
  for i in range(sides):
   a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(n,mesh);ROOM.objects.link(obj);mesh.materials.append(ceramic)
 for f in mesh.polygons:f.use_smooth=True
 ring(n+' rim',(x,y,z+.47*scale),.118*scale,.012*scale,ceramic)
 cyl(n+' inner',(x,y,z+.435*scale),.095*scale,.01,black)
 if plant:
  for j in range(7):
   a=j*2.4;dx=math.sin(a)*scale*.25;dy=math.cos(a)*scale*.20;height=(.72+(j%3)*.12)*scale
   line(n+' twig',[(x,y,z+.44*scale),(x+dx*.6,y+dy*.6,z+height*.77),(x+dx,y+dy,z+height)],.005*scale,dark)
   for k in range(3,7):
    t=k/7;px=x+dx*t;py=y+dy*t;pz=z+.44*scale+(height-.44*scale)*t
    for side in [-1,1]:
     leaf=uv_sphere(n+' leaf',(px+side*.036*scale,py,pz),(.055*scale,.019*scale,.024*scale),foliage);leaf.rotation_euler=(.3,a,side*.6)

def stack_book(n,center,size,angle=0):
 w,d,h=size;x,y,z=center
 cube(n+' pages',(x,y,z+h/2),(w-.035,d-.025,h*.72),paper,.009,rot=(0,0,angle))
 for dz in [0,h]:cube(n+' cover',(x,y,z+dz),(w,d,.035),dark,.014,rot=(0,0,angle))
 cube(n+' bound spine',(x+w/2-.012,y,z+h/2),(.035,d,h+.018),dark,.01,rot=(0,0,angle))
 for offset in [-d*.3,d*.3]:cube(n+' spine band',(x-w/2,y+offset,z+h/2),(.024,.025,h+.04),brass,.004)

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
 obj=put(bpy.context.object,n,m)
 if n in ['magic foot','magic stem','magic table edge']:
  mod=obj.modifiers.new('carved edge softness','BEVEL');mod.width=.018;mod.segments=2
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=obj.modifiers.new('weighted face normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return obj

def line(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=8;c.bevel_depth=r;c.bevel_resolution=2
 sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for b,co in zip(sp.bezier_points,pts):b.co=co;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,c);active.objects.link(o);c.materials.append(m)
 bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

def carved_beam(n,points,width=.26,depth=.26):
 vertices=[];faces=[]
 for x,y,z in points:
  vertices.extend([(x,y-depth/2,z-width/2),(x,y+depth/2,z-width/2),(x,y+depth/2,z+width/2),(x,y-depth/2,z+width/2)])
 for i in range(len(points)-1):
  a=i*4
  for j in range(4):faces.append((a+j,a+(j+1)%4,a+4+(j+1)%4,a+4+j))
 faces.extend([(3,2,1,0),tuple((len(points)-1)*4+j for j in range(4))])
 mesh=bpy.data.meshes.new(n);mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(n,mesh);ROOM.objects.link(o);mesh.materials.append(wood)
 bpy.context.view_layer.objects.active=o
 bevel=o.modifiers.new('worn beam edges','BEVEL');bevel.width=.025;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
 return o

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
 uv_sphere('lantern crown',(x,y,z+.35),(.15,.15,.075),brass)
 for a in range(4):
  ang=a*math.pi/2+math.pi/4;line('lantern cage',[(x+.13*math.cos(ang),y+.13*math.sin(ang),z),(x+.13*math.cos(ang),y+.13*math.sin(ang),z+.31)],.011,iron)
 uv_sphere('lantern glow',(x,y,z+.18),(.073,.073,.12),lamp_glass)
 candle(x,y,z+.04,.19)
 ring('lantern loop',(x,y,z+.49),.05,.012,iron).rotation_euler[0]=math.pi/2

# Plank floor with controlled rhythm and a few slightly uneven joints.
cube('floor foundation',(0,-1.2,-.18),(9.8,12,.25),dark)
for row in range(25):
 x=-4.704+row*.392
 start=-7.2-(row%3)*.8
 for seg in range(6):
  lo=max(-7.2,start+seg*2.4);hi=min(4.8,start+(seg+1)*2.4)
  if hi-lo<.05:continue
  cube('floor plank',(x,(lo+hi)/2,-.026+random.uniform(-.001,.001)),(.386,hi-lo-.005,.12),floor,.003)
# Side walls and back wall, back has an architectural window opening.
cube('left wall',(-4.8,-1.25,2.2),(.35,12,4.6),plaster,.08)
cube('right wall',(4.8,-1.25,2.2),(.35,12,4.6),plaster,.08)
# Complete the room behind the overview camera for an actual 360-degree visit.
cube('entrance wall',(0,-7.22,2.2),(9.8,.22,4.6),plaster,.055)
cube('closed entrance door',(0,-7.08,1.32),(1.48,.12,2.64),wood,.07)
for x in [-.82,.82]:cube('door jamb',(x,-6.97,1.38),(.14,.16,2.78),dark,.035)
cube('door lintel',(0,-6.97,2.74),(1.76,.16,.15),dark,.035)
uv_sphere('door knob',(.50,-6.96,1.28),(.045,.045,.045),brass)
cube('back lower',(0,4.55,.64),(9.8,.35,1.36),plaster,.065)
cube('back upper',(0,4.55,4.05),(9.8,.35,1.25),plaster,.07)
cube('back left',(-3.06,4.55,2.42),(3.68,.35,2.25),plaster,.065)
cube('back right',(3.06,4.55,2.42),(3.68,.35,2.25),plaster,.065)
# Ceiling and mildly bent beams.
cube('ceiling',(0,-1.25,4.58),(9.85,12,.3),plaster,.12)
for y in [-6.7,-3.8,-.9,2.0,4.35]:
 carved_beam('bent crossbeam',[(-4.55,y,3.62),(-3.8,y,3.92),(-2.1,y,4.08),(0,y,4.10),(2.1,y,4.08),(3.8,y,3.92),(4.55,y,3.62)])
 for x in [-4.55,4.55]:
  cube('carved upright',(x,y,1.82),(.24,.26,3.60),wood,.032)
  cube('post foot',(x,y,.22),(.37,.34,.4),wood,.04)
for x in [-3,-1.5,0,1.5,3]:cube('ceiling runner',(x,-1.2,4.43),(.13,11.75,.15),wood,.02)
for x in [-4.55,4.55]:
 for z in [.25,1.0,3.45]:cube('wall rail',(x,-1.25,z),(.18,11.65,.14),wood,.03)
for z in [.23,1.04,3.64]:cube('back rail',(0,4.31,z),(9.2,.2,.13),wood)
# Window: rounded arch with leaded panes and a deep sill.
cube('night pane',(0,5.65,2.48),(5.0,.06,4.4),blue,.06)
# Layered 3D conifers occupy the shallow exterior recess; no flat scene backdrop.
for depth,m,count in [(5.35,night_far,13),(4.91,night_near,11)]:
 for i in range(count):
  x=-1.7+i*3.4/(count-1)
  height=([.60,1.1,1.50,1.15,.85,.62,.9,1.62,1.15,.83,.6][i] if m==night_near else .52+((i*5)%8)*.10)
  # Short irregular tiers break the large triangle silhouette into branches.
  for tier in range(9):
   fraction=tier/9;z=1.03+height*(.10+fraction*.85);radius=height*(.20*(1-fraction)+.015)
   verts=[(x,depth,z+height*.21)];faces=[]
   for k in range(16):
    a=k*math.tau/16;rr=radius*(1 if k%2==0 else .70);verts.append((x+rr*math.cos(a),depth+rr*math.sin(a),z+(.025 if k%2 else 0)))
   for k in range(16):faces.append((0,1+k,1+(k+1)%16))
   mesh=bpy.data.meshes.new('fir branches');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('fir branches',mesh);ROOM.objects.link(obj);mesh.materials.append(m)
  cyl('night tree trunk',(x,depth,1.15+height*.20),.018,height*.60,m,6)
# Fill the two upper corners so the opening itself follows the timber arch.
for side in [-1,1]:
 verts=[];faces=[]
 for i in range(17):
  x=side*i*1.20/16;z=2.55+1.0*math.sqrt(max(0,1-(x/1.2)**2));verts.extend([(x,4.28,z),(x,4.28,3.65)])
 for i in range(16):
  k=2*i;faces.append((k,k+1,k+3,k+2) if side>0 else (k+2,k+3,k+1,k))
 mesh=bpy.data.meshes.new('window arch spandrel');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('window arch spandrel',mesh);ROOM.objects.link(obj);mesh.materials.append(plaster)
for x in [-1.22,1.22]:cube('window jamb',(x,4.25,2.48),(.18,.38,2.46),wood,.045)
cube('window sill',(0,4.12,1.30),(2.85,.64,.18),wood,.05)
for x in [-.6,0,.6]:cube('window mullion',(x,4.23,2.5),(.045,.08,2.2),wood,.008)
for z in [1.95,2.7,3.45]:cube('window lead',(0,4.23,z),(2.4,.08,.038),iron,.006)
# Arch shaped frame inset within the architectural opening.
line('window arch',[(-1.2,4.10,2.45),(-1.06,4.10,3.22),(0,4.10,3.56),(1.06,4.10,3.22),(1.2,4.10,2.45)],.09,wood)
# A small writing nook beside the window; all props follow its layout anchor.
desk_before=set(ROOM.objects)
cube('writing desk',(0,3.66,.94),(2.6,.86,.16),furniture,.055)
for x in [-1.08,1.08]:
 for y in [3.35,3.97]:cube('desk leg',(x,y,.45),(.15,.14,.90),furniture,.025,rot=(0,.07 if x>0 else -.07,0))
cube('desk apron',(0,3.25,.75),(2.32,.1,.25),furniture,.04)
for drawer_x in [-.65,.65]:
 cube('drawer',(drawer_x,3.17,.76),(.87,.06,.18),furniture,.016)
 uv_sphere('drawer pull',(drawer_x,3.11,.76),(.03,.03,.025),brass)
lantern(-.68,3.60,1.06)
vase('desk vase',-1.06,3.72,1.05,.62)
# Ink and an unlettered paper, no litter across the floor.
cyl('inkwell',(.81,3.67,1.07),.065,.12,iron)
line('quill',[(.81,3.67,1.13),(.90,3.73,1.46),(.99,3.77,1.60)],.007,trim)
paper=mat('Paper',(.69,.59,.39),.98)
cube('writing paper',(.17,3.58,1.035),(.50,.36,.006),paper,.003,rot=(0,0,.08))
stack_book('desk book lower',(-.34,3.77,1.06),(.45,.31,.075),.08)
stack_book('desk book upper',(-.36,3.78,1.155),(.39,.29,.065),-.04)
desk_x,desk_z=fixture('desk')['center']
for obj in set(ROOM.objects)-desk_before:
 obj.location.x*=.94;obj.scale.x*=.94
 obj.location+=Vector((desk_x,-desk_z-3.66,.20))
 if obj.name.startswith('desk leg'):obj.location.z-=.10;obj.scale.z*=1.222222
# Chair, padded but sculptural.
chair_before=set(ROOM.objects)
for x in [-.28,.28]:
 for y in [2.35,2.84]:cube('chair leg',(x,y,.34),(.09,.09,.66),furniture,.02)
cube('chair seat',(0,2.60,.69),(.73,.69,.16),furniture,.045)
for x in [-.33,.33]:line('chair back post',[(x,2.28,.38),(x,2.20,1.2),(x*.85,2.27,1.45)],.05,wood)
line('chair back crown',[(-.3,2.25,1.35),(0,2.21,1.5),(.3,2.25,1.35)],.065,wood)
for x in [-.16,0,.16]:line('chair spindle',[(x,2.26,.78),(x,2.22,1.36)],.022,wood)
chair_x,chair_z=fixture('chair')['center']
for obj in set(ROOM.objects)-chair_before:obj.location+=Vector((chair_x,-chair_z-2.60,0))
# Keep the repaired continuous arch and translate the whole hearth together.
hearth_before=set(ROOM.objects)
cube('hearth plinth',(-4.14,.9,.14),(1.13,1.85,.25),stone,.035)
cube('hearth back',(-4.55,.9,1.22),(.16,1.58,2.2),black,.02)
for y in [.08,1.72]:
 cube('continuous hearth jamb',(-4.24,y,1.08),(.66,.34,1.71),stone,.016)
# Extruded arch fills the entire space up to the mantel; its ends overlap the jambs.
verts=[];faces=[];steps=28
for x in [-4.57,-3.91]:
 for i in range(steps+1):
  t=-1+2*i/steps;y=.9+.67*t;z=1.31+.39*math.sqrt(max(0,1-t*t))
  verts.extend([(x,y,z),(x,y,1.935)])
back=2*(steps+1)
for i in range(steps):
 k=2*i
 faces.extend([(k,k+2,k+3,k+1),(back+k+1,back+k+3,back+k+2,back+k),
               (k,back+k,back+k+2,k+2),(k+1,k+3,back+k+3,back+k+1)])
faces.extend([(0,1,back+1,back),(2*steps,back+2*steps,back+2*steps+1,2*steps+1)])
mesh=bpy.data.meshes.new('continuous hearth arch');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('continuous hearth arch',mesh);ROOM.objects.link(o);mesh.materials.append(stone)
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
# Shallow mortar lines describe masonry without opening holes through the pillars.
for y in [.08,1.72]:
 for z in [.64,1.06,1.48]:cube('hearth mortar seam',(-3.908,y,z),(.004,.29,.009),dark,.001)
cube('mantel',(-4.21,.9,1.99),(.99,2.05,.19),wood,.05)
cube('chimney breast',(-4.39,.9,3.27),(.59,1.83,2.43),stone,.035)
for row in range(7):
 start=.025
 widths=[.47,.70,.62] if row%2==0 else [.73,.51,.55]
 for col,width in enumerate(widths):
  cube('chimney face stone',(-4.075,start+width/2,2.22+row*.34),(.048,width-.012,.327),stone,.015,rot=(random.uniform(-.005,.005),0,0));start+=width
for z in [2.32,2.67,3.02,3.37,3.72,4.07,4.42]:
 cube('chimney mortar',(-4.091,.9,z),(.004,1.78,.011),dark,.002)
 for y in ([.50,1.29] if int(z*100)%2 else [.18,.96,1.67]):cube('chimney vertical mortar',(-4.090,y,z+.17),(.005,.009,.31),dark,.001)
# Firebrick surfaces inside the open firebox receive the new runtime firelight.
for row in range(3):
 for col in range(4):
  cube('firebrick',(-4.458,.42+col*.31,.52+row*.32),(.025,.304,.311),stone,.006)
for i in range(9):
 t=-.96+i*.24;y=.9+.67*t;z=1.31+.39*math.sqrt(max(0,1-t*t))
 line('arch joint',[(-3.905,y,z+.018),(-3.905,.9+t*.69,1.925)],.004,dark)
for y in [.35,.86,1.34]:
 o=cyl('log',(-4.19,y,.37),.10,.69,dark,10);o.rotation_euler[1]=math.pi/2
 uv_sphere('ember',(-4.14,y,.43),(.16,.105,.055),ember)
candle(-4.05,.52,2.10,.22);candle(-4.03,1.50,2.10,.30)
vase('mantel vase',-4.16,.16,2.10,.85)
stack_book('mantel book lower',(-4.15,.91,2.10),(.38,.49,.085),.03)
stack_book('mantel book middle',(-4.16,.91,2.20),(.34,.46,.075),-.04)
stack_book('mantel book upper',(-4.12,.93,2.29),(.37,.47,.08),.02)
for y in [.28,1.5]:
 line('fire grate foot',[(-3.94,y,.25),(-3.84,y,.49)],.019,iron)
 uv_sphere('grate finial',(-3.84,y,.53),(.028,.028,.028),brass)
line('fire grate rail',[(-3.85,.27,.4),(-3.85,1.52,.4)],.017,iron)
for obj in set(ROOM.objects)-hearth_before:
 obj.location.x+=fixture('hearth')['center'][0]+4.14
 obj.location.y+=-fixture('hearth')['center'][1]-.9
 obj.location.z*=1.05;obj.scale.z*=1.05
# Hearth tools and log basket stay against the wall, out of the walking lanes.
tx,tz=fixture('hearth-tools')['center'];ty=-tz
cyl('tool stand',(tx,ty,.09),.18,.08,iron,12)
line('tool rack',[(tx,ty,.12),(tx,ty,1.20),(tx,ty+.14,1.24)],.018,iron)
for y in [ty-.12,ty,ty+.12]:
 line('fire iron',[(tx+.09,y,.14),(tx+.10,y,.97)],.011,iron)
 ring('fire iron handle',(tx+.10,y,1.01),.036,.009,iron).rotation_euler[1]=math.pi/2
 cube('fire iron blade',(tx+.09,y,.18),(.045,.09,.12),iron,.008)
bx,bz=fixture('log-basket')['center'];by=-bz
cyl('basket bottom',(bx,by,.075),.26,.05,dark,12)
for z in [.11,.35]:ring('basket hoop',(bx,by,z),.29,.014,iron)
for i in range(14):
 a=i*math.tau/14;line('basket stave',[(bx+.26*math.cos(a),by+.26*math.sin(a),.08),(bx+.29*math.cos(a),by+.29*math.sin(a),.39)],.031,wood)
for i in range(5):
 o=cyl('stored firewood',(bx+(i%2)*.12-.08,by+(i//2)*.10-.1,.30),.055,.49,dark,8);o.rotation_euler=(.4,(-.25+i*.13),0)
# The generated cloth is real surface detail, not extra floor furniture.
rx,rz=LAYOUT['rug']['center'];rw,rd=LAYOUT['rug']['size']
cube('rug',(rx,-rz,.057),(rw,rd,.025),rug,.07)
cloth=atlas_panel('woven rug surface',(rx,-rz,.074),(rw-.10,rd-.10),3,(0,0,0),rug_art)
for loop,uv in zip(cloth.data.uv_layers.active.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=uv
for side in [-1,1]:
 for i in range(48):
  x=rx-rw/2+.05+i*(rw-.10)/47;y=-rz+side*rd/2
  line('rug fringe',[(x,y-side*.055,.075),(x+.009,y+side*.07,.063)],.008,rug)
# Central magic writing table, original reusable sculpted piece.
table_before=set(ROOM.objects)
cyl('magic foot',(0,-.6,.16),.60,.25,furniture,8,r2=.48)
cyl('magic stem',(0,-.6,.59),.28,.68,furniture,10,r2=.43)
table_radius=LAYOUT['table']['radius']
cyl('magic table edge',(0,-.6,.98),table_radius,.17,furniture,64)
cyl('magic table inset',(0,-.6,1.057),table_radius-.10,.036,table_slate,64)
ring('brass table ring',(0,-.6,1.08),table_radius-.18,.011,brass)
ring('brass table ring',(0,-.6,1.08),.52,.006,brass)
for a in range(12):
 t=a*math.tau/12
 line('table radial',[(.64*math.cos(t),-.6+.64*math.sin(t),1.08),(.70*math.cos(t),-.6+.70*math.sin(t),1.08)],.006,brass)
table_x,table_z=LAYOUT['table']['center']
for obj in set(ROOM.objects)-table_before:obj.location+=Vector((table_x,-table_z+.6,LAYOUT['table']['topHeight']-1.1))
# Five stable lecterns; positions are also exported to application metadata.
slots=[(s['position'][0],-s['position'][2],s['yaw']) for s in LAYOUT['slots']]
for i,(x,y,ang) in enumerate(slots):
 scale=LAYOUT['slots'][i].get('scale',1)
 base_scale=LAYOUT['slots'][i].get('baseScale',scale)
 pitch=LAYOUT['slots'][i].get('pitch',LAYOUT['lectern']['pitch'])
 cyl(f'lectern {i} base',(x,y,.12),.32*base_scale,.18,furniture,4,r2=.255*base_scale).rotation_euler[2]=ang+math.pi/4
 cube(f'lectern {i} stem',(x,y,.66),(.19*base_scale,.22*base_scale,1.0),furniture,.012,rot=(0,0,ang))
 for dx in [-.24,.24]:
  line('lectern support',[local_point((x,y,0),p,(0,0,ang)) for p in [(0,0,.7),(dx,0,1.08),(dx*1.4,0,1.16)]],.035,furniture)
 rotation=(pitch,0,ang)
 cube(f'lectern {i} top',(x,y,1.18),(1.02*scale,.81*scale,.075),furniture,.018,rot=rotation)
 for row in range(4):
  dy=(-.30375+row*.2025)*scale
  cube('lectern top plank',local_point((x,y,1.18),(0,dy,.039),rotation),(1.00*scale,.2025*scale-.004,.018),furniture,.004,rot=rotation)
 for dx in [-.43,.43]:
  cube('lectern brass edge',local_point((x,y,1.18),(dx*scale,-.37*scale,.054),rotation),(.13*scale,.067*scale,.013),brass,.004,rot=rotation)
  for dy in [-.24,.10,.31]:
   nail=uv_sphere('lectern pin',local_point((x,y,1.18),(dx*scale,dy*scale,.052),rotation),(.008,.008,.004),brass);nail.rotation_euler=rotation
 cube('book rest lip',local_point((x,y,1.18),(0,-.39*scale,.048),rotation),(1.04*scale,.052,.072),furniture,.009,rot=rotation)
# Restrained sconces with pools of warm light.
for x,y in [(-4.47,-2.1),(4.47,-2.1),(4.47,2.95)]:
 cube('sconce back',(x,y,2.3),(.10,.25,.46),wood,.08)
 inward=-1 if x>0 else 1
 line('sconce arm',[(x,y,2.1),(x+inward*.2,y,2.03),(x+inward*.35,y,2.16)],.025,iron)
 candle(x+inward*.35,y,2.17,.27)
# Quiet wall details follow the approved view without occupying the centre.
atlas_panel('hearthside tapestry',(-2.92,4.245,2.38),(1.06,2.08),0)
line('tapestry rod',[(-3.55,4.22,3.48),(-2.29,4.22,3.48)],.025,dark)
for x in [-3.42,-2.42]:ring('tapestry ring',(x,4.21,3.44),.046,.010,brass).rotation_euler[0]=math.pi/2
picture('small botanical',(-1.57,4.23,2.17),(.37,.64),1)
picture('botanical', (2.55,4.23,2.44),(.55,.96),1)
picture('forest painting',(4.395,.50,2.54),(.67,1.29),2,(math.pi/2,0,-math.pi/2))
vase('corner vase',fixture('floor-vase')['center'][0],-fixture('floor-vase')['center'][1],.05,1.02)
cube('wall shelf',(4.34,-1.44,2.76),(.53,.69,.095),wood,.02)
vase('shelf vase',4.34,-1.44,2.82,.52)
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
# Use metre-scaled grain/plaster UVs before joining, avoiding cube-atlas seams.
for obj in ROOM.objects:
 if obj.type!='MESH' or obj.active_material not in [wood,furniture,floor,plaster,stone]:continue
 mesh=obj.data
 if not mesh.vertices:continue
 extents=[max(v.co[i] for v in mesh.vertices)-min(v.co[i] for v in mesh.vertices) for i in range(3)]
 uv=mesh.uv_layers.active or mesh.uv_layers.new(name='SurfaceUV')
 offset=(random.uniform(0,1),random.uniform(0,1))
 for face in mesh.polygons:
  normal_axis=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=normal_axis]
  if obj.active_material in [wood,furniture,floor]:
   long_axis=max(axes,key=lambda i:extents[i])
   if 2 in axes and any(part in obj.name.lower() for part in ['stem','upright','post','leg','chimney']):long_axis=2
   short_axis=next(i for i in axes if i!=long_axis);scales=(2.2,2.8)
  else:short_axis,long_axis=axes;scales=(2.2,2.2)
  for index in face.loop_indices:
   co=mesh.vertices[mesh.loops[index].vertex_index].co
   uv.data[index].uv=(co[short_axis]/scales[0]+offset[0],co[long_axis]/scales[1]+offset[1])
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
light('Desk amber',(desk_x-.94,-desk_z-.06,1.4),(1,.47,.15),100,.4)
light('Hearth',(-3.8,.9,.65),(1,.29,.055),170,.45)
light('Left wall lamp',(-3.9,-2.1,2.5),(1,.52,.22),100,.4)
light('Right wall lamp',(3.9,-2.1,2.5),(1,.52,.22),90,.4)
light('Right rear lamp',(3.9,2.95,2.5),(1,.52,.22),90,.4)
light('Magic glow',(0,-.6,1.45),(.27,.55,.54),24,.3)
world=bpy.context.scene.world;world.use_nodes=True;next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.07,.11,.19,1);next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.24
bpy.ops.object.camera_add(location=(0,-6.5,2.15));cam=bpy.context.object;cam.name='OverviewCamera';cam.rotation_euler=(Vector((0,1.4,1.75))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1440;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/'evidence/blender-room-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'assets/source/storyos-library.blend'))
metadata={'version':LAYOUT['version'],'baseVersion':'v0.1.0-baseline','change':'Selected A hearth study: side writing nook, lighter reading stands, open center and layered materials/light.','blender':bpy.app.version_string,'room':{'width':9.6,'depth':12,'height':4.6},'slots':[{'index':i,**slot} for i,slot in enumerate(LAYOUT['slots'])],'layoutSource':'apps/web/src/room-layout.json','layout':LAYOUT,'visualTarget':'design/round-05/A-hearth-study/final.png','materials':{m.name:list(m.get('runtimeTint',[])) for m in [wood,furniture,floor,plaster,stone]},'source':'scripts/build_library.py'}
(R/'public/assets/models/scene.json').write_text(json.dumps(metadata,indent=2))
print('STORYOS_ASSETS_READY',json.dumps(metadata))
if '--render' in __import__('sys').argv:bpy.ops.render.render(write_still=True)
