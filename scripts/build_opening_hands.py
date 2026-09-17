"""Author the reusable, skinned hands independently of the approved room.

All geometry is project-authored. Metres, Blender Z-up; palm dorsal surface +Z,
fingers +Y. Runtime places wrists against the book using its shared timeline.
Run: blender --background --factory-startup --python-exit-code 1 --python scripts/build_opening_hands.py
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


def material(name, color, roughness):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return m


skin = material('WriterSkin', (.52, .30, .19), .69)
nail = material('WriterNails', (.60, .37, .28), .48)
cloth = material('WriterSleeve', (.048, .080, .089), .92)
seam = material('WriterCuff', (.11, .15, .15), .86)


def ellipsoid(name, center, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16 if 'Nail' in name else 24, ring_count=8 if 'Nail' in name else 16, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def loft(name, rings, sides=16, mat=None):
    """Elliptical sections, long axis +Y; no overlapping segment seams."""
    vertices, faces = [], []
    for x, y, z, width, depth in rings:
        for i in range(sides):
            a = i * math.tau / sides
            vertices.append((x + math.cos(a) * width, y, z + math.sin(a) * depth))
    for j in range(len(rings)-1):
        for i in range(sides):
            a = j*sides+i
            b = j*sides+(i+1)%sides
            faces.append((a, b, b+sides, a+sides))
    faces.extend([tuple(reversed(range(sides))), tuple((len(rings)-1)*sides+i for i in range(sides))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        mesh.materials.append(mat)
    return obj


def attach(obj, armature, weights):
    for bone in armature.data.bones:
        obj.vertex_groups.new(name=bone.name)
    for vertex in obj.data.vertices:
        for name, weight in weights(vertex.co):
            if weight > .001:
                obj.vertex_groups[name].add([vertex.index], weight, 'REPLACE')
    modifier = obj.modifiers.new('Skin', 'ARMATURE')
    modifier.object = armature
    obj.parent = armature
    for face in obj.data.polygons:
        face.use_smooth = True


def distance_segment(p, a, b):
    ab = b-a
    u = max(0, min(1, (p-a).dot(ab)/ab.length_squared))
    return (p-(a+ab*u)).length


def make_hand(side):
    prefix = 'Right' if side == 1 else 'Left'
    # Palm flares from a narrow wrist to a subtly arched row of knuckles.
    parts = [loft(prefix+'Palm', [
        (0,-.22,0,.042,.031), (0,-.155,0,.037,.026),
        (0,-.105,.001,.045,.027), (-.005,-.060,.002,.068,.032),
        (0,-.005,.001,.078,.030), (.002,.042,0,.078,.026),
        (.004,.078,-.002,.065,.019), (.004,.087,-.003,.045,.013),
    ])]
    parts.append(ellipsoid(prefix+'Thenar',(-.046,-.035,-.014),(.042,.060,.027)))
    parts.append(ellipsoid(prefix+'Hypothenar',(.046,-.034,-.010),(.032,.057,.025)))
    specs = [('Index',-.056,.052,.167,.0195,-.025),
             ('Middle',-.016,.068,.181,.020,0),
             ('Ring',.026,.059,.168,.0185,.012),
             ('Little',.064,.031,.137,.0155,.029)]
    chains = {}
    nail_specs = []
    for name, x, start, length, radius, spread in specs:
        rings = []
        for t, w, d in [(0,1.05,.86),(.15,1.02,.82),(.36,.92,.76),(.48,.99,.81),
                         (.59,.84,.70),(.72,.89,.72),(.84,.75,.64),(.94,.60,.53),(1,.18,.20)]:
            rings.append((x+spread*t,start+length*t,-.004-.012*t*t,radius*w,radius*d))
        parts.append(loft(prefix+name,rings))
        points = [Vector((x+spread*t,start+length*t,-.004-.012*t*t)) for t in [0,.46,.75,1.0]]
        chains[name] = points
        nail_specs.append((name, (x+spread*.87,start+length*.87,-.004-.012*.87**2+radius*.61), (radius*.57,length*.081,.0025)))
    # Opposable thumb: broad base, diagonal metacarpal, narrowing distal pad.
    thumb = [Vector(p) for p in [(-.047,-.050,-.010),(-.094,-.007,-.010),(-.124,.033,-.018),(-.136,.068,-.024)]]
    for i in range(3):
        a,b=thumb[i],thumb[i+1]
        obj=ellipsoid(prefix+'ThumbMass'+str(i),(a+b)/2,(.025-i*.004,(b-a).length*.67,.022-i*.003))
        obj.rotation_euler[2]=-math.atan2((b-a).x,(b-a).y)
        parts.append(obj)
    chains['Thumb']=thumb
    nail_specs.append(('Thumb',(-.132,.054,-.006),(.010,.013,.0025)))
    for obj in parts:
        bpy.context.view_layer.objects.active=obj
        sub=obj.modifiers.new('Rounded anatomical sections','SUBSURF')
        sub.levels=1
        bpy.ops.object.modifier_apply(modifier=sub.name)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    hand=parts[0]
    hand.name=prefix+'Skin'
    # A single manifold surface gives the palm/finger webs continuous shading.
    remesh=hand.modifiers.new('Continuous sculpt','REMESH')
    remesh.mode='VOXEL'
    remesh.voxel_size=.0032
    remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=hand.modifiers.new('Sculpt relaxation','SMOOTH')
    smooth.factor=.8
    smooth.iterations=7
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    decimate=hand.modifiers.new('Web topology','DECIMATE')
    decimate.ratio=.27
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    hand.data.materials.append(skin)
    for v in hand.data.vertices:
        v.co.x*=side
    for points in chains.values():
        for p in points:
            p.x*=side
    armdata=bpy.data.armatures.new(prefix+'Rig')
    arm=bpy.data.objects.new(prefix+'Hand',armdata)
    bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm
    bpy.ops.object.mode_set(mode='EDIT')
    root_name=prefix+'Wrist'
    root=armdata.edit_bones.new(root_name)
    root.head=(0,-.15,0)
    root.tail=(0,.03,0)
    segments=[]
    for name,points in chains.items():
        parent=root
        for i in range(3):
            bone=armdata.edit_bones.new(prefix+name+str(i))
            bone.head=points[i]
            bone.tail=points[i+1]
            bone.parent=parent
            parent=bone
            segments.append((bone.name,points[i],points[i+1],name))
    bpy.ops.object.mode_set(mode='OBJECT')

    def weights(p):
        # Smooth blend at the MCP and segment joints; palm remains rigid at wrist.
        right=Vector((p.x*side,p.y,p.z))
        if right.y < -.065:
            return [(root_name,1)]
        choices=sorted((distance_segment(p,a,b),n,part) for n,a,b,part in segments)
        d,n,part=choices[0]
        base=chains[part][0]
        if part=='Thumb':
            finger=max(0,min(1,(-right.x-.065)/.033))
        else:
            finger=max(0,min(1,(right.y-base.y+.016)/.038))
        if finger <= 0:
            return [(root_name,1)]
        nearby=[(dist,name) for dist,name,chain in choices if chain==part][:2]
        ws=[1/(.005+dist)**3 for dist,name in nearby]
        total=sum(ws)
        return [(root_name,1-finger)]+[(name,finger*w/total) for (dist,name),w in zip(nearby,ws)]

    attach(hand,arm,weights)
    for name,center,scale in nail_specs:
        obj=ellipsoid(prefix+name+'Nail',(center[0]*side,center[1],center[2]),scale)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        obj.data.materials.append(nail)
        attach(obj,arm,lambda p,n=prefix+name+'2':[(n,1)])
    sleeve=loft(prefix+'Sleeve',[
        (0,-.48,-.005,.064,.052),(0,-.40,0,.060,.050),(.003,-.31,0,.056,.046),
        (0,-.245,.001,.051,.040),(0,-.194,0,.049,.037),(0,-.184,0,.048,.036)
    ],24,cloth)
    cuff=loft(prefix+'Cuff',[(0,-.205,0,.051,.039),(0,-.188,0,.052,.040),(0,-.180,0,.047,.035)],24,seam)
    for obj in [sleeve,cuff]:
        attach(obj,arm,lambda p:[(root_name,1)])
    # Merge compatible parts while retaining skin weights and material slots.
    bpy.ops.object.select_all(action='DESELECT')
    meshes=[obj for obj in bpy.data.objects if obj.type=='MESH' and obj.parent==arm]
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=hand
    bpy.ops.object.join()
    # Mirroring vertices reverses winding; recalculate the closed surface normals.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


for side in [-1,1]:
    make_hand(side)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/models/writer-hands.glb'),
    export_format='GLB',use_selection=True,export_apply=False,
    export_animations=False,export_skins=True,export_all_influences=False,
    export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/source/writer-hands.blend'))
(ROOT/'assets/source/writer-hands.json').write_text(json.dumps({
    'source':'Project-authored anatomical lofts, voxel union, smoothed surface and weighted armature',
    'generator':'scripts/build_opening_hands.py','blender':bpy.app.version_string,
    'license':'Original project asset; no third-party model or texture',
    'runtime':'apps/web/src/OpeningHands.jsx','timeline':'apps/web/src/opening-motion.mjs',
    'style':'Soft stylized human hands, slate linen cuffs; approved hearth-study palette',
    'bones_per_hand':16,'unit':'metres'
},indent=2)+'\n')
print('WRITER_HANDS_READY')
