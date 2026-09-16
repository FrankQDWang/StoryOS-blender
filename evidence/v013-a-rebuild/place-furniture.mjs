import * as THREE from '../../apps/web/node_modules/three/build/three.module.js';
import fs from 'node:fs';
const report=JSON.parse(fs.readFileSync('evidence/v013-a-rebuild/camera-fit.json'));
const c=new THREE.PerspectiveCamera(report.fov,1849/851,.06,60);c.position.fromArray(report.position);c.lookAt(...report.lookAt);c.updateMatrixWorld();
const ray=new THREE.Raycaster(),plane=new THREE.Plane(new THREE.Vector3(0,1,0),-.15);
for(const [name,x,y] of [['left front',180,667],['left rear',541,536],['right rear',1340,567],['right mid',1510,620],['right front',1655,752]]){
 ray.setFromCamera(new THREE.Vector2(x/1849*2-1,1-y/851*2),c);
 const v=new THREE.Vector3();ray.ray.intersectPlane(plane,v);
 let top=v.clone();top.y=1.18;top.project(c);
 console.log(name,v.toArray(),[1849*(top.x+1)/2,851*(1-top.y)/2]);
}
