"""Compare preserved skeleton motion and measure the changed rest surfaces."""
from pathlib import Path
import bpy, json, math

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
scale=.824

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene=bpy.context.scene
    arms=sorted([o for o in bpy.data.objects if o.type=='ARMATURE'],key=lambda o:o.name)
    frames=[]
    for frame in range(106):
        scene.frame_set(frame)
        frames.append({arm.name+'.'+bone.name:[v for row in bone.matrix for v in row]
                       for arm in arms for bone in arm.pose.bones})
    meshes={o.name: [[float(v) for v in p.co] for p in o.data.vertices]
            for o in bpy.data.objects if o.type=='MESH'}
    measurements={}
    for name in ['RightSkin','LeftSkin']:
        points=meshes[name]
        band=[p for p in points if abs(p[1])<.005]
        measurements[name]={
            'hand_length_cm':max(p[1] for p in points)*scale*100,
            'wrist_band_width_cm':(max(p[0] for p in band)-min(p[0] for p in band))*scale*100,
            'wrist_band_depth_cm':(max(p[2] for p in band)-min(p[2] for p in band))*scale*100,
            'vertices':len(points),
        }
    return frames,meshes,measurements

before=snapshot(ROOT/'downloads/mage-hands/baseline/assets/source/makehuman-hands.blend')
after=snapshot(ROOT/'assets/source/makehuman-hands.blend')
maximum=0
for old,new in zip(before[0],after[0]):
    assert old.keys()==new.keys()
    for key in old:
        maximum=max(maximum,max(abs(a-b) for a,b in zip(old[key],new[key])))
assert maximum<1e-6,maximum
delta={}
for name in ['RightSkin','LeftSkin']:
    a,b=before[1][name],after[1][name]
    assert len(a)==len(b)
    changes=[math.dist(x,y)*scale*1000 for x,y in zip(a,b)]
    delta[name]={'maximum_surface_offset_runtime_mm':max(changes),'modified_vertices':sum(d>.001 for d in changes)}
result={'skeletal_frames_compared':106,'bones_each_frame':42,'maximum_bone_matrix_difference':maximum,
        'existing_skeletal_motion_preserved':True,'before_measurements':before[2],'after_measurements':after[2],
        'hand_surface_changes':delta,'new_meshes':sorted(after[1]),
        'limits':'Rest mesh measurements, not a complete collision simulation or proof of visual quality.'}
(OUT/'model-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
