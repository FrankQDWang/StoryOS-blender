"""Independent moonlit-window geometry. Blender Z-up; glTF converts to Y-up.
Does not open or regenerate the approved room, its lightmap, books or hands.
"""
import bpy, math, random, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
random.seed(10429)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
groups={}

def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.94
    groups[name]=[]
    return m

near=material('VistaNear',(.028,.062,.084))
bark=material('VistaBark',(.06,.08,.10))
middle=material('VistaMiddle',(.042,.09,.13))
far=material('VistaFar',(.065,.13,.20))
ridge=material('VistaRidge',(.086,.157,.235))
sky=material('VistaSky',(1,1,1));moon=material('VistaMoon',(1,1,1))
wood=material('VistaWindowJoin',(.20,.105,.052))
glass=material('VistaGlass',(.25,.34,.43))

def mesh(name,verts,faces,mat,uvs=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    if uvs:
        uv=data.uv_layers.new(name='AtlasUV')
        for face in data.polygons:
            for loop in face.loop_indices:uv.data[loop].uv=uvs[data.loops[loop].vertex_index]
    
    if name.startswith('right old') or name in ['old tree branch','branch tip']:
        for vertex in data.vertices:vertex.co.x-=.42
    for face in data.polygons:face.use_smooth=True
    groups[mat.name].append(obj)
    return obj

def tube(name,points,radii,mat,sides=7):
    pts=[Vector(p) for p in points];verts=[]
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        u=tangent.cross(Vector((0,1,0)))
        if u.length<.01:u=tangent.cross(Vector((1,0,0)))
        u.normalize();v=tangent.cross(u).normalized()
        for j in range(sides):
            a=j*math.tau/sides;verts.append(tuple(p+radii[i]*(math.cos(a)*u+math.sin(a)*v)))
    faces=[]
    for i in range(len(pts)-1):
        for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    faces.extend([tuple(range(sides-1,-1,-1)),tuple((len(pts)-1)*sides+j for j in range(sides))])
    uvs=[(.754+.240*j/sides,.006+.735*i/(len(pts)-1)) for i in range(len(pts)) for j in range(sides)] if mat==bark else None
    return mesh(name,verts,faces,mat,uvs)

def bough(origin,angle,length,width,mat,sprig=False):
    # Close foreground uses many small needle sprays instead of large polygon plates.
    if mat==near and not sprig:
        for i in range(4):
            t=.12+i*.20
            center=Vector(origin)+Vector((math.cos(angle),math.sin(angle),-.35))*(t*length)
            for sign in [-1,1]:
                bough(tuple(center),angle+sign*random.uniform(.5,.9),length*(.47-.15*t),width*.38,mat,True)
        bough(tuple(Vector(origin)+Vector((math.cos(angle),math.sin(angle),-.35))*(length*.76)),angle,length*.32,width*.22,mat,True)
        return
    # Closed irregular needle sprays, with genuine volume from every angle.
    o=Vector(origin);axis=Vector((math.cos(angle),math.sin(angle),-.42));side=Vector((-math.sin(angle),math.cos(angle),0))
    outline=[(-.08,0),(.12,-.38),(.24,-1),(.34,-.57),(.47,-.83),(.56,-.38),(.72,-.52),(1,0),(.69,.48),(.58,.33),(.44,.80),(.32,.52),(.20,.83),(.10,.36)]
    verts=[]
    for sign in [-1,1]:
        for t,w in outline:
            p=o+axis*(t*length)+side*(w*width)+Vector((0,0,sign*.12*length*(1-max(t,0))))
            verts.append(tuple(p))
        verts.append(tuple(o+axis*(.38*length)+Vector((0,0,sign*.24*length))))
    n=len(outline);faces=[]
    for j in range(n):
        k=(j+1)%n;faces.extend([(n,j,k),(2*n+1,n+1+k,n+1+j),(j,n+1+j,n+1+k,k)])
    return mesh('needle spray',verts,faces,mat)

def fir(x,depth,height,width,mat,lean=0):
    base=.05;points=[(x+lean*t*t,depth+.09*math.sin(t*4),base+height*t) for t in [0,.2,.42,.64,.82,1]]
    tube('fir trunk',points,[width*.065,width*.052,width*.039,width*.023,width*.012,.009],bark if mat==near else mat)
    levels=20 if mat==near else 13
    for level in range(levels):
        t=.13+.80*level/(levels-1);radius=width*(1-t)**.82
        count=5 if mat==near else 3
        offset=random.random()*math.tau
        for j in range(count):
            a=offset+j*math.tau/count+random.uniform(-.23,.23)
            origin=(x+lean*t*t,depth,base+height*t+random.uniform(-.045,.045)*height)
            length=radius*random.uniform(.65,1.13)
            if mat==near:
                end=tuple(Vector(origin)+Vector((math.cos(a)*length,math.sin(a)*length,-length*.18)))
                tube('bough branch',[origin,end],[.020*(1-t),.004],bark,5)
            bough(origin,a,length,length*.43,mat)
    bough(points[-2],.3,width*.12,width*.05,mat)

# Dense depth layers are spread in world space, not camera-facing billboards.
for x,depth,h,w in [(-10,17,6,1.9),(-7.8,18,5.4,1.6),(-5.8,16.8,4.9,1.5),(-3.9,18.4,5.5,1.8),(-2.1,17.5,4.5,1.4),(-.5,18,3.8,1.3),(1.2,17,4.6,1.5),(3.2,18.2,6.1,1.8),(5.2,17,5.0,1.4),(7.2,18,6.2,1.9),(9.7,17.5,5.8,1.8)]:
    fir(x,depth,h,w,far,random.uniform(-.25,.25))
for x,depth,h,w in [(-7.2,11.8,5.2,1.5),(-5.3,12.5,4.5,1.4),(-3.4,11.6,3.9,1.1),(-2.0,12.3,3.1,1.0),(-.7,12.7,2.9,.9),(.7,13.2,3.2,.8),(2.5,12.0,4.3,1.2),(4.4,12.6,5.3,1.6),(6.6,12,4.9,1.4)]:
    fir(x,depth,h,w,middle,random.uniform(-.23,.23))
fir(-1.25,6.45,5.5,1.02,near,.20)
# Right foreground has an asymmetric trunk with a few bare offshoots.
tube('right old tree',[(1.75,6.7,0),(1.65,6.72,1.8),(1.72,6.78,3),(1.59,6.77,4.1),(1.48,6.8,5.7)],[.19,.16,.13,.09,.027],bark,9)
for points in [[(1.68,6.77,3.1),(1.20,6.64,3.65),(.87,6.68,3.85)],[(1.58,6.77,4.0),(1.07,6.85,4.32),(.71,6.88,4.38)],[(1.66,6.75,2.5),(2.1,6.98,2.95),(2.5,7,3.06)]]:
    tube('old tree branch',points,[.06,.026,.006],bark)
    p=Vector(points[1]);tube('branch tip',[p,p+Vector((-.07,.05,.30))],[.017,.003],bark,5)

# Low, continuous ridgeline. This fills beneath the distant image at oblique views.
verts=[]
for i in range(65):
    x=-60+i*120/64;y=2.6+.75*math.sin(x*.33)+.32*math.cos(x*.62)
    verts.extend([(x,28,-30),(x,28,y)])
mesh('distant ridge',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(64)],ridge)
# Atlas left 75%: landscape. A broad backing surface cannot expose an edge through the window.
mesh('night sky',[(-70,42,-45),(70,42,-45),(70,42,65),(-70,42,65)],[(0,1,2,3)],sky,[(.006,-3.14),(.744,-3.14),(.744,4.714),(.006,4.714)])
# Moon is a distant decal in the same sky, using the atlas top-right square.
mx,my,mz,size=1.27,40.9,7.9,1.30
mesh('cloud veiled moon',[(mx-size/2,my,mz-size/2),(mx+size/2,my,mz-size/2),(mx+size/2,my,mz+size/2),(mx-size/2,my,mz+size/2)],[(0,1,2,3)],moon,[(.751,.751),(.999,.751),(.999,.999),(.751,.999)])

# Small physical joints on the existing sill; no changes to the original lightmapped wood.
for x in [-.78,.72]:
    tube('sill joint',[(x,3.815,1.24),(x,3.815,1.355)],[.003,.003],wood,4)
for x in [-1.215,1.215]:
    tube('jamb joint',[(x-.06,4.052,2.40),(x+.06,4.052,2.40)],[.003,.003],wood,4)
# Single quiet pane behind the existing mullions. Drawn once, no transmission/reflection pass.
outline=[(-1.19,4.285,1.40),(1.19,4.285,1.40),(1.19,4.285,2.55)]
for i in range(1,25):
    angle=math.pi*i/24;outline.append((math.cos(angle)*1.19,4.285,2.55+math.sin(angle)*.98))
mesh('quiet glass',outline,[tuple(range(len(outline)))],glass)

for name,objects in groups.items():
    if not objects:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    objects[0].name=name
bpy.ops.object.select_all(action='SELECT')
source=ROOT/'assets/source/moonlit-window/window-vista.blend';source.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
out=ROOT/'public/assets/models/window-vista.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
report={'generator':'scripts/build_window_vista.py','seed':10429,'source':str(source.relative_to(ROOT)),'model':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'style_reference':'design/round-12-moonlit-window/02-room-proposal.png','coordinates':'Blender XYZ -> glTF XZ-Y; exterior is beyond room window','materials':list(groups),'original_room_rebuilt':False}
(source.parent/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
