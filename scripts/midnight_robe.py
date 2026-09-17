"""Original soft wizard robe, with baked gravity/inertia-driven cloth bones.

The cloth is authored in the existing wrist-local rest coordinates and uses the
existing wrist-local basis. Original hand animation is never changed; dedicated
cloth bones provide the sleeve's non-rigid movement.
All embroidery and textile maps below are procedural original artwork, not
pixels extracted from the concept image or external costume references.
"""
from pathlib import Path
import hashlib
import json
import math

import bpy
import numpy as np
from mathutils import Vector, Matrix


def _image(root, suffix, rgb, non_color=False):
    path = root / 'assets/source' / ('midnight-robe-' + suffix + '.png')
    name = 'Midnight robe ' + suffix
    old = bpy.data.images.get(name)
    if old:
        return old
    height, width = rgb.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    if non_color:
        image.colorspace_settings.name = 'Non-Color'
    rgba = np.ones((height, width, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(rgb, 0, 1)
    image.pixels.foreach_set(rgba.ravel())
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    # Reload as a file image: glTF can then embed the exact authored PNG.
    bpy.data.images.remove(image)
    image = bpy.data.images.load(str(path), check_existing=True)
    image.name = name
    if non_color:
        image.colorspace_settings.name = 'Non-Color'
    image.pack()
    return image


def _normal(height, strength=10):
    dy, dx = np.gradient(height)
    n = np.stack((-dx * strength, -dy * strength, np.ones_like(dx)), axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return n * .5 + .5


def _maps(root):
    # Repeating cloth needs less resolution than the unique skin/embroidery.
    n = 512
    v, u = np.mgrid[0:n, 0:n].astype(np.float32) / n
    warp = np.sin(u * math.tau * 96)
    weft = np.sin(v * math.tau * 96)
    weave = .65 * warp * weft + .35 * np.sin((u + v) * math.tau * 48)
    # A quiet repeating ogee/leaf damask, intentionally original geometry.
    x = (u * 4) % 1 - .5
    y = (v * 4 + .25 * ((u * 4).astype(int) % 2)) % 1 - .5
    leaf = np.abs((x / .32) ** 2 + (y / .47) ** 2 - 1)
    motif = np.exp(-leaf * leaf * 110) * .75
    veins = np.exp(-((np.abs(x) - .29 * (1 - np.abs(y) * 2)) ** 2) * 2200)
    damask = motif + .45 * veins
    # These authored PNG pixels are sRGB values; the image node converts them
    # to linear light. Keep enough blue chroma to survive the warm room lights.
    navy = np.array((.120, .175, .300), dtype=np.float32)
    color = navy + damask[:, :, None] * np.array((.016, .023, .038))
    color += weave[:, :, None] * .0013
    outer = _image(root, 'navy-damask-color', color)
    normal = _image(root, 'woven-normal', _normal(.023 * weave + .055 * damask, 1.4), True)

    h, w = 512, 1024
    v, u = np.mgrid[0:h, 0:w].astype(np.float32)
    u /= w
    v /= h
    ink = np.zeros((h, w), dtype=np.float32)

    def line(distance, width=.005):
        nonlocal ink
        ink = np.maximum(ink, np.clip((width + .002 - np.abs(distance)) / .003, 0, 1))

    for border in (.045, .080, .140, .860, .920, .955):
        line(v - border, .0035 if border in (.14, .86) else .0045)
    # Braided selvage between the double outlines.
    for phase in (0, math.pi):
        line(v - (.11 + .013 * np.sin(u * math.tau * 36 + phase)), .002)
        line(v - (.89 + .013 * np.sin(u * math.tau * 36 + phase)), .002)
    cx = (u - .5) * 2.4
    cy = v - .5
    radius = np.sqrt(cx * cx + cy * cy)
    line(radius - .315, .004)
    line(radius - .275, .003)
    line(np.sqrt((cx * .79 + cy * .40) ** 2 + (cy * 1.60) ** 2) - .29, .003)
    line(np.sqrt((cx * .79 - cy * .40) ** 2 + (cy * 1.60) ** 2) - .29, .003)
    for i in range(8):
        a = i * math.pi / 4
        along = cx * math.cos(a) + cy * math.sin(a)
        across = -cx * math.sin(a) + cy * math.cos(a)
        ray = np.clip((.004 + .018 * (1 - along / .27) - np.abs(across)) / .004, 0, 1)
        ray *= (along >= 0) & (along < (.27 if i % 2 == 0 else .205))
        ink = np.maximum(ink, ray)
    line(cy, .002)
    for center in (.105, .895):
        mx = (u - center) * 2.4
        mr = np.sqrt(mx * mx + cy * cy)
        cut = np.sqrt((mx - .060) ** 2 + (cy + .030) ** 2)
        crescent = np.clip((.129 - mr) / .004, 0, 1) * np.clip((cut - .123) / .004, 0, 1)
        ink = np.maximum(ink, crescent)
        line(np.sqrt(mx * mx + cy * cy) - .175, .0025)
    for center in (.285, .715):
        dot = np.sqrt(((u - center) * 2.4) ** 2 + cy ** 2)
        ink = np.maximum(ink, np.clip((.014 - dot) / .004, 0, 1))
    thread = np.sin(u * math.tau * 256) * np.sin(v * math.tau * 128)
    gold = np.array((.65, .610, .510)) + thread[:, :, None] * .010
    backing = np.array((.130, .185, .300)) + thread[:, :, None] * .0013
    brocade = backing * (1 - ink[:, :, None]) + gold * ink[:, :, None]
    border = _image(root, 'star-and-moon-brocade-color', brocade)
    relief = _image(root, 'brocade-normal', _normal(ink * .11 + thread * .013, 3), True)
    return outer, normal, border, relief


def _material(name, color, roughness, image=None, normal=None, metallic=0):
    material = bpy.data.materials.get(name)
    if material:
        return material
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
    if shader is None:
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        output = next((node for node in nodes if node.type == 'OUTPUT_MATERIAL'), None)
        if output is None:
            output = nodes.new('ShaderNodeOutputMaterial')
        links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    shader.inputs['Metallic'].default_value = metallic
    # glTF emits the white sheen tint even with a tiny Blender weight; the
    # standard roughness/normal channels preserve navy cloth in the browser.
    shader.inputs['Sheen Weight'].default_value = 0
    if image:
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = image
        texture.extension = 'REPEAT'
        links.new(texture.outputs['Color'], shader.inputs['Base Color'])
    if normal:
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = normal
        texture.extension = 'REPEAT'
        tangent = nodes.new('ShaderNodeNormalMap')
        tangent.inputs['Strength'].default_value = .22
        links.new(texture.outputs['Color'], tangent.inputs['Color'])
        links.new(tangent.outputs['Normal'], shader.inputs['Normal'])
    return material


def _mesh(name, arm, side, vertices, faces, uv_faces, material, wrist_blend=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = arm
    uv = mesh.uv_layers.new(name='RobeUV')
    for polygon, coordinates in zip(mesh.polygons, uv_faces):
        polygon.use_smooth = True
        for index, coordinate in zip(polygon.loop_indices, coordinates):
            uv.data[index].uv = coordinate
    forearm = obj.vertex_groups.new(name='lowerarm02.' + side)
    wrist = obj.vertex_groups.new(name='wrist.' + side) if wrist_blend else None
    direction = arm.data.bones['lowerarm02.' + side].head_local.normalized()
    for i, position in enumerate(vertices):
        distance = Vector(position).dot(direction)
        # Match the adjacent source skin (about 7–12% wrist influence), so
        # the fitted cuff does not lift away from the forearm when the wrist bends.
        weight = min(.10, max(0, (.16 - distance) * .85)) if wrist_blend else 0
        forearm.add([i], 1 - weight, 'REPLACE')
        if weight:
            wrist.add([i], weight, 'REPLACE')
    modifier = obj.modifiers.new('Existing forearm deformation', 'ARMATURE')
    modifier.object = arm
    return obj


def _surface(name, arm, side, rows, segments, point, uv_for, material, thickness=0, lining=None, wrist=False):
    vertices = []
    faces = []
    uv_faces = []
    for row in rows:
        for j in range(segments):
            vertices.append(point(row, j * math.tau / segments))
    for i in range(len(rows) - 1):
        for j in range(segments):
            a, b = j * math.tau / segments, (j + 1) * math.tau / segments
            faces.append((i * segments + j, (i + 1) * segments + j,
                          (i + 1) * segments + (j + 1) % segments, i * segments + (j + 1) % segments))
            uv_faces.append((uv_for(rows[i], a), uv_for(rows[i + 1], a),
                             uv_for(rows[i + 1], b), uv_for(rows[i], b)))
    obj = _mesh(name, arm, side, vertices, faces, uv_faces, material, wrist)
    if thickness:
        if lining:
            obj.data.materials.append(lining)
        solid = obj.modifiers.new('Real cloth edge and lining', 'SOLIDIFY')
        solid.thickness = thickness
        solid.offset = -1
        solid.use_even_offset = True
        solid.material_offset = 1 if lining else 0
        solid.material_offset_rim = 1 if lining else 0
        # Apply only the construction modifier, preserving the live armature.
        obj.modifiers.move(len(obj.modifiers) - 1, 0)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=solid.name)
    return obj


_CLOTH_STATIONS = (.050, .230, .550, 1.100)
_CLOTH_SECTORS = 6


def _axes(arm, side):
    direction = arm.data.bones['lowerarm02.' + side].head_local.normalized()
    forward = -direction
    xx = Vector((1, 0, 0))
    xx = (xx - forward * xx.dot(forward)).normalized()
    return direction, xx, xx.cross(forward).normalized()


def _cloth_bones(arm, side, clothes):
    """A 4 by 6 cloth cage; bilinear weights use at most four influences."""
    direction, xx, zz = _axes(arm, side)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    for station, distance in enumerate(_CLOTH_STATIONS):
        for sector in range(_CLOTH_SECTORS):
            a = math.tau * sector / _CLOTH_SECTORS
            bone = arm.data.edit_bones.new(f'robe_{station:02}_{sector:02}.{side}')
            bone.head = direction * distance + xx * math.cos(a) * .060 + zz * math.sin(a) * .055
            bone.tail = bone.head - direction * .040
            bone.parent = arm.data.edit_bones['lowerarm02.' + side]
            bone.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in clothes:
        if obj.name.endswith('CuffFacing'):
            continue
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        groups = {(i, j): obj.vertex_groups.new(name=f'robe_{i:02}_{j:02}.{side}')
                  for i in range(len(_CLOTH_STATIONS)) for j in range(_CLOTH_SECTORS)}
        for vertex in obj.data.vertices:
            distance = vertex.co.dot(direction)
            station = min(len(_CLOTH_STATIONS) - 2,
                          max(0, next((i - 1 for i, d in enumerate(_CLOTH_STATIONS) if d > distance), len(_CLOTH_STATIONS) - 2)))
            fraction = max(0, min(1, (distance - _CLOTH_STATIONS[station]) /
                                     (_CLOTH_STATIONS[station + 1] - _CLOTH_STATIONS[station])))
            angle = math.atan2(vertex.co.dot(zz), vertex.co.dot(xx)) % math.tau
            radial = angle / math.tau * _CLOTH_SECTORS
            sector = int(radial)
            phase = radial - sector
            for i, along in ((station, 1 - fraction), (station + 1, fraction)):
                for j, around in ((sector, 1 - phase), ((sector + 1) % _CLOTH_SECTORS, phase)):
                    weight = along * around
                    if weight > 1e-7:
                        groups[i, j].add([vertex.index], weight, 'REPLACE')


def build_robe(arm, side, label, root):
    """Build one navy robe directly at the wrist; there is no inner sleeve.

    The short internal facing closes the cropped forearm behind the open hem.
    It is a transverse construction surface, not a second forearm sleeve.
    Call bake_robe_deformation after the existing hand action has been baked.
    """
    root = Path(root)
    outer_map, cloth_normal, trim_map, trim_normal = _maps(root)
    outer = _material('Soft midnight woven robe', (.016, .025, .055), .91, outer_map, cloth_normal)
    lining = _material('Midnight blue soft lining', (.016, .026, .047), .92)
    trim = _material('Soft silver gold celestial embroidery', (.43, .41, .34), .76, trim_map, trim_normal, .06)
    piping = _material('Soft woven hem thread', (.32, .29, .23), .82, metallic=.04)
    direction, xx, zz = _axes(arm, side)
    mirror = 1 if side == 'R' else -1

    def outer_point(t, a, lift=0):
        down = max(0, -math.sin(a))
        # A true slanted robe opening: dorsal edge behind the wrist, lower
        # panel extending forward beneath it. This is not a shirt cuff ring.
        opening = .070 + .025 * max(0, math.sin(a)) - .090 * down ** 1.4 + .012 * math.cos(a) * mirror
        distance = opening + t * (1.20 - opening)
        distal = math.exp(-t * 5)
        width = (.085 - .030 * distal) * (1 - .13 * down ** 1.5 * distal)
        top = .077 - .022 * distal
        bottom = .104 + .029 * distal
        phase = a + .24 * math.sin(t * 8) + mirror * .10
        fold = (.003 + .004 * down) * math.cos(2 * phase + t * 4)

        def angular_patch(center, spread):
            delta = math.atan2(math.sin(a - center), math.cos(a - center))
            return math.exp(-(delta / spread) ** 2)

        # Three broad folds gather where the weight of the open sleeve pulls
        # on its upper cloth. Local angular patches avoid corrugated rings.
        upper_fold = angular_patch(1.30, .88)
        fold += .012 * upper_fold * math.exp(-((distance - (.215 + .025 * math.cos(a))) / .019) ** 2)
        fold -= .0085 * upper_fold * math.exp(-((distance - (.247 + .020 * math.cos(a))) / .016) ** 2)
        side_fold = angular_patch(.30 if side == 'R' else 2.84, .96)
        fold += .012 * side_fold * math.exp(-((distance - (.345 + .034 * math.sin(a))) / .025) ** 2)
        fold -= .008 * side_fold * math.exp(-((distance - .390) / .020) ** 2)
        lower_fold = angular_patch(4.28, .84)
        fold += .012 * lower_fold * math.exp(-((distance - (.165 + .023 * math.cos(a))) / .027) ** 2)
        fold -= .007 * lower_fold * math.exp(-((distance - .206) / .020) ** 2)
        # A slow crease further up the cloth prevents the visible proximal
        # proxy from becoming one immaculate straight uniform tube.
        fold += .0085 * angular_patch(2.04, 1.05) * math.exp(-((distance - (.66 + .06 * math.cos(a))) / .075) ** 2)
        # A gentle sideways fall/curl keeps the hanging panel from becoming
        # a perfectly symmetric stiff funnel around the forearm.
        center = direction * distance - zz * .005 + xx * (.014 * down ** 3 * distal ** 2 * mirror)
        return (center + xx * math.cos(a) * (width + fold * .60 + lift)
                + zz * math.sin(a) * ((top if math.sin(a) >= 0 else bottom) + fold + lift))

    # Concentrate topology where real fold peaks/valleys need curvature;
    # proximal cloth keeps coarse spacing instead of uniformly inflating GLB.
    rows = sorted(set([i * .006 for i in range(61)] + [.39 + i * .03 for i in range(12)] + [.78, .86, .94, 1.0]), reverse=True)
    clothes = [_surface(label + 'OuterRobe', arm, side, rows, 64, outer_point,
                        lambda t, a: (a / math.tau * 2.2, t * 4.6), outer, .0014, lining)]
    trim_rows = [.049, .041, .033, .025, .017, .009, .001]
    clothes.append(_surface(label + 'CelestialCuff', arm, side, trim_rows, 72,
                            lambda t, a: outer_point(t, a, .0009),
                            lambda t, a: (a / math.tau * 3, (t - .001) / .048), trim))
    for edge, radius in ((0, .00050), (.051, .00040)):
        vertices, faces, uv_faces = [], [], []
        for j in range(72):
            a = math.tau * j / 72
            center = outer_point(edge, a, .00075)
            radial = (xx * math.cos(a) + zz * math.sin(a)).normalized()
            tangent = (outer_point(edge, a + .001, .00075) - center).normalized()
            cross = tangent.cross(radial).normalized()
            for k in range(5):
                b = math.tau * k / 5
                vertices.append(center + radial * math.cos(b) * radius + cross * math.sin(b) * radius)
        for j in range(72):
            for k in range(5):
                faces.append((j * 5 + k, ((j + 1) % 72) * 5 + k,
                              ((j + 1) % 72) * 5 + (k + 1) % 5, j * 5 + (k + 1) % 5))
                uv_faces.append(((j / 72, k / 5), ((j + 1) / 72, k / 5),
                                 ((j + 1) / 72, (k + 1) / 5), (j / 72, (k + 1) / 5)))
        clothes.append(_mesh(label + ('HemPiping' if edge == 0 else 'BorderPiping'), arm, side,
                             vertices, faces, uv_faces, piping))

    # Recessed annular facing hides the source skin's proximal crop. It never
    # extends to the exposed wrist and does not recreate the rejected sleeve.
    skin = bpy.data.objects.get(label + 'Skin')
    section = []
    if skin:
        for edge in skin.data.edges:
            a, b = (skin.data.vertices[i].co for i in edge.vertices)
            da, db = a.dot(direction), b.dot(direction)
            if (da - .112) * (db - .112) <= 0 and abs(da - db) > 1e-8:
                p = a.lerp(b, (.112 - da) / (db - da))
                px, pz = p.dot(xx), p.dot(zz)
                section.append((math.atan2(pz, px) % math.tau, math.hypot(px, pz)))
    section.sort()

    def fitted_radius(angle):
        if not section:
            return 1 / math.sqrt((math.cos(angle) / .0395) ** 2 + (math.sin(angle) / .0410) ** 2)
        samples = [(section[-1][0] - math.tau, section[-1][1]), *section,
                   (section[0][0] + math.tau, section[0][1])]
        angle %= math.tau
        for (a0, r0), (a1, r1) in zip(samples, samples[1:]):
            if a0 <= angle <= a1:
                factor = (angle - a0) / max(a1 - a0, 1e-8)
                return r0 + (r1 - r0) * factor + .0006
        return .0395

    def facing_point(t, a):
        radius = fitted_radius(a)
        inside = direction * .112 + (xx * math.cos(a) + zz * math.sin(a)) * radius
        outside = outer_point(.085, a) - (xx * math.cos(a) + zz * math.sin(a)) * .002
        return inside.lerp(outside, t)
    clothes.append(_surface(label + 'CuffFacing', arm, side, [1, .66, .33, 0], 72,
                            facing_point, lambda t, a: (a / math.tau, t), lining, .0010, lining))
    _cloth_bones(arm, side, clothes)
    arm['robe_side'] = side
    arm['robe_root'] = str(root)
    paths = [root / 'assets/source' / ('midnight-robe-' + suffix + '.png') for suffix in
             ('navy-damask-color', 'woven-normal', 'star-and-moon-brocade-color', 'brocade-normal')]
    metadata = {
        'reference': 'design/round-07-wizard-robes/02-midnight-tower-mage.png',
        'reference_sha256': 'a341540ff20bc5eb4bce825ca728d5224b7dbf9f8476f3d8edd692cca05d7483',
        'user_revision': 'Remove the green/teal inner sleeve entirely; soften navy cloth and deform it during the existing motion.',
        'provenance': 'Original procedural geometry and textile/embroidery artwork; no reference-image pixels used.',
        'generator': 'scripts/midnight_robe.py',
        'construction': 'Single navy sleeve ending close to the wrist, thin lined open hem, recessed transverse facing and celestial embroidery. No InnerSleeve mesh or teal material.',
        'deformation': '24 dedicated cloth bones per arm, four skinning influences maximum. Bake gravity and inertia response after the original hand action.',
        'local_dimensions_metres': {'dorsal_cuff_from_wrist': .095, 'side_cuff_from_wrist_range': [.058, .082], 'palm_cuff_from_wrist': -.020, 'cuff_side_half_width': .055, 'cuff_lower_drape_depth': .133, 'localized_broad_fold_relief': [.0085, .012], 'outer_thickness': .0014, 'recessed_facing_from_wrist': .112, 'proximal_camera_proxy_extent': 1.20},
        'limits': ['Proximal arm remains a camera proxy.', 'Reduced cloth model uses damped gravity/inertia-driven bones, not a general cloth solver or automatic book collision simulation.'],
        'textures': [{'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
    }
    (root / 'assets/source/midnight-robe-provenance.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    return clothes


def bake_robe_deformation(arm, robes, fps=30, frame_start=0, frame_end=105, root=None):
    """Bake damped sleeve response without changing any original hand channel.

    Moving forearm acceleration produces inertia, projected world gravity
    changes the drape as the arm turns, and a damped spring settles each cloth
    cage node. Translations become ordinary glTF skin animation tracks.
    """
    side = arm.get('robe_side', 'R' if arm.name.startswith('Right') else 'L')
    direction, xx, zz = _axes(arm, side)
    scene = bpy.context.scene
    previous_frame = scene.frame_current
    forearm_name = 'lowerarm02.' + side
    rest = arm.data.bones[forearm_name].matrix_local.copy()
    rest_inverse = rest.inverted()
    names = [f'robe_{i:02}_{j:02}.{side}' for i in range(len(_CLOTH_STATIONS)) for j in range(_CLOTH_SECTORS)]
    matrices, anchors = [], []
    for frame in range(frame_start, frame_end + 1):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        deform = arm.pose.bones[forearm_name].matrix @ rest_inverse
        matrices.append(deform.copy())
        anchors.append([deform @ arm.data.bones[name].head_local for name in names])
    gravity = Vector((0, 0, -1))
    positions = [Vector((0, 0, 0)) for _ in names]
    velocities = [Vector((0, 0, 0)) for _ in names]
    minimum = [Vector((float('inf'),) * 3) for _ in names]
    maximum = [Vector((float('-inf'),) * 3) for _ in names]
    dt = 1 / fps
    for index, frame in enumerate(range(frame_start, frame_end + 1)):
        scene.frame_set(frame)
        deform = matrices[index]
        rotation = deform.to_3x3()
        inverse_rotation = rotation.inverted()
        axis_world = (rotation @ direction).normalized()
        projected_gravity = gravity - axis_world * gravity.dot(axis_world)
        for node, name in enumerate(names):
            station, sector = divmod(node, _CLOTH_SECTORS)
            distance = _CLOTH_STATIONS[station]
            a = math.tau * sector / _CLOTH_SECTORS
            upper = max(0, math.sin(a))
            distal = math.exp(-distance * 2.4)
            freedom = .30 + .70 * (1 - upper)
            # Keep the dorsal lip above the skin; the lower and side cloth
            # can settle visibly, while proximal cloth moves more gently.
            sag = (.009 + .020 * distal) * freedom
            rest_sag = rotation @ (-zz * sag)
            target = projected_gravity * sag - rest_sag
            if 0 < index < len(matrices) - 1:
                acceleration = (anchors[index + 1][node] - anchors[index][node] * 2 + anchors[index - 1][node]) / (dt * dt)
                inertia = -acceleration * (.0024 + .0018 * distal) * freedom
                if inertia.length > .025:
                    inertia *= .025 / inertia.length
                target += inertia
            if index == 0:
                positions[node] = target.copy()
            # Four substeps give reproducible, stable damped response at 30fps.
            sub_dt = dt / 4
            for _ in range(4):
                velocities[node] += ((target - positions[node]) * 95 - velocities[node] * 17) * sub_dt
                positions[node] += velocities[node] * sub_dt
            local_delta = inverse_rotation @ positions[node]
            # Avoid pulling the sleeve into the anatomical core. The upper
            # rim is pinned more strongly than the hanging lower/side panels.
            if station == 0:
                local_delta *= .24 if upper > 0 else .65
            if local_delta.length > .050:
                local_delta *= .050 / local_delta.length
            radial = xx * math.cos(a) + zz * math.sin(a)
            inward = local_delta.dot(radial)
            min_inward = (-.0006 if upper > 0 else -.0020) if station == 0 else -.006
            if inward < min_inward:
                local_delta += radial * (min_inward - inward)
            if station == 0:
                max_outward = .0035 if upper > 0 else (.008 if abs(math.sin(a)) < .1 else .021)
                outward = local_delta.dot(radial)
                if outward > max_outward:
                    local_delta -= radial * (outward - max_outward)
            # A small motion-dependent crease response keeps broad folds from
            # behaving like a single rotating pipe, without periodic noise.
            speed = velocities[node].length
            crease = min(.0035, speed * .025) * math.sin(a * 2 + distance * 17)
            local_delta += radial * crease
            world_delta = rotation @ local_delta
            bone = arm.pose.bones[name]
            target_matrix = deform @ bone.bone.matrix_local
            target_matrix.translation += world_delta
            bone.matrix = target_matrix
            bone.keyframe_insert(data_path='location', frame=frame, group=name)
            for axis in range(3):
                minimum[node][axis] = min(minimum[node][axis], local_delta[axis])
                maximum[node][axis] = max(maximum[node][axis], local_delta[axis])
        bpy.context.view_layer.update()
    scene.frame_set(previous_frame)
    spans = [(maximum[i] - minimum[i]).length for i in range(len(names))]
    result = {'side': side, 'cloth_bones': len(names), 'sampled_frames': frame_end - frame_start + 1,
              'minimum_node_motion_span_metres': min(spans), 'maximum_node_motion_span_metres': max(spans),
              'original_hand_channels_modified': False, 'model': 'Damped gravity/inertia-driven cloth cage; no runtime physics dependency.'}
    root = Path(root or arm['robe_root'])
    path = root / 'assets/source/midnight-robe-provenance.json'
    metadata = json.loads(path.read_text())
    metadata.setdefault('baked_deformation', {})[side] = result
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    return result
