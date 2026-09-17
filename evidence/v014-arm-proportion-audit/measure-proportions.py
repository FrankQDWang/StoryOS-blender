"""Read-only rest-mesh section audit. Never saves or exports a Blender asset.
Run: blender --background --factory-startup --python-exit-code 1 --python evidence/v014-arm-proportion-audit/measure-proportions.py
"""
from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/v014-arm-proportion-audit'
profile=json.loads((ROOT/'apps/web/src/opening-anatomy.json').read_text())
S=profile['referenceBookScale']
inputs=['assets/source/makehuman-hands.blend','assets/vendor/makehuman/base-human.blend','public/assets/models/makehuman-hands.glb','apps/web/src/opening-anatomy.json']
before={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}

def vec(v): return [round(float(x),9) for x in v]
def section(vertices,edges,origin,axis,widthaxis,thicknessaxis,distance,allowed=None):
    points=[]
    for edge in edges:
        i,j=edge.vertices
        if allowed is not None and not (allowed[i] and allowed[j]): continue
        a,b=vertices[i],vertices[j]
        da=(a-origin).dot(axis)-distance; db=(b-origin).dot(axis)-distance
        if abs(da)<1e-8: points.append(a)
        if abs(db)<1e-8: points.append(b)
        if da*db < 0: points.append(a+(b-a)*(da/(da-db)))
    if not points: return None
    x=[(p-origin).dot(widthaxis) for p in points]
    z=[(p-origin).dot(thicknessaxis) for p in points]
    return {'distance_proximal_from_wrist_m':distance,'width_m':max(x)-min(x),'thickness_m':max(z)-min(z),'intersection_count':len(points),'width_min_m':min(x),'width_max_m':max(x),'thickness_min_m':min(z),'thickness_max_m':max(z)}

def data_of(mesh,transform):
    return [transform@v.co for v in mesh.vertices], mesh.edges

def frame(direction):
    axis=direction.normalized()
    width=Vector((1,0,0)); width=(width-axis*width.dot(axis)).normalized()
    thickness=width.cross(axis).normalized()
    return axis,width,thickness

bpy.ops.wm.open_mainfile(filepath=str(ROOT/inputs[0]))
actual={}
for side,label in [('R','Right'),('L','Left')]:
    rig=bpy.data.objects[label+'Hand']; skin=bpy.data.objects[label+'Skin']; sleeve=bpy.data.objects[label+'Sleeve']
    origin=rig.data.bones['wrist.'+side].head_local*S
    direction=rig.data.bones['lowerarm02.'+side].head_local*S-origin
    axis,widthaxis,thicknessaxis=frame(direction)
    vs,edges=data_of(skin.data,Matrix.Scale(S,4)); svs,sedges=data_of(sleeve.data,Matrix.Scale(S,4))
    tip=max(v.y for v in vs); ratio=(tip/S)/.22225145995616913
    palm=[v.co*S for v in skin.data.vertices if .09*ratio<v.co.y<.115*ratio and sum(g.weight for g in v.groups if skin.vertex_groups[g.group].name.startswith('finger1'))<.15]
    skin_sections=[section(vs,edges,origin,axis,widthaxis,thicknessaxis,d) for d in [0,.01,.02,.04,.06,.0824,.10]]
    sleeve_sections=[section(svs,sedges,origin,axis,widthaxis,thicknessaxis,d) for d in [.0824,.09,.10,.12,.15,.20,.25,.30,.40,.50,.80]]
    sleeve_axis=[(v-origin).dot(axis) for v in svs]
    sleeve_weights={}
    for v in sleeve.data.vertices:
        for g in v.groups:
            name=sleeve.vertex_groups[g.group].name
            sleeve_weights.setdefault(name,[]).append(g.weight)
    actual[label]={'wrist_origin_runtime_m':vec(origin),'forearm_axis_proximal':vec(axis),'width_axis':vec(widthaxis),'thickness_axis':vec(thicknessaxis),'hand_length_wrist_to_farthest_mesh_y_m':tip-origin.y,'documented_palm_slab':{'authoring_y_min':.09*ratio,'authoring_y_max':.115*ratio,'runtime_y_min_m':.09*ratio*S,'runtime_y_max_m':.115*ratio*S,'width_m':max(v.x for v in palm)-min(v.x for v in palm),'thickness_m':max(v.z for v in palm)-min(v.z for v in palm),'vertex_count':len(palm)},'skin_sections':skin_sections,'sleeve_sections':sleeve_sections,'sleeve_axis_extent_m':[min(sleeve_axis),max(sleeve_axis)],'sleeve_vertex_count':len(svs),'sleeve_weight_summary':{n:{'vertex_assignments':len(w),'min':min(w),'max':max(w)} for n,w in sleeve_weights.items()},'rig_bone_count':len(rig.data.bones),'rig_bone_names':[b.name for b in rig.data.bones]}

bpy.ops.wm.open_mainfile(filepath=str(ROOT/inputs[1]))
human=bpy.data.objects['MakeHumanSource']; rig=bpy.data.objects['MakeHumanRig']
deps=bpy.context.evaluated_depsgraph_get()
mesh=bpy.data.meshes.new_from_object(human.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
base={}
for side,label in [('R','Right'),('L','Left')]:
    wrist=rig.data.bones['wrist.'+side].head_local.copy()
    forward=(rig.data.bones['finger3-1.'+side].head_local-wrist).normalized()
    radial=rig.data.bones['finger2-1.'+side].head_local-rig.data.bones['finger5-1.'+side].head_local
    radial=(radial-forward*radial.dot(forward)).normalized()
    x=radial*(-1 if side=='R' else 1); z=x.cross(forward).normalized()
    basis=Matrix((x,forward,z))
    anatomy_scale=profile['handLengthMetres']/(.22225145995616913*S)
    transform=Matrix.Scale(1.3*anatomy_scale*S,4)@basis.to_4x4()@Matrix.Translation(-wrist)
    origin=transform@wrist
    direction=transform@rig.data.bones['lowerarm02.'+side].head_local-origin
    axis,widthaxis,thicknessaxis=frame(direction)
    vs,edges=data_of(mesh,transform)
    allowed=[]
    for v in mesh.vertices:
        arm_weight=sum(g.weight for g in v.groups if human.vertex_groups[g.group].name.endswith('.'+side) and human.vertex_groups[g.group].name.startswith(('lowerarm','upperarm','wrist','finger','metacarpal')))
        allowed.append(arm_weight>.5)
    sections=[section(vs,edges,origin,axis,widthaxis,thicknessaxis,d,allowed) for d in [0,.01,.02,.04,.06,.0824,.10,.12,.15,.20,.25,.30,.40,.50]]
    landmarks={name:vec(transform@rig.data.bones[name+'.'+side].head_local) for name in ['lowerarm02','lowerarm01','upperarm02','upperarm01','wrist']}
    base[label]={'sections':sections,'same_side_arm_weight_filter':'> 0.5 at both edge endpoints','landmarks_transformed_m':landmarks,'wrist_to_lowerarm01_head_euclidean_m':(transform@rig.data.bones['lowerarm01.'+side].head_local-origin).length,'evaluated_vertex_count':len(mesh.vertices),'source_modifiers':[{'name':m.name,'type':m.type,'show_viewport':m.show_viewport} for m in human.modifiers]}

ratios={}
for label in actual:
    curr=actual[label]; src=base[label]
    sleeve={round(s['distance_proximal_from_wrist_m'],5):s for s in curr['sleeve_sections'] if s}
    bare={round(s['distance_proximal_from_wrist_m'],5):s for s in src['sections'] if s}
    ratios[label]={}
    for d in [.0824,.10,.12,.15,.20,.25,.30]:
        if d in sleeve and d in bare:
            ratios[label][str(d)]={'sleeve_to_source_bare_width':sleeve[d]['width_m']/bare[d]['width_m'],'sleeve_to_source_bare_thickness':sleeve[d]['thickness_m']/bare[d]['thickness_m'],'sleeve_width_minus_source_bare_width_m':sleeve[d]['width_m']-bare[d]['width_m']}
    ratios[label]['sleeve_20cm_to_documented_palm_width']=sleeve[.20]['width_m']/curr['documented_palm_slab']['width_m']
    ratios[label]['cuff_to_wrist_origin_section_width']=sleeve[.0824]['width_m']/curr['skin_sections'][0]['width_m']
after={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
assert before==after,'Read-only input hash check failed'
result={'date':'2026-09-17','character_profile':profile,'method':{'asset':'Rest mesh coordinates read from saved .blend; no rebuild, pose change on disk, save, or export.','runtime_scale':'Reference scale 0.824; runtime compensates book scales so this is the same physical size across the five lecterns.','section':'Exact edge-plane intersections; planes perpendicular to original lowerarm02 rest axis through wrist, sampled at proximal distances. Width is projected authored x after removal of forearm-axis component; thickness is its cross with forearm axis.','palm':'Historical vertex slab behind knuckles, excluding vertices with finger1 weight >= 0.15. This is a reproducible mesh envelope, not a standardized anthropometric landmark.','base':'Evaluated CC0 source body transformed with the same wrist basis and scale as the hand generator, then filtered to same-side arm weights; no source mesh was altered.','limitations':['All widths are geometric envelope projections, not certified anatomical measurements or circumferences.','Concept ImageGen pictures have no 3D scale; their dimensions are not proven by this mesh audit.','The source body is aligned/scaled to the actual hand for comparison; this does not establish a complete 1.70m character.','Mesh section directions follow the original straight lowerarm02 axis; far above elbow they stop representing a local perpendicular anatomical section.','No visual or motion acceptance is implied.']},'current':actual,'source_bare_arm':base,'ratios':ratios,'input_hashes_before':before,'input_hashes_after':after,'inputs_unchanged':before==after}
(OUT/'measurements.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'current':{k:{'hand_length_cm':v['hand_length_wrist_to_farthest_mesh_y_m']*100,'palm_width_cm':v['documented_palm_slab']['width_m']*100,'skin_sections':v['skin_sections'],'sleeve_sections':v['sleeve_sections'],'sleeve_axis_extent_m':v['sleeve_axis_extent_m']} for k,v in actual.items()},'ratios':ratios,'source_bare_arm':base,'inputs_unchanged':True},ensure_ascii=False,indent=2))
