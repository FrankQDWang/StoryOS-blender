import {BoxGeometry,Vector3} from 'three';

// Preserve the binding and contact perimeter; soften the leather over the board.
const geometries=new Map();
export function softCoverGeometry(front=true) {
  if(geometries.has(front))return geometries.get(front);
  const width=.78,height=.065,depth=1,radius=.027;
  const geometry=new BoxGeometry(width,height,depth,28,4,36);
  const position=geometry.attributes.position,normal=geometry.attributes.normal;
  const half=new Vector3(width/2,height/2,depth/2),inner=half.clone().addScalar(-radius);
  const p=new Vector3(),q=new Vector3(),n=new Vector3();
  const negativeInner=inner.clone().negate();
  const cushion=(x,z)=>{
    const u=x/half.x,v=z/half.z;
    const edge=Math.max(0,1-u*u*u*u)*Math.max(0,1-v*v*v*v);
    const bindingCrease=Math.exp(-Math.pow((x+.315)/.025,2))*.0018;
    return edge*(.006-bindingCrease+.0007*Math.sin(z*11+x*7));
  };
  for(let i=0;i<position.count;i++){
    p.fromBufferAttribute(position,i);q.copy(p).clamp(negativeInner,inner);
    n.copy(p).sub(q).normalize();p.copy(q).addScaledVector(n,radius);
    if(front&&n.y>0){
      const weight=n.y*n.y,step=.0001;
      const dx=(cushion(p.x+step,p.z)-cushion(p.x-step,p.z))/(2*step);
      const dz=(cushion(p.x,p.z+step)-cushion(p.x,p.z-step))/(2*step);
      p.y+=cushion(p.x,p.z)*weight;
      n.x-=dx*weight;n.z-=dz*weight;n.normalize();
    }
    position.setXYZ(i,p.x,p.y,p.z);normal.setXYZ(i,n.x,n.y,n.z);
  }
  if(front){
    const old=geometry.index.array,top=geometry.groups[2],indices=[];
    for(const group of geometry.groups)if(group!==top)for(let i=group.start;i<group.start+group.count;i++)indices.push(old[i]);
    const sides=indices.length;
    for(let i=top.start;i<top.start+top.count;i++)indices.push(old[i]);
    geometry.setIndex(indices);geometry.clearGroups();
    geometry.addGroup(0,sides,0);geometry.addGroup(sides,top.count,1);
  }
  geometry.computeBoundingBox();geometry.computeBoundingSphere();
  geometries.set(front,geometry);return geometry;
}
