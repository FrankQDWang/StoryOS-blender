"""Probe the saved baseline and repaired masonry; run with Blender in background."""
from pathlib import Path
import json
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]

def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    vertices, faces = [], []
    for obj in bpy.data.collections['Room'].objects:
        if obj.type != 'MESH':
            continue
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        for face in obj.data.polygons:
            material = obj.data.materials[face.material_index]
            if material and material.name == 'Stone':
                faces.append(tuple(offset + i for i in face.vertices))
    tree = BVHTree.FromPolygons(vertices, faces)
    def hit(y, z):
        return tree.ray_cast(Vector((-3.7, y, z)), Vector((-1, 0, 0)), 1.0)[0] is not None
    probes = [(y, round(.28 + i * .01, 2)) for y in [.08, 1.72] for i in range(165)]
    missing = [[y, z] for y, z in probes if not hit(y, z)]
    return {
        'pillar_ray_count': len(probes), 'pillar_gap_count': len(missing),
        'pillar_gap_locations': missing,
        'header_hits': sum(hit(.3 + i * .05, 1.84) for i in range(25)),
        'header_ray_count': 25,
        'firebox_open': not hit(.9, 1.0),
        'packed_textures': sorted(i.name for i in bpy.data.images if i.packed_file),
    }

baseline = inspect(ROOT / '.worktrees/baseline/assets/source/storyos-library.blend')
current = inspect(ROOT / 'assets/source/storyos-library.blend')
result = {'baseline': baseline, 'current': current,
          'scope': 'Front-facing rays through saved Stone meshes; not a whole-scene manifold or collision proof.'}
(ROOT / 'evidence/v011/hearth-check.json').write_text(json.dumps(result, indent=2) + '\n')
assert baseline['pillar_gap_count'] > 0, 'Baseline probes must reproduce the reported gaps'
assert current['pillar_gap_count'] == 0
assert current['header_hits'] == current['header_ray_count']
assert current['firebox_open']
assert len(current['packed_textures']) == 2
print('HEARTH_CHECK_PASSED', json.dumps(result))
