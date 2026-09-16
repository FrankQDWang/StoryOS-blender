import ROOM_LAYOUT from './room-layout.json' with { type: 'json' };

const EPSILON = 1e-9;

function obstacles(layout) {
  return [
    { center: layout.table.center, radius: layout.table.radius },
    ...layout.fixtures,
    ...layout.slots.map(({ position, yaw }) => ({
      center: [position[0], position[2]], halfSize: layout.lectern.halfSize, yaw,
    })),
  ];
}

// A circular body against the nearest point on a rectangle preserves clearance
// at its corners without blocking the extra space of a padded rectangular box.
function contact(point, obstacle) {
  const dx = point.x - obstacle.center[0], dz = point.z - obstacle.center[1];
  if (obstacle.radius !== undefined) {
    const distance = Math.hypot(dx, dz);
    return { distance: distance - obstacle.radius, nx: distance ? dx / distance : 1, nz: distance ? dz / distance : 0 };
  }
  const c = Math.cos(obstacle.yaw || 0), s = Math.sin(obstacle.yaw || 0);
  // Three.js rotation about +Y: world x = local x*cos + local z*sin.
  const x = c * dx - s * dz, z = s * dx + c * dz;
  const [hx, hz] = obstacle.halfSize;
  const px = x - Math.max(-hx, Math.min(hx, x));
  const pz = z - Math.max(-hz, Math.min(hz, z));
  const distance = Math.hypot(px, pz);
  let nx, nz;
  if (distance > 0) {
    nx = px / distance; nz = pz / distance;
  } else if (hx - Math.abs(x) < hz - Math.abs(z)) {
    nx = Math.sign(x) || 1; nz = 0;
  } else {
    nx = 0; nz = Math.sign(z) || 1;
  }
  return { distance, nx: c * nx + s * nz, nz: -s * nx + c * nz };
}

function insideBounds(point, layout) {
  const { room, navigation: { bodyRadius } } = layout;
  return Number.isFinite(point.x) && Number.isFinite(point.z)
    && point.x >= room.minX + bodyRadius - EPSILON && point.x <= room.maxX - bodyRadius + EPSILON
    && point.z >= room.minZ + bodyRadius - EPSILON && point.z <= room.maxZ - bodyRadius + EPSILON;
}

function clearOfFurniture(point, shapes, radius) {
  return shapes.every(shape => contact(point, shape).distance >= radius - EPSILON);
}

export function isWalkable(point, layout = ROOM_LAYOUT) {
  return insideBounds(point, layout) && clearOfFurniture(point, obstacles(layout), layout.navigation.bodyRadius);
}

/** Move a body on the floor by a displacement in metres, preserving its height elsewhere. */
export function moveWithCollisions(position, displacement, layout = ROOM_LAYOUT) {
  const current = { x: position.x, z: position.z };
  const radius = layout.navigation.bodyRadius, shapes = obstacles(layout);
  if (!insideBounds(current, layout) || !clearOfFurniture(current, shapes, radius)
    || !Number.isFinite(displacement.x) || !Number.isFinite(displacement.z)) return current;

  const { room } = layout;
  const bounded = point => ({
    x: Math.max(room.minX + radius, Math.min(room.maxX - radius, point.x)),
    z: Math.max(room.minZ + radius, Math.min(room.maxZ - radius, point.z)),
  });
  // Shorter than the body's radius, so even a long requested move cannot jump
  // across a thin piece of furniture between collision samples.
  const steps = Math.max(1, Math.ceil(Math.hypot(displacement.x, displacement.z) / Math.min(.05, radius / 4)));
  const delta = { x: displacement.x / steps, z: displacement.z / steps };
  for (let i = 0; i < steps; i++) {
    let next = bounded({ x: current.x + delta.x, z: current.z + delta.z });
    if (!clearOfFurniture(next, shapes, radius)) {
      let slide = { x: next.x - current.x, z: next.z - current.z };
      // Remove motion into each contact normal. This also slides along rotated
      // lecterns and round table edges, instead of favouring a world axis.
      for (let pass = 0; pass < 3 && !clearOfFurniture(next, shapes, radius); pass++) {
        for (const shape of shapes) {
          if (contact(next, shape).distance >= radius - EPSILON) continue;
          const { nx, nz } = contact(current, shape);
          const inward = slide.x * nx + slide.z * nz;
          if (inward < 0) { slide.x -= inward * nx; slide.z -= inward * nz; }
        }
        next = bounded({ x: current.x + slide.x, z: current.z + slide.z });
      }
    }
    if (clearOfFurniture(next, shapes, radius)) { current.x = next.x; current.z = next.z; }
  }
  return current;
}
