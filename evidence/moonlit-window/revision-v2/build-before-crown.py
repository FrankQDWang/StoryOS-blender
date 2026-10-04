"""Independent moonlit-window geometry. Blender Z-up; glTF converts to Y-up.
Does not open or regenerate the approved room, its lightmap, books or hands.
"""
import bpy, math, random, json, hashlib, struct
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
    if name in ['right framing trunk','side fork','fine fork']:verts=[(x-.22,y,z) for x,y,z in verts]
    groups[mat.name].append((verts,faces,uvs))


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
    uvs=[(.01+.98*j/sides,.01+.98*i/(len(pts)-1)) for i in range(len(pts)) for j in range(sides)] if mat==bark else None
    return mesh(name,verts,faces,mat,uvs)

def bough(origin,angle,length,width,mat,sprig=False):
    # Closed, finely serrated foliage volume follows each actual radial branch.
    o=Vector(origin);axis=Vector((math.cos(angle),math.sin(angle),-.30));side=Vector((-math.sin(angle)*.6,math.cos(angle)*.6,.8))
    outline=[]
    for sign,indices in [(-1,range(13)),(1,range(12,-1,-1))]:
        for i in indices:
            t=i/12;spread=math.sin(math.pi*t)**.65*(.62 if i%2 else 1)
            outline.append(o+axis*t*length+side*sign*spread*width*random.uniform(.85,1.12))
    n=len(outline);verts=[]
    for sign in [-1,1]:
        verts.extend(tuple(v+Vector((0,0,sign*length*.015))) for v in outline)
        verts.append(tuple(o+axis*length*.42+Vector((0,0,sign*length*.075))))
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(n,i,j),(2*n+1,n+1+j,n+1+i),(i,n+1+i,n+1+j,j)])
    mesh('solid pine foliage',verts,faces,mat)

def fir(x,depth,height,width,mat,lean=0):
    base=-.7;height+=.7;points=[(x+lean*t*t,depth+.09*math.sin(t*4),base+height*t) for t in [0,.2,.42,.64,.82,1]]
    tube('fir trunk',points,[width*.065,width*.052,width*.039,width*.023,width*.012,.009],bark if mat==near else mat)
    levels=24 if mat==near else 18
    for level in range(levels):
        t=.13+.80*level/(levels-1);radius=width*2.05*(1-t)**.82
        count=7 if mat==near else 6
        offset=random.random()*math.tau
        for j in range(count):
            a=offset+j*math.tau/count+random.uniform(-.23,.23)
            origin=(x+lean*t*t,depth,base+height*t+random.uniform(-.045,.045)*height)
            length=radius*random.uniform(.65,1.13)
            if mat==near:
                end=tuple(Vector(origin)+Vector((math.cos(a)*length,math.sin(a)*length,-length*.18)))
                tube('bough branch',[origin,end],[.020*(1-t),.004],bark,5)
            bough(origin,a,length,length*.36,mat)
    bough(points[-2],.3,width*.12,width*.05,mat)

# Reference-aligned tree silhouettes: tall sides, low open central forest.
for x,h,w in [(-7,3.1,.85),(-5,2.3,.75),(-3.5,2.0,.6),(-2.0,1.5,.48),(-1.2,1.25,.4),(-.1,1.2,.42),(.75,1.0,.35),(1.7,1.5,.48),(2.8,2.2,.65),(4,2.8,.8),(6,3.1,.9)]:
    fir(x,18+random.uniform(-.8,.8),h+.35,w,far,random.uniform(-.12,.12))
for x,h,w in [(-4.5,3.8,.85),(-2.5,2.65,.72),(-1.45,2.98,.64),(-.86,1.83,.37),(-.40,2.22,.39),(.38,1.94,.35),(1.12,2.95,.64),(2.05,1.95,.55),(3.4,3.8,.87),(5.2,3.6,.9)]:
    fir(x,12+random.uniform(-.45,.45),h,w,middle,random.uniform(-.11,.11))
# Cropped side branches, not an entire cone-shaped foreground tree.
tube('left pine trunk',[(-1.55,6.4,-.4),(-1.48,6.45,1.8),(-1.42,6.4,3.2),(-1.45,6.4,4.6)],[.11,.105,.08,.05],bark,9)
for height,reach,depth in [(2.87,.95,6.4),(3.52,.78,6.45),(3.86,.68,6.5),(2.12,.48,6.5)]:
    points=[(-1.6,depth,height),(-1.6+reach*.48,depth+.05,height-.05),(-1.6+reach,depth+.02,height+.01)]
    tube('left framing branch',points,[.035,.02,.002],bark,7)
    for i in range(9):
        t=(i+.3)/9;p=Vector(points[0]).lerp(Vector(points[-1]),t);p.z+=random.uniform(-.08,.04)
        for sign in [-1,1]:
            a=sign*random.uniform(.5,1.35)
            bough(tuple(p),a,random.uniform(.31,.49)*(1-t*.4),.20,near)
# Gently bending trunk stays at the right edge of the view.
tube('right framing trunk',[(1.42,6.7,-.6),(1.48,6.75,1.5),(1.39,6.7,2.65),(1.42,6.75,3.3),(1.29,6.8,4.5)],[.12,.11,.10,.075,.04],bark,11)
for pts in [[(1.4,6.7,2.58),(1.19,6.72,2.77),(1.02,6.7,2.83)],[(1.41,6.75,3.55),(1.13,6.8,3.69),(.99,6.81,3.67)]]:
    tube('side fork',pts,[.025,.013,.002],bark,7)
    for i in range(4):
        p=Vector(pts[0]).lerp(Vector(pts[-1]),(i+.3)/4)
        tube('fine fork',[p,p+Vector((-.045,.03,.12+random.random()*.08))],[.007,.001],bark,5)
# Opaque distant image combines the approved sky, soft moon/cloud and mountain ridge.
# Square projection preserves the moon's shape. Large backing prevents exposed edges.
verts=[];uvs=[]
for t in [-5,0,.35,.65,1,5.5]:
    z=10.25-10.4*t+.45*max(0,min(1,(t-.35)/.30))
    for x in [-70,70]:verts.append((x,42,z));uvs.append(((x+5.4)/10.4,1-t))
mesh('night sky',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(5)],sky,uvs)

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

for name,parts in groups.items():
    if not parts:continue
    verts=[];faces=[];uvs=[]
    for points,polygons,coords in parts:
        offset=len(verts);verts.extend(points)
        faces.extend(tuple(offset+i for i in polygon) for polygon in polygons)
        uvs.extend(coords or [(0,0)]*len(points))
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(bpy.data.materials[name])
    uv=data.uv_layers.new(name='AtlasUV') if any(part[2] for part in parts) else None
    for face in data.polygons:
        face.use_smooth=True
        if uv:
            for loop in face.loop_indices:uv.data[loop].uv=uvs[data.loops[loop].vertex_index]
bpy.ops.object.select_all(action='SELECT')
source=ROOT/'assets/source/moonlit-window/window-vista.blend';source.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(source))
out=ROOT/'public/assets/models/window-vista.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
# Unlit distance layers never consume normals. Drop only those unused streams,
# preserving every position, triangle and UV bit-for-bit.
raw=out.read_bytes();jsize=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jsize]);binary=raw[28+jsize:]
for item in doc['meshes']:
    for primitive in item['primitives']:
        matname=doc['materials'][primitive['material']]['name']
        if matname in ['VistaMiddle','VistaFar','VistaSky','VistaGlass']:
            primitive['attributes'].pop('NORMAL',None)
used=set()
for item in doc['meshes']:
    for primitive in item['primitives']:used.update(primitive['attributes'].values());used.add(primitive['indices'])
accessors=sorted(used);amap={old:i for i,old in enumerate(accessors)}
views=sorted({doc['accessors'][i]['bufferView'] for i in accessors});vmap={old:i for i,old in enumerate(views)}
newbin=bytearray();newviews=[]
for i in views:
    view=dict(doc['bufferViews'][i]);start=view.get('byteOffset',0)
    while len(newbin)%4:newbin.append(0)
    view['byteOffset']=len(newbin);newbin.extend(binary[start:start+view['byteLength']]);newviews.append(view)
doc['accessors']=[doc['accessors'][i] for i in accessors]
for accessor in doc['accessors']:accessor['bufferView']=vmap[accessor['bufferView']]
for item in doc['meshes']:
    for primitive in item['primitives']:
        primitive['attributes']={k:amap[v] for k,v in primitive['attributes'].items()};primitive['indices']=amap[primitive['indices']]
doc['bufferViews']=newviews;doc['buffers'][0]['byteLength']=len(newbin)
while len(newbin)%4:newbin.append(0)
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
out.write_bytes(struct.pack('<4sII',b'glTF',2,28+len(j)+len(newbin))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(newbin),b'BIN\0')+newbin)
report={'generator':'scripts/build_window_vista.py','seed':10429,'source':str(source.relative_to(ROOT)),'model':str(out.relative_to(ROOT)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'style_reference':'design/round-12-moonlit-window/02-room-proposal.png','coordinates':'Blender XYZ -> glTF XZ-Y; exterior is beyond room window','materials':list(groups),'original_room_rebuilt':False}
(source.parent/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
