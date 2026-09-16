import test from 'node:test';
import assert from 'node:assert/strict';
import ROOM_LAYOUT from '../src/room-layout.json' with { type: 'json' };
import { isWalkable, moveWithCollisions, readingApproach } from '../src/roaming.mjs';

const EPSILON = 1e-7;
const distance = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
const rotated = ({ x, z }, yaw = 0) => ({ x: x * Math.cos(yaw) + z * Math.sin(yaw), z: -x * Math.sin(yaw) + z * Math.cos(yaw) });
const emptyRoom = () => ({ ...ROOM_LAYOUT, room: { minX: -20, maxX: 20, minZ: -20, maxZ: 20 }, table: { center: [50, 50], radius: .92 }, fixtures: [], slots: [] });

test('body clearance applies to walls and round table; long displacement cannot cross the table', () => {
  const { table, navigation: { bodyRadius } } = ROOM_LAYOUT;
  const edge = table.center[1] + table.radius + bodyRadius;
  assert.equal(isWalkable({ x: table.center[0], z: edge - .01 }), false);
  assert.equal(isWalkable({ x: table.center[0], z: edge + .01 }), true);
  const stopped = moveWithCollisions({ x: 0, z: 4 }, { x: 0, z: -12 });
  assert.ok(stopped.z >= edge - EPSILON && stopped.z < edge + .05);
  assert.equal(isWalkable(stopped), true);
  const layout = emptyRoom();
  assert.deepEqual(moveWithCollisions({ x: 0, z: 0 }, { x: 100, z: 100 }, layout), { x: 19.75, z: 19.75 });
  assert.equal(isWalkable({ x: 19.8, z: 0 }, layout), false);
});

test('every fixture and all five rotated lecterns stop movement before the body enters them', () => {
  const shapes = [
    ...ROOM_LAYOUT.fixtures,
    ...ROOM_LAYOUT.slots.map((slot, i) => ({ id: `lectern ${i}`, center: [slot.position[0], slot.position[2]], halfSize: ROOM_LAYOUT.lectern.halfSize, yaw: slot.yaw })),
  ];
  for (const shape of shapes) {
    const layout = { ...emptyRoom(), fixtures: [shape] };
    const padding = shape.halfSize[1] + layout.navigation.bodyRadius;
    const offset = rotated({ x: 0, z: padding + .6 }, shape.yaw);
    const start = { x: shape.center[0] + offset.x, z: shape.center[1] + offset.z };
    const delta = rotated({ x: 0, z: -2 * (padding + 1) }, shape.yaw);
    const end = moveWithCollisions(start, delta, layout);
    const local = rotated({ x: end.x - shape.center[0], z: end.z - shape.center[1] }, -(shape.yaw || 0));
    assert.ok(local.z >= padding - EPSILON, `${shape.id}: crossed the front face`);
    assert.ok(local.z < padding + .05, `${shape.id}: stopped too early`);
    assert.equal(isWalkable(end, layout), true, shape.id);
    assert.equal(isWalkable({ x: shape.center[0], z: shape.center[1] }, layout), false, shape.id);
  }
});

test('rectangle corners use circular body clearance and diagonal movement slides along a rotated face', () => {
  const yaw = Math.PI / 4;
  const layout = { ...emptyRoom(), fixtures: [{ center: [0, 0], halfSize: [2, .5], yaw }] };
  assert.equal(isWalkable(rotated({ x: 2.2, z: .7 }, yaw), layout), true);
  assert.equal(isWalkable(rotated({ x: 2.17, z: .67 }, yaw), layout), false);
  const start = rotated({ x: -.5, z: .79 }, yaw);
  const end = moveWithCollisions(start, rotated({ x: 1, z: -1 }, yaw), layout);
  const local = rotated(end, -yaw);
  assert.ok(local.x > .49, 'tangential movement must continue after contact');
  assert.ok(local.z >= .75 - EPSILON && local.z < .80);
  assert.equal(isWalkable(end, layout), true);
});

test('zero displacement is stable and invalid starting positions are not teleported through furniture', () => {
  const home = { x: ROOM_LAYOUT.home.position[0], z: ROOM_LAYOUT.home.position[2] };
  assert.deepEqual(moveWithCollisions(home, { x: 0, z: 0 }), home);
  const insideTable = { x: ROOM_LAYOUT.table.center[0], z: ROOM_LAYOUT.table.center[1] };
  assert.deepEqual(moveWithCollisions(insideTable, { x: 5, z: 0 }), insideTable);
});

// Planning exists only in this test: every accepted grid edge is executed by
// the same movement function used by the camera, rather than by point checks.
function reachableFloor(step = .15) {
  const origin = { x: ROOM_LAYOUT.home.position[0], z: ROOM_LAYOUT.home.position[2] };
  const key = (x, z) => `${x},${z}`;
  const start = { ix: 0, iz: 0, point: origin, previous: null };
  const nodes = new Map([[key(0, 0), start]]), queue = [start];
  for (let i = 0; i < queue.length; i++) {
    const current = queue[i];
    for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const ix = current.ix + dx, iz = current.iz + dz, id = key(ix, iz);
      if (nodes.has(id)) continue;
      const target = { x: origin.x + ix * step, z: origin.z + iz * step };
      if (!isWalkable(target)) continue;
      const end = moveWithCollisions(current.point, { x: target.x - current.point.x, z: target.z - current.point.z });
      if (distance(end, target) > EPSILON) continue;
      const next = { ix, iz, point: target, previous: current };
      nodes.set(id, next); queue.push(next);
    }
  }
  return queue;
}

test('all five reading stands have reachable standing positions within book interaction distance', t => {
  const nodes = reachableFloor();
  assert.ok(nodes.length > 1000, 'the usable floor must be a connected open room');
  for (const [index, slot] of ROOM_LAYOUT.slots.entries()) {
    const target = readingApproach(slot);
    assert.ok(target, 'a reading position must exist in the front half of each stand');
    assert.equal(isWalkable(target), true, `lectern ${index}: standing space is blocked`);
    const nearest = nodes.reduce((best, next) => distance(next.point, target) < distance(best.point, target) ? next : best);
    assert.ok(distance(nearest.point, target) < .22, `lectern ${index}: no connected route`);
    const end = moveWithCollisions(nearest.point, { x: target.x - nearest.point.x, z: target.z - nearest.point.z });
    assert.ok(distance(end, target) < EPSILON, `lectern ${index}: cannot finish approach`);
    const bookDistance = Math.hypot(end.x - slot.position[0], end.z - slot.position[2], ROOM_LAYOUT.navigation.eyeHeight - slot.position[1]);
    assert.ok(bookDistance < 1.9, `lectern ${index}: cannot trigger nearby book`);
    let current = nearest, length = 0;
    while (current.previous) { length += distance(current.point, current.previous.point); current = current.previous; }
    t.diagnostic(`lectern ${index + 1}: verified route ${length.toFixed(2)} m; final book distance ${bookDistance.toFixed(2)} m`);
  }
});

test('the central table has a complete unobstructed walking circuit connected to the entrance', () => {
  const { center, radius } = ROOM_LAYOUT.table;
  const routeRadius = radius + ROOM_LAYOUT.navigation.bodyRadius + .3;
  let position = { x: center[0], z: center[1] + routeRadius };
  const home = { x: ROOM_LAYOUT.home.position[0], z: ROOM_LAYOUT.home.position[2] };
  const approached = moveWithCollisions(home, { x: position.x - home.x, z: position.z - home.z });
  assert.ok(distance(approached, position) < EPSILON, 'circuit must connect to the entrance');
  const start = position;
  for (let i = 1; i <= 144; i++) {
    const angle = i * Math.PI * 2 / 144;
    const target = { x: center[0] + Math.sin(angle) * routeRadius, z: center[1] + Math.cos(angle) * routeRadius };
    position = moveWithCollisions(position, { x: target.x - position.x, z: target.z - position.z });
    assert.ok(distance(position, target) < EPSILON, `table circuit blocked at segment ${i}`);
    assert.equal(isWalkable(position), true);
  }
  assert.ok(distance(position, start) < EPSILON, 'circuit must close');
});
