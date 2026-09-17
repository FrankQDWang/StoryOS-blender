"""Rest-shape and exportable skin refinements for the selected midnight mage.

The MakeHuman topology, UVs, skin weights and skeleton remain authoritative.
Rest sculpting and bone-driven corrective morphs use those landmarks. Units
are the existing hand asset's metres before the runtime reference scale (0.824).
"""
from pathlib import Path
import math
import hashlib

import bpy
import numpy as np
from mathutils import Vector


HAND_REFINEMENT_METADATA = {
    'version': 'midnight-mage-anatomy-v2',
    'reference': 'design/round-07-wizard-robes/02-midnight-tower-mage.png',
    'control_cage_changes': [
        'Wrist breadth +10 percent and depth +9 percent at peak, smoothly blended proximally and into palm.',
        'Separate thenar/hypothenar pads and softly cupped palm, without narrowing the forearm.',
        'MCP arch, metacarpal extensor routes, intermetacarpal hollows and distal radius/ulna contours selected by surface normals.',
        'Phalangeal pads and joint/shaft cross-section variation; original bones and longitudinal fingertip reach retained.',
    ],
    'post_subdivision_changes': [
        'Fine dorsal tendon and intermetacarpal relief on the subdivided export mesh, before Basis creation.',
        'Exact CC0 source-UV nail perimeter micro-sculpt, without new geometry islands or guessed nail regions.',
    ],
    'correctives': {
        'count_per_hand': 5,
        'type': 'Baked glTF morph target weights; no runtime Blender drivers',
        'response': 'Original proximal/middle finger flexion, smooth threshold 0.12 to 1.20 radians.',
        'affected_regions': 'Dorsal knuckles and thenar volume; distal contact regions protected.',
        'idle_policy': 'Low-flexion poses keep low weights; no independent motion or artificial oscillation.',
    },
    'surface_changes': [
        'No albedo-derived normal noise; restrained anatomical folds and exact source-mask nail bed normals.',
        'Skin roughness approximately 0.49, nail roughness 0.25, subtle source-linked roughness variation.',
        'Softened source pigment speckle and compressed broad brown-patch variation to 68 percent; subtle joint/nail hue variation retained.',
        '2K colour atlas, normal and roughness capped at 1K.',
        'Blender-only subsurface scattering disabled so offline views use the same opaque PBR capability as glTF.',
    ],
    'preserved': 'Source topology, UV correspondence, skin weights, bones, bone lengths and animation authority.',
    'limits': 'Authored anatomical sculpt and flexion response, not scanned skin, photogrammetry or a muscle/soft-tissue simulation.',
}


def _gaussian(value, centre, radius):
    return math.exp(-((value - centre) / radius) ** 2)


def _smoothstep(low, high, value):
    u = min(1.0, max(0.0, (value - low) / (high - low)))
    return u * u * (3.0 - 2.0 * u)


def refine_hand_shape(obj, arm, side):
    """Refine the cropped original mesh before subdivision; never edit bones.

    Fuller carpal volume is blended into the unaltered proximal forearm.
    Dorsal metacarpal ridges and knuckle forms follow the actual source bones.
    Distal phalanges and thumb tip are deliberately unchanged, preserving the
    current side-grip contact geometry. No new vertices, UVs or weights.
    """
    bones = arm.data.bones
    wrist = bones['wrist.' + side].head_local.copy()
    palm_end = bones['finger3-1.' + side].head_local.copy()
    palm_length = (palm_end - wrist).length
    # Source anatomy is mirrored around X; the local dorsal direction is +Z.
    radial_sign = -1.0 if side == 'R' else 1.0
    group_names = {group.index: group.name for group in obj.vertex_groups}
    obj.data.update()
    surface_normals = [vertex.normal.copy() for vertex in obj.data.vertices]
    before = [vertex.co.copy() for vertex in obj.data.vertices]
    modified = 0
    maximum = 0.0
    for vertex in obj.data.vertices:
        p = vertex.co.copy()
        x, y, z = p
        offset = Vector((0, 0, 0))
        # The wrist was disproportionately narrow under the former sleeve.
        # Peak +10% breadth, +9% depth, tapering smoothly in both directions.
        wrist_envelope = _gaussian(y, -.006, .049)
        wrist_envelope *= 1.0 - _smoothstep(.065, .105, y)
        wrist_envelope *= _smoothstep(-.128, -.085, y)
        offset.x += (x - wrist.x) * .10 * wrist_envelope
        offset.z += (z - wrist.z) * .09 * wrist_envelope

        # Palm volume remains generous. A shallow dorsal arch joins carpus
        # and knuckles instead of shrinking the palm to imply elegance.
        palm = _gaussian(y, palm_length * .51, palm_length * .40)
        palm *= _gaussian(x, radial_sign * .003, .056)
        # The relaxed hand curves below z=0 at the MCP heads. Select the
        # actual dorsal surface by its normal, never by absolute z height.
        dorsal = _smoothstep(.05, .76, surface_normals[vertex.index].z)
        offset.z += .0008 * palm * dorsal
        offset.z += z * .035 * palm

        # Thenar pad: strengthen the thumb-root transition on the palm side;
        # actual thumb distal phalanges and contact pad are not touched.
        thenar = _gaussian(x, radial_sign * .033, .024)
        thenar *= _gaussian(y, .047, .035)
        palmar = _smoothstep(.05, .76, -surface_normals[vertex.index].z)
        offset.z -= .0040 * thenar * palmar
        offset.x += radial_sign * .0015 * thenar * palmar
        # The hypothenar pad balances the thumb mound; the middle palm is
        # softly cupped rather than a single uniformly inflated surface.
        hypothenar = _gaussian(x, -radial_sign * .035, .016) * _gaussian(y, .064, .046)
        offset.z -= .0028 * hypothenar * palmar
        central_cup = _gaussian(x, 0, .021) * _gaussian(y, .072, .033)
        offset.z += .0010 * central_cup * palmar

        # Extensor forms follow each real metacarpal route. These are broad,
        # sub-millimetre elevations, not cords or drawn veins.
        for digit in range(2, 6):
            end = bones[f'finger{digit}-1.{side}'].head_local
            start = wrist.lerp(end, .33)
            direction = end - start
            t = (p - start).dot(direction) / direction.length_squared
            tc = min(1.0, max(0.0, t))
            route = start + direction * tc
            tendon = _gaussian(x, route.x, .0055)
            tendon *= _smoothstep(.02, .25, t) * (1 - _smoothstep(.78, 1.05, t))
            offset.z += .0026 * tendon * dorsal
            knuckle = _gaussian(x, end.x, .0090) * _gaussian(y, end.y, .011)
            offset.z += .0030 * knuckle * dorsal

        # The intermetacarpal hollows are as important as raised tendons. They
        # separate the four MCP heads into a natural arch instead of a slab.
        for first, second in ((2, 3), (3, 4), (4, 5)):
            a = bones[f'finger{first}-1.{side}'].head_local
            b = bones[f'finger{second}-1.{side}'].head_local
            end = (a + b) * .5
            t = min(1, max(0, y / end.y))
            route_x = wrist.x * (1 - t) + end.x * t
            valley = _gaussian(x, route_x, .0058)
            valley *= _smoothstep(.035, .068, y) * (1 - _smoothstep(end.y - .007, end.y + .012, y))
            offset.z -= .0019 * valley * dorsal

        # Distal radius/ulna remain rounded under skin, but create the small
        # asymmetric bony changes of plane visible at an adult wrist.
        radius = _gaussian(x, radial_sign * .027, .012) * _gaussian(y, -.018, .015)
        ulna = _gaussian(x, -radial_sign * .027, .010) * _gaussian(y, -.002, .012)
        offset.z += (.0015 * radius + .0020 * ulna) * dorsal

        # A little radial volume in proximal/middle fingers; no length change,
        # no global scale and no change to nail/tip geometry. Skinning weights
        # smoothly select the original phalanx cross sections.
        finger_offset = Vector((0, 0, 0))
        for membership in vertex.groups:
            name = group_names[membership.group]
            if not name.startswith('finger') or not name.endswith('.' + side):
                continue
            digit, joint = map(int, name.split('.')[0][6:].split('-'))
            if digit == 1 or joint == 3:
                continue
            bone = bones[name]
            axis = (bone.tail_local - bone.head_local).normalized()
            along = (p - bone.head_local).dot(axis)
            centre = bone.head_local + axis * along
            cross_section = p - centre
            # Give each phalanx a soft finger pad, narrowing between joints.
            # The dorsal/lateral knuckle flare is separate from pad fullness.
            t = along / max(bone.length, 1e-6)
            shaft = math.sin(math.pi * max(0, min(1, t))) ** 2
            joint_flare = _gaussian(t, 0, .22) + _gaussian(t, 1, .20)
            lateral_strength = .045 + .065 * joint_flare - .025 * shaft
            depth_strength = .075 + .070 * shaft
            cross_offset = Vector((cross_section.x * lateral_strength,
                                   0,
                                   cross_section.z * depth_strength))
            # Cross-section shaping never changes the rest longitudinal reach.
            cross_offset -= axis * cross_offset.dot(axis)
            finger_offset += cross_offset * membership.weight
        offset += finger_offset
        distal_weight = sum(membership.weight for membership in vertex.groups
                            if group_names[membership.group].startswith('finger')
                            and group_names[membership.group].endswith('-3.' + side))
        offset *= 1.0 - _smoothstep(.35, .80, distal_weight)
        vertex.co += offset
        length = offset.length
        modified += int(length > 1e-7)
        maximum = max(maximum, length)
    obj.data.update()
    return {
        'side': side,
        'vertices': len(before),
        'modified_vertices': modified,
        'maximum_rest_offset_asset_metres': round(maximum, 7),
        'wrist_peak_breadth_factor': 1.10,
        'wrist_peak_depth_factor': 1.09,
        'topology_uv_weights_bones_preserved': True,
        'distal_phalanges_not_radially_scaled': True,
        'sculpt': 'Surface-normal selected dorsal/palmar sculpt; separate thenar/hypothenar pads, metacarpal tendons and interosseous hollows, MCP arch, distal radius/ulna, phalanx pads.',
    }


def _polish_dorsal_surface(obj, arm, side):
    """Resolve narrow anatomical forms after the source cage is subdivided.

    The 1,721-vertex control cage averages these features away. Apply them on
    the 6,859-vertex export surface before Basis/corrective keys are created.
    """
    bones = arm.data.bones
    wrist = bones['wrist.' + side].head_local
    normals = [v.normal.copy() for v in obj.data.vertices]
    maximum = 0.0
    for vertex in obj.data.vertices:
        x, y, z = vertex.co
        dorsal = _smoothstep(.1, .8, normals[vertex.index].z)
        relief = 0.0
        for digit in range(2, 6):
            end = bones[f'finger{digit}-1.{side}'].head_local
            t = max(0, min(1, y / end.y))
            # The route fans out from the carpus instead of extending four
            # parallel ridges through the wrist, as on an anatomical hand.
            centre_x = wrist.x * (1 - t) + end.x * t
            envelope = _smoothstep(.025, .058, y) * (1 - _smoothstep(end.y - .005, end.y + .010, y))
            relief += .0015 * _gaussian(x, centre_x, .0040) * envelope
            relief += .0019 * _gaussian(x, end.x, .0068) * _gaussian(y, end.y - .001, .008)
        for first, second in ((2, 3), (3, 4), (4, 5)):
            a, b = bones[f'finger{first}-1.{side}'].head_local, bones[f'finger{second}-1.{side}'].head_local
            end = (a + b) * .5
            t = max(0, min(1, y / end.y))
            centre_x = wrist.x * (1 - t) + end.x * t
            envelope = _smoothstep(.040, .066, y) * (1 - _smoothstep(end.y - .012, end.y + .006, y))
            relief -= .0012 * _gaussian(x, centre_x, .0048) * envelope
        dz = relief * dorsal
        vertex.co.z += dz
        maximum = max(maximum, abs(dz))

    # Upstream's exact nail mask identifies the perimeter. Add a tiny cuticle
    # recess, not a floating nail primitive or guessed region around each tip.
    source_uv = obj.data.uv_layers.get('SourceUV') or obj.data.uv_layers[0]
    mask_path = Path(__file__).resolve().parents[1] / 'assets/source/mage-hand-source-fingernails.jpg'
    image = bpy.data.images.load(str(mask_path), check_existing=False)
    image.colorspace_settings.name = 'Non-Color'
    pixels = np.empty(image.size[0] * image.size[1] * 4, np.float32)
    image.pixels.foreach_get(pixels)
    mask = pixels.reshape(image.size[1], image.size[0], 4)[:, :, 0]
    uv = np.array([item.uv[:] for item in source_uv.data], np.float32)
    amount = _bilinear(mask, uv[:, 0], uv[:, 1])
    sums, counts = np.zeros(len(obj.data.vertices)), np.zeros(len(obj.data.vertices))
    for loop, value in zip(obj.data.loops, amount):
        sums[loop.vertex_index] += value
        counts[loop.vertex_index] += 1
    weights = sums / np.maximum(counts, 1)
    # Only Z changes: neither phalanx length nor fingertip reach is altered.
    for vertex, weight in zip(obj.data.vertices, weights):
        edge = 4 * weight * (1 - weight)
        vertex.co.z += .00010 * weight - .00025 * edge
    bpy.data.images.remove(image)
    obj.data.update()
    return {'maximum_dorsal_relief_asset_metres': round(maximum, 7),
            'source_mask_nail_vertices': int(np.count_nonzero(weights > .2)),
            'reason': 'Fine anatomical relief applied after subdivision so source control cage does not erase it.'}


def add_hand_correctives(obj, arm, side):
    """Add five glTF morphs after subdivision, before animation baking.

    These restore a little dorsal knuckle/thenar volume as the original skin
    bends. They do not move the skeleton, fingertips, nails, UVs or contacts.
    """
    if obj.data.shape_keys is not None:
        raise ValueError('Hand correctives require the baked macro mesh without existing shape keys')
    surface_polish = _polish_dorsal_surface(obj, arm, side)
    obj.shape_key_add(name='Basis', from_mix=False)
    positions = [vertex.co.copy() for vertex in obj.data.vertices]
    surface_normals = [vertex.normal.copy() for vertex in obj.data.vertices]
    group_names = {group.index: group.name for group in obj.vertex_groups}
    protected = []
    for vertex in obj.data.vertices:
        distal = sum(item.weight for item in vertex.groups
                      if group_names[item.group].startswith('finger')
                      and group_names[item.group].endswith('-3.' + side))
        protected.append(1 - _smoothstep(.25, .75, distal))
    statistics = []
    for digit in range(1, 6):
        key = obj.shape_key_add(name=f'MageFlex{digit}', from_mix=False)
        key.slider_min, key.slider_max = 0, 1
        maximum, count = 0, 0
        for i, p in enumerate(positions):
            offset = Vector((0, 0, 0))
            if digit == 1:
                radial = -1 if side == 'R' else 1
                thenar = _gaussian(p.x, radial * .035, .025) * _gaussian(p.y, .049, .036)
                palmar = _smoothstep(.05, .76, -surface_normals[i].z)
                offset.z -= .0024 * thenar * palmar
                offset.x += radial * .0013 * thenar * palmar
            else:
                for joint in (1, 2):
                    bone = arm.data.bones[f'finger{digit}-{joint}.{side}']
                    delta = p - bone.head_local
                    axis = (bone.tail_local - bone.head_local).normalized()
                    along = delta.dot(axis)
                    lateral = Vector((0, 0, 1)).cross(axis).normalized()
                    across = delta.dot(lateral)
                    dorsal = _smoothstep(.05, .76, surface_normals[i].z)
                    envelope = _gaussian(along, -.001, .013 if joint == 1 else .009)
                    envelope *= _gaussian(across, 0, .012)
                    # Restore the part flattened by linear blended skinning,
                    # while distributing lateral skin stretch over the joint.
                    offset.z += .0025 * envelope * dorsal
                    offset += lateral * across * .055 * envelope
            offset *= protected[i]
            key.data[i].co = p + offset
            maximum = max(maximum, offset.length)
            count += int(offset.length > 1e-7)
        statistics.append({'digit': digit, 'affected_vertices': count,
                           'maximum_offset_asset_metres': round(maximum, 7)})
    return {'surface_polish': surface_polish, 'morphs': statistics,
            'source': 'Authored flexion volume correctives, not a soft-body simulation'}


def bake_hand_correctives(obj, arm, side, frame):
    """Call after each pose update; keyframe glTF morph weights, no drivers."""
    if obj.data.shape_keys is None:
        raise ValueError('Call add_hand_correctives before baking')
    for digit in range(1, 6):
        proximal = arm.pose.bones[f'finger{digit}-1.{side}'].rotation_quaternion.angle
        middle = arm.pose.bones[f'finger{digit}-2.{side}'].rotation_quaternion.angle
        flexion = (.60 * proximal + .40 * middle) if digit > 1 else proximal
        key = obj.data.shape_keys.key_blocks[f'MageFlex{digit}']
        key.value = _smoothstep(.12, 1.20, flexion)
        key.keyframe_insert(data_path='value', frame=frame)
    obj.data.shape_keys.animation_data.action.name = 'OpenBook' + obj.name + 'SkinResponse'


def _blur(array, radius):
    """Separable box filter, with edge padding rather than UV wraparound."""
    result = array
    for axis in (0, 1):
        padding = [(0, 0)] * result.ndim
        padding[axis] = (radius, radius)
        padded = np.pad(result, padding, mode='edge')
        cumulative = np.cumsum(padded, axis=axis, dtype=np.float32)
        shape = list(cumulative.shape)
        shape[axis] = 1
        cumulative = np.concatenate((np.zeros(shape, np.float32), cumulative), axis=axis)
        front = [slice(None)] * result.ndim
        back = [slice(None)] * result.ndim
        front[axis] = slice(2 * radius + 1, None)
        back[axis] = slice(None, -(2 * radius + 1))
        result = (cumulative[tuple(front)] - cumulative[tuple(back)]) / (2 * radius + 1)
    return result


def _save_map(name, values, path):
    height, width = values.shape[:2]
    image = bpy.data.images.new(name, width=width, height=height, alpha=False)
    image.colorspace_settings.name = 'Non-Color'
    image.pixels.foreach_set(np.asarray(values, dtype=np.float32).ravel())
    image.filepath_raw = str(path)
    image.file_format = 'PNG'
    image.save()
    image.pack()
    return image


def _bilinear(values, u, v):
    height, width = values.shape[:2]
    x = np.clip(u * (width - 1), 0, width - 1)
    y = np.clip(v * (height - 1), 0, height - 1)
    x0, y0 = x.astype(np.int32), y.astype(np.int32)
    x1, y1 = np.minimum(x0 + 1, width - 1), np.minimum(y0 + 1, height - 1)
    fx, fy = x - x0, y - y0
    if values.ndim == 3:
        fx, fy = fx[..., None], fy[..., None]
    return ((values[y0, x0] * (1 - fx) + values[y0, x1] * fx) * (1 - fy)
            + (values[y1, x0] * (1 - fx) + values[y1, x1] * fx) * fy)


def _source_surface_maps(skin, size, source_mask):
    """Rasterize actual source UVs and rest positions into the new hand atlas."""
    positions = np.zeros((size, size, 3), np.float32)
    normals = np.zeros_like(positions)
    source_uvs = np.zeros((size, size, 2), np.float32)
    owner = np.zeros((size, size), np.int8)
    density = np.zeros((size, size, 2), np.float32)
    rigs = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or skin not in list(obj.data.materials):
            continue
        mesh = obj.data
        source_uv = mesh.uv_layers.get('SourceUV')
        atlas_uv = mesh.uv_layers.get('HandAtlas')
        if source_uv is None or atlas_uv is None:
            raise ValueError('Call configure_hand_material before removing SourceUV')
        side = 'R' if obj.name.startswith('Right') else 'L'
        ident = 1 if side == 'R' else 2
        rigs[ident] = (obj.parent, side)
        mesh.calc_loop_triangles()
        for tri in mesh.loop_triangles:
            uv = np.array([atlas_uv.data[i].uv[:] for i in tri.loops], np.float32)
            suv = np.array([source_uv.data[i].uv[:] for i in tri.loops], np.float32)
            points = np.array([mesh.vertices[i].co[:] for i in tri.vertices], np.float32)
            norms = np.array([mesh.vertices[i].normal[:] for i in tri.vertices], np.float32)
            low = np.maximum(0, np.floor(uv.min(axis=0) * size - .5).astype(int))
            high = np.minimum(size - 1, np.ceil(uv.max(axis=0) * size - .5).astype(int))
            if np.any(high < low):
                continue
            gridy, gridx = np.mgrid[low[1]:high[1] + 1, low[0]:high[0] + 1]
            samples = np.stack(((gridx + .5) / size, (gridy + .5) / size), axis=-1)
            e1, e2 = uv[1] - uv[0], uv[2] - uv[0]
            determinant = e1[0] * e2[1] - e1[1] * e2[0]
            if abs(determinant) < 1e-12:
                continue
            delta = samples - uv[0]
            b = (delta[..., 0] * e2[1] - delta[..., 1] * e2[0]) / determinant
            c = (e1[0] * delta[..., 1] - e1[1] * delta[..., 0]) / determinant
            a = 1 - b - c
            inside = (a >= -1e-5) & (b >= -1e-5) & (c >= -1e-5)
            yy, xx = gridy[inside], gridx[inside]
            bary = np.stack((a[inside], b[inside], c[inside]), axis=1)
            positions[yy, xx] = bary @ points
            normals[yy, xx] = bary @ norms
            source_uvs[yy, xx] = bary @ suv
            owner[yy, xx] = ident
            du = ((points[1] - points[0]) * e2[1] - (points[2] - points[0]) * e1[1]) / determinant
            dv = (-(points[1] - points[0]) * e2[0] + (points[2] - points[0]) * e1[0]) / determinant
            density[yy, xx] = (size / max(np.linalg.norm(du), .01),
                               size / max(np.linalg.norm(dv), .01))
    nails = _bilinear(source_mask, source_uvs[..., 0], source_uvs[..., 1])
    nails *= owner > 0
    return positions, normals, owner, density, nails, rigs


def _anatomical_surface_detail(positions, normals, owner, rigs):
    """Shallow skin folds placed from each real finger joint and wrist plane.

    This is explicit anatomy-guided sculpting, not a simulated skin solver.
    Depths are 0.035–0.08 mm in asset space, much smaller than hand silhouette.
    """
    height = np.zeros(owner.shape, np.float32)
    joint_tint = np.zeros(owner.shape, np.float32)
    for ident, (rig, side) in rigs.items():
        mask = owner == ident
        points = positions[mask]
        surface_normals = normals[mask]
        field = np.zeros(len(points), np.float32)
        tint = np.zeros(len(points), np.float32)
        dorsal = np.clip((surface_normals[:, 2] - .04) / .70, 0, 1)
        for digit in range(1, 6):
            for joint in (2, 3):
                bone = rig.data.bones[f'finger{digit}-{joint}.{side}']
                centre = np.array(bone.head_local[:], np.float32)
                axis = np.array((bone.tail_local - bone.head_local).normalized()[:], np.float32)
                lateral = np.cross(np.array([0, 0, 1], np.float32), axis)
                lateral /= max(np.linalg.norm(lateral), 1e-5)
                delta = points - centre
                along = delta @ axis
                across = delta @ lateral
                distance = np.linalg.norm(delta - along[:, None] * axis, axis=1)
                radius = .017 if digit < 5 else .013
                cross_gate = np.exp(-(across / (radius * .66)) ** 4)
                cross_gate *= np.exp(-(distance / (radius * 1.5)) ** 6)
                # Slightly bowed transverse folds break up the rounded plastic
                # phalanx highlight while leaving the natural skin hue intact.
                fold_axis = along + .0010 * (across / radius) ** 2
                for shift, depth, width in ((-.0019, .000035, .00095),
                                            (.0002, .000080, .00085)):
                    groove = np.exp(-((fold_axis - shift) / width) ** 2)
                    field -= groove * depth * cross_gate * dorsal
                tint += np.exp(-(along / .006) ** 2) * cross_gate * dorsal
        # Two broad wrist creases are palmar; a softer shallow dorsal fold is
        # enough to show carpal transition without drawing dark wrist bands.
        palmar = np.clip((-surface_normals[:, 2] - .08) / .65, 0, 1)
        span = np.exp(-(points[:, 0] / .031) ** 6)
        for centre, amount in ((-.005, .000070), (.005, .000045)):
            line = points[:, 1] - centre + .0013 * (points[:, 0] / .031) ** 2
            field -= np.exp(-(line / .00095) ** 2) * span * palmar * amount
        dorsal_line = points[:, 1] + .005 + .0009 * (points[:, 0] / .031) ** 2
        field -= np.exp(-(dorsal_line / .0011) ** 2) * span * dorsal * .000035
        height[mask] = field
        joint_tint[mask] = np.clip(tint, 0, 1)
    return height, joint_tint


def configure_hand_material(skin, root):
    """Create glTF-compatible maps from the already baked CC0 skin atlas.

    Photographed colour is combined with shallow bone-guided joint folds.
    The exact upstream MPFB source-UV nail mask provides nail placement.
    Normal and roughness maps are capped at 1K; colour keeps the 2K bake.
    """
    root = Path(root)
    nodes, links = skin.node_tree.nodes, skin.node_tree.links
    principled = nodes.get('Principled BSDF')
    colour_link = principled.inputs['Base Color'].links[0]
    texture = colour_link.from_node
    if texture.type != 'TEX_IMAGE':
        raise ValueError('Expected the baked skin atlas directly on Base Color')
    atlas = texture.image
    width, height = atlas.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    atlas.pixels.foreach_get(pixels)
    pixels = pixels.reshape(height, width, 4)
    rgb = pixels[:, :, :3]
    size = min(1024, width, height)
    yy, xx = np.mgrid[0:size, 0:size]
    small = _bilinear(rgb, (xx + .5) / size, (yy + .5) / size)
    luminance = small @ np.array([.2126, .7152, .0722], dtype=np.float32)
    mask = (luminance > .025).astype(np.float32)
    # Suppress island borders and black atlas background before taking slopes.
    border_radius = 3
    safe = (_blur(mask, border_radius) > .999).astype(np.float32)
    local = luminance - _blur(luminance, 2)
    local *= safe
    mask_path = root / 'assets/source/mage-hand-source-fingernails.jpg'
    mask_image = bpy.data.images.load(str(mask_path), check_existing=False)
    mask_image.colorspace_settings.name = 'Non-Color'
    mask_pixels = np.empty(mask_image.size[0] * mask_image.size[1] * 4, np.float32)
    mask_image.pixels.foreach_get(mask_pixels)
    source_mask = mask_pixels.reshape(mask_image.size[1], mask_image.size[0], 4)[:, :, 0]
    positions, normals, owner, density, nails, rigs = _source_surface_maps(skin, size, source_mask)
    bpy.data.images.remove(mask_image)
    fold_height, tint = _anatomical_surface_detail(positions, normals, owner, rigs)
    # The fixed source mask is the source of truth; a small filter antialiases
    # the existing nail borders, without inventing new nail extents.
    nails = np.clip(_blur(nails, 1), 0, 1)
    # Softer continuous highlights reveal the sculpt; source photographic
    # pigmentation is not a rough surface and must not become bump noise.
    roughness = np.clip(.49 + local * .14 - _blur(local, 5) * .12, .46, .53)
    roughness = roughness * (1 - nails) + .25 * nails
    rough_pixels = np.ones((size, size, 4), np.float32)
    rough_pixels[:, :, :3] = roughness[:, :, None]
    rough_image = _save_map('Mage skin roughness', rough_pixels,
                           root / 'assets/source/mage-hand-roughness.png')

    # Remove broad colour/shadow variation. Only the small local feature band
    # contributes, with bounded slopes to avoid treating pigmentation as bumps.
    # Object-space fold depths become tangent-space slopes using each source
    # triangle's real UV-to-metre density, not an arbitrary dark line texture.
    cuticle = np.clip(_blur(nails, 2) - nails, 0, 1)
    hdy, hdx = np.gradient(fold_height + nails * .00010 - cuticle * .000070)
    inside = (_blur((owner > 0).astype(np.float32), 1) > .999).astype(np.float32)
    slope_x = np.clip(hdx * density[:, :, 0], -.50, .50) * inside
    slope_y = np.clip(hdy * density[:, :, 1], -.50, .50) * inside
    normal = np.stack((-slope_x, -slope_y, np.ones_like(slope_x)), axis=2)
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    normal_pixels = np.ones((size, size, 4), np.float32)
    normal_pixels[:, :, :3] = normal * .5 + .5
    normal_image = _save_map('Mage skin subtle detail', normal_pixels,
                            root / 'assets/source/mage-hand-normal.png')

    # Very modest local colour contrast preserves the photographed source;
    # do not recolour skin as uniformly pink or orange to imitate warm lighting.
    full_y, full_x = np.mgrid[0:height, 0:width]
    full_u, full_v = (full_x + .5) / width, (full_y + .5) / height
    local_full = _bilinear(local, full_u, full_v)
    nails_full = _bilinear(nails, full_u, full_v)
    tint_full = _bilinear(tint, full_u, full_v)
    # Suppress oversized pigment speckle from magnifying a 2K full-body skin
    # onto a close-up hand; keep broad source colour and anatomy, not flat paint.
    valid_colour = (np.mean(rgb, axis=2) > .025).astype(np.float32)
    blurred_colour = _blur(rgb * valid_colour[:, :, None], 2)
    blurred_weight = _blur(valid_colour, 2)
    blurred_colour /= np.maximum(blurred_weight[:, :, None], 1e-6)
    rgb[:] = rgb * .38 + blurred_colour * .62
    rgb[:] = np.clip(rgb - (local_full * .18)[:, :, None], 0, 1)
    # The low-resolution full-body photo contains broad brown patches that
    # read as dirt when enlarged. Compress that colour variation gently while
    # retaining source skin hue and the finer photographed transitions.
    broad_weight = _blur(valid_colour, 10)
    broad_colour = _blur(rgb * valid_colour[:, :, None], 10)
    broad_colour /= np.maximum(broad_weight[:, :, None], 1e-6)
    median_skin = np.median(rgb[valid_colour > .5], axis=0)
    corrected_broad = median_skin + (broad_colour - median_skin) * .68
    rgb[:] += (corrected_broad - broad_colour) * valid_colour[:, :, None]
    # Subtle natural nail-body colour variation and warm joint skin; folds
    # themselves are shaded geometry detail, not painted black strokes.
    nail_tone = rgb * np.array([1.025, .995, 1.008], np.float32) + .016
    rgb[:] = rgb * (1 - nails_full[:, :, None] * .65) + nail_tone * nails_full[:, :, None] * .65
    rgb[:] *= 1 + tint_full[:, :, None] * np.array([.022, -.012, -.012], np.float32)
    rgb[:] = np.clip(rgb, 0, 1)
    atlas.pixels.foreach_set(pixels.ravel())
    atlas.update()
    atlas.save()
    atlas.pack()
    for image, socket in ((rough_image, 'Roughness'), (normal_image, 'Normal')):
        node = nodes.new('ShaderNodeTexImage')
        node.image = image
        if texture.inputs['Vector'].is_linked:
            links.new(texture.inputs['Vector'].links[0].from_socket, node.inputs['Vector'])
        if socket == 'Normal':
            normal_node = nodes.new('ShaderNodeNormalMap')
            normal_node.inputs['Strength'].default_value = 1.0
            links.new(node.outputs['Color'], normal_node.inputs['Color'])
            links.new(normal_node.outputs['Normal'], principled.inputs['Normal'])
        else:
            links.new(node.outputs['Color'], principled.inputs[socket])
    principled.inputs['Roughness'].default_value = .49
    principled.inputs['IOR'].default_value = 1.40
    # Opaque glTF PBR does not carry Blender's subsurface scattering. Use zero
    # here so offline comparisons do not promise skin scattering absent on web.
    principled.inputs['Subsurface Weight'].default_value = 0
    return {
        'atlas_size': [width, height],
        'detail_map_size': [size, size],
        'roughness_map': 'assets/source/mage-hand-roughness.png',
        'normal_map': 'assets/source/mage-hand-normal.png',
        'normal_source': 'Restrained anatomy-guided joint folds and exact source-UV nail bed; no albedo-derived bump or random pore noise.',
        'skin_scattering': 'No offline-only Blender SSS; exported opaque glTF PBR with continuous soft highlights.',
        'nail_mask_source': {
            'path': 'assets/source/mage-hand-source-fingernails.jpg',
            'upstream_path': 'src/mpfb/data/textures/mpfb_fingernails.jpg',
            'repository': 'https://github.com/makehumancommunity/mpfb2',
            'commit': '817587ceb2ea03ea17a5b47e04396cbb4ddfa2d5',
            'sha256': hashlib.sha256(mask_path.read_bytes()).hexdigest(),
            'license': 'CC0 1.0, upstream LICENSE.ASSETS.md',
            'placement': 'Barycentric SourceUV to HandAtlas remap; no inferred nail region',
        },
        'nail_mask_pixels_over_half': int(np.count_nonzero(nails > .5)),
        'new_random_noise': False,
        'nail_topology_and_source_uv_correspondence_retained': True,
        'nail_surface_adaptation': 'Source nail boundary receives shallow micro-sculpt; runtime UVs are repacked into HandAtlas.',
    }
