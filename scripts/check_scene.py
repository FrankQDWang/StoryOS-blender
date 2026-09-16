"""Inspect saved Blender geometry without saving either file.

Run: blender --background --factory-startup --python-exit-code 1 --python scripts/check_scene.py
Room meshes are joined by material, so identify furniture by connected geometry,
dimensions and height; do not infer its position from the layout being checked.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / '.worktrees/baseline/assets/source/storyos-library.blend'
CURRENT = ROOT / 'assets/source/storyos-library.blend'
LAYOUT_PATH = ROOT / 'apps/web/src/room-layout.json'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', default='evidence/v012/geometry-check.json')
import sys
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
OUTPUT = ROOT / args.output
TOLERANCE = .00001  # 0.01 mm for unchanged source meshes.
OCCUPANCY_TOLERANCE = .0001  # 0.1 mm numerical allowance for world transforms.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime(v):
    return (v.x, v.z, -v.y)


def reusable_meshes():
    return {
        collection: {
            obj.name: [tuple(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices]
            for obj in bpy.data.collections[collection].objects if obj.type == 'MESH'
        } for collection in ['Book', 'Hands']
    }


def compare_meshes(before, after):
    result = {}
    for collection in before:
        a, b = before[collection], after[collection]
        missing, extra = sorted(set(a) - set(b)), sorted(set(b) - set(a))
        details = []
        for name in sorted(set(a) & set(b)):
            same_count = len(a[name]) == len(b[name])
            max_delta = max((math.dist(p, q) for p, q in zip(a[name], b[name])), default=0)
            details.append({'name': name, 'vertices': len(b[name]), 'same_vertex_count': same_count,
                            'max_world_vertex_delta_metres': max_delta,
                            'passed': same_count and max_delta <= TOLERANCE})
        result[collection] = {'missing_names': missing, 'extra_names': extra,
                              'mesh_count': len(b), 'vertex_count': sum(map(len, b.values())),
                              'meshes': details,
                              'passed': not missing and not extra and all(item['passed'] for item in details)}
    return result


def bounds(vertices):
    low = [min(v[i] for v in vertices) for i in range(3)]
    high = [max(v[i] for v in vertices) for i in range(3)]
    return {'min': low, 'max': high,
            'center': [(a + b) / 2 for a, b in zip(low, high)],
            'size': [b - a for a, b in zip(low, high)]}


def connected_room_geometry():
    result = []
    for obj in bpy.data.collections['Room'].objects:
        if obj.type != 'MESH' or not obj.data.vertices:
            continue
        vertices = [runtime(obj.matrix_world @ vertex.co) for vertex in obj.data.vertices]
        adjacent = [[] for _ in vertices]
        for edge in obj.data.edges:
            a, b = edge.vertices
            adjacent[a].append(b); adjacent[b].append(a)
        seen = set()
        for index in range(len(vertices)):
            if index in seen:
                continue
            pending = [index]; seen.add(index); indices = []
            while pending:
                current = pending.pop(); indices.append(current)
                for other in adjacent[current]:
                    if other not in seen:
                        seen.add(other); pending.append(other)
            points = [vertices[i] for i in indices]
            result.append({'source_mesh': obj.name, 'first_vertex': index,
                           'material': obj.active_material.name if obj.active_material else None,
                           'vertices': points, **bounds(points)})
    return result


def description(component):
    return {key: value for key, value in component.items() if key != 'vertices'}


def one(components, predicate, label):
    found = [c for c in components if predicate(c)]
    assert len(found) == 1, f'{label}: expected one geometry component, found {len(found)}'
    return found[0]


def fixture(layout, name):
    return next(item for item in layout['fixtures'] if item['id'] == name)


def rectangle_overrun(vertices, shape):
    c, s = math.cos(shape.get('yaw', 0)), math.sin(shape.get('yaw', 0))
    hx, hz = shape['halfSize']; cx, cz = shape['center']
    overrun = []
    for x, _, z in vertices:
        dx, dz = x - cx, z - cz
        overrun.append(max(abs(c * dx - s * dz) - hx, abs(s * dx + c * dz) - hz, 0))
    return max(overrun, default=0)


def occupancy(name, components, shape, layout):
    points = [v for item in components for v in item['vertices']]
    assert points, f'{name}: no geometry found'
    box = bounds(points)
    if 'radius' in shape:
        overrun = max(max(math.hypot(x - shape['center'][0], z - shape['center'][1]) - shape['radius'], 0)
                      for x, _, z in points)
    else:
        overrun = rectangle_overrun(points, shape)
    room = layout['room']
    contained_by_room = all(room['minX'] - OCCUPANCY_TOLERANCE <= x <= room['maxX'] + OCCUPANCY_TOLERANCE
                            and room['minZ'] - OCCUPANCY_TOLERANCE <= z <= room['maxZ'] + OCCUPANCY_TOLERANCE
                            for x, _, z in points)
    return {'components': len(components), 'vertices': len(points), 'actual_bounds': box,
            'collision_shape': shape, 'maximum_collision_shape_overrun_metres': overrun,
            'within_room_bounds': contained_by_room,
            'passed': contained_by_room and overrun <= OCCUPANCY_TOLERANCE}


def check_layout(components, layout):
    # Read the actual shape, not pre-export object names or JSON metadata.
    tops = [c for c in components if c['material'] == 'Timber'
            and abs(c['center'][1] - 1.18) < .002 and .20 < c['size'][1] < .40
            and .95 < c['size'][0] < 1.3 and .7 < c['size'][2] < 1.3]
    assert len(tops) == 5, f'Expected five separate sloped lectern tops, found {len(tops)}'
    lecterns = []
    for index, slot in enumerate(layout['slots']):
        top = min(tops, key=lambda c: math.hypot(c['center'][0] - slot['position'][0], c['center'][2] - slot['position'][2]))
        tops.remove(top)
        delta = math.hypot(top['center'][0] - slot['position'][0], top['center'][2] - slot['position'][2])
        shape = {'center': [slot['position'][0], slot['position'][2]], 'halfSize': layout['lectern']['halfSize'], 'yaw': slot['yaw']}
        overrun = rectangle_overrun(top['vertices'], shape)
        lecterns.append({'slot': index, 'geometry': description(top), 'layout_position': slot['position'],
                         'horizontal_center_error_metres': delta, 'maximum_collision_shape_overrun_metres': overrun,
                         'passed': delta < TOLERANCE and overrun <= OCCUPANCY_TOLERANCE})

    desk_top = one(components, lambda c: c['material'] == 'Timber' and abs(c['center'][1] - .94) < .002
                   and abs(c['size'][0] - 2.6) < .002 and abs(c['size'][2] - .86) < .002, 'desk top')
    seat = one(components, lambda c: c['material'] == 'Velvet' and abs(c['center'][1] - .51) < .002
               and abs(c['size'][0] - .73) < .002, 'chair seat')
    table = one(components, lambda c: c['material'] == 'Timber' and abs(c['size'][0] - 1.84) < .002
                and abs(c['size'][2] - 1.84) < .002 and abs(c['size'][1] - .13) < .002, 'round table edge')

    def neighbourhood(anchor, hx, hz, min_height, max_height):
        x, _, z = anchor['center']
        return [c for c in components if c['min'][0] >= x - hx and c['max'][0] <= x + hx
                and c['min'][2] >= z - hz and c['max'][2] <= z + hz
                and c['min'][1] >= min_height and c['max'][1] <= max_height]

    furniture = {
        'desk': occupancy('desk', neighbourhood(desk_top, 1.38, .85, -.025, 1.9), fixture(layout, 'desk'), layout),
        'chair': occupancy('chair', neighbourhood(seat, .52, .47, -.001, 1.65), fixture(layout, 'chair'), layout),
        'table': occupancy('table', neighbourhood(table, .97, .97, .079, layout['table']['topHeight'] + .02), layout['table'], layout),
    }
    for name, anchor in [('desk', desk_top), ('chair', seat), ('table', table)]:
        shape = layout['table'] if name == 'table' else fixture(layout, name)
        delta = math.hypot(anchor['center'][0] - shape['center'][0], anchor['center'][2] - shape['center'][1])
        furniture[name]['horizontal_center_error_metres'] = delta
        furniture[name]['passed'] = furniture[name]['passed'] and delta < TOLERANCE

    floor = one(components, lambda c: c['material'] == 'DarkTimber' and c['max'][1] < 0
                and c['size'][0] > 9 and c['size'][2] > 11, 'floor foundation')
    room = layout['room']
    floor_contains_navigation = floor['min'][0] <= room['minX'] < room['maxX'] <= floor['max'][0] \
        and floor['min'][2] <= room['minZ'] < room['maxZ'] <= floor['max'][2]
    return {'lecterns': lecterns, 'furniture': furniture, 'floor_geometry': description(floor),
            'navigation_inside_real_floor': floor_contains_navigation,
            'passed': all(item['passed'] for item in lecterns) and all(item['passed'] for item in furniture.values()) and floor_contains_navigation}


def hearth():
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
        # Stop at x=-4.3: the new firebricks behind this plane must not count as
        # a front jamb hit or incorrectly label the open firebox as blocked.
        return tree.ray_cast(Vector((-3.7, y, z)), Vector((-1, 0, 0)), .6)[0] is not None
    probes = [(y, round(.28 + i * .01, 2)) for y in [.08, 1.72] for i in range(165)]
    missing = [[y, z] for y, z in probes if not hit(y, z)]
    header_hits = sum(hit(.3 + i * .05, 1.84) for i in range(25))
    firebox_open = not hit(.9, 1.0)
    return {'ray_x_range': [-3.7, -4.3], 'pillar_ray_count': len(probes), 'pillar_gap_count': len(missing),
            'pillar_gap_locations': missing, 'header_hits': header_hits, 'header_ray_count': 25,
            'firebox_open': firebox_open, 'passed': not missing and header_hits == 25 and firebox_open}


layout = json.loads(LAYOUT_PATH.read_text())
before_hashes = {'baseline': digest(BASELINE), 'current': digest(CURRENT), 'layout': digest(LAYOUT_PATH)}
bpy.ops.wm.open_mainfile(filepath=str(BASELINE))
baseline_meshes = reusable_meshes()
baseline_hearth = hearth()
bpy.ops.wm.open_mainfile(filepath=str(CURRENT))
result = {
    'version': layout['version'], 'blender': bpy.app.version_string,
    'sources': {'baseline': str(BASELINE.relative_to(ROOT)), 'current': str(CURRENT.relative_to(ROOT)), 'layout': str(LAYOUT_PATH.relative_to(ROOT))},
    'sha256': before_hashes, 'unchanged_mesh_tolerance_metres': TOLERANCE,
    'occupancy_tolerance_metres': OCCUPANCY_TOLERANCE,
    'reusable_meshes': compare_meshes(baseline_meshes, reusable_meshes()),
    'layout_geometry': check_layout(connected_room_geometry(), layout),
    'hearth': {'baseline': baseline_hearth, 'current': hearth()},
    'packed_textures': sorted(image.name for image in bpy.data.images if image.packed_file),
    'scope': 'Saved source world vertices and disconnected static mesh surfaces; furniture occupancy and sampled front masonry rays. Runtime route tests and Chrome verification are separate evidence.',
}
after_hashes = {'baseline': digest(BASELINE), 'current': digest(CURRENT), 'layout': digest(LAYOUT_PATH)}
result['source_files_unchanged'] = before_hashes == after_hashes
result['passed'] = all(item['passed'] for item in result['reusable_meshes'].values()) and result['layout_geometry']['passed'] \
    and result['hearth']['current']['passed'] and baseline_hearth['pillar_gap_count'] > 0 and result['source_files_unchanged']
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
print('SCENE_GEOMETRY_CHECK', json.dumps({'passed': result['passed'], 'output': str(OUTPUT.relative_to(ROOT)),
      'reusable_meshes': {key: {'meshes': value['mesh_count'], 'vertices': value['vertex_count'], 'passed': value['passed']} for key, value in result['reusable_meshes'].items()},
      'furniture': result['layout_geometry']['furniture'], 'hearth': result['hearth']['current']}))
assert result['passed'], f'Geometry consistency failed; inspect {OUTPUT}'
