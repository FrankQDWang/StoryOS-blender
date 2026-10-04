import {useEffect,useMemo} from 'react';
import {useTexture} from '@react-three/drei';
import * as THREE from 'three';
import {bookMaterial} from './book-materials.mjs';
import {softCoverGeometry} from './soft-cover-geometry.mjs';

const surfaceGeometry=new WeakMap();
function mappedSurface(source) {
  if(surfaceGeometry.has(source))return surfaceGeometry.get(source);
  const geometry=source.clone();geometry.computeBoundingBox();
  const {min,max}=geometry.boundingBox,positions=geometry.attributes.position,normals=geometry.attributes.normal;
  const uv=new Float32Array(positions.count*2);
  for(let i=0;i<positions.count;i++){
    const x=positions.getX(i),y=positions.getY(i),z=positions.getZ(i);
    // Box projection keeps the same grain scale on broad leather faces and edges.
    const nx=Math.abs(normals.getX(i)),ny=Math.abs(normals.getY(i)),nz=Math.abs(normals.getZ(i));
    uv[i*2]=nx>ny&&nx>nz?(z-min.z)/(max.z-min.z):(x-min.x)/(max.x-min.x);
    uv[i*2+1]=ny>=nx&&ny>=nz?1-(z-min.z)/(max.z-min.z):(y-min.y)/(max.y-min.y);
  }
  geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));surfaceGeometry.set(source,geometry);return geometry;
}

function canvasTexture(canvas) {
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=8;
  return texture;
}

function textLines(ctx,text,x,y,maxWidth,lineHeight) {
  let line='';
  for(const character of text){
    if(ctx.measureText(line+character).width>maxWidth&&line){ctx.fillText(line,x,y);y+=lineHeight;line=''}
    line+=character;
  }
  ctx.fillText(line,x,y);
  return y;
}

export function useBookAppearance(book) {
  const [leather,paper]=useTexture(['/assets/textures/manuscript-soft-leather.webp','/assets/textures/manuscript-page.webp']);
  const style=bookMaterial(book);
  const appearance=useMemo(()=>{
    leather.colorSpace=THREE.SRGBColorSpace;leather.anisotropy=8;paper.colorSpace=THREE.SRGBColorSpace;paper.anisotropy=8;
    const title=document.createElement('canvas');title.width=768;title.height=1024;
    const ink=title.getContext('2d');ink.drawImage(leather.image,0,0,768,1024);
    ink.fillStyle='#302b26';ink.textAlign='center';ink.textBaseline='middle';
    const size=book.title.length>28?32:book.title.length>12?40:64;
    ink.font=`${size}px "Kaiti SC", "STKaiti", "KaiTi", serif`;
    ink.translate(384,0);ink.rotate(-.015);
    textLines(ink,book.title,0,230,640,size*1.3);
    let page=paper;
    if(book.description){
      const canvas=document.createElement('canvas');canvas.width=768;canvas.height=768;
      const content=canvas.getContext('2d');content.drawImage(paper.image,0,0,768,768);
      content.fillStyle=style.ink;content.textAlign='center';
      const descriptionSize=book.description.length>90?16:22;
      content.font=`${descriptionSize}px "Kaiti SC", "STKaiti", "KaiTi", serif`;
      textLines(content,book.description,384,345,590,descriptionSize*1.3);
      page=canvasTexture(canvas);
    }
    return {style,color:book.color??style.color,leather,back:paper,title:canvasTexture(title),page};
  },[leather,paper,style,book.title,book.description,book.color]);
  useEffect(()=>{
    appearance.title.needsUpdate=true;appearance.page.needsUpdate=true;
    return()=>{appearance.title.dispose();if(appearance.page!==paper)appearance.page.dispose()};
  },[appearance]);
  return appearance;
}

export function pageMaterial(appearance) {
  return {map:appearance.page,color:appearance.style.paper,roughness:.94,side:THREE.DoubleSide,
    customProgramCacheKey:()=> 'manuscript-page-v1',
    onBeforeCompile:shader=>{
      shader.uniforms.pageBack={value:appearance.back};
      shader.fragmentShader='uniform sampler2D pageBack;\n'+shader.fragmentShader.replace('#include <map_fragment>',
        THREE.ShaderChunk.map_fragment.replace('texture2D( map, vMapUv )','( gl_FrontFacing ? texture2D( map, vMapUv ) : texture2D( pageBack, vec2(1.0-vMapUv.x,vMapUv.y) ) )'));
    }};
}

export function applyBookAppearance(object,appearance) {
  const {style,leather}=appearance;
  object.traverse(mesh=>{
    if(!mesh.isMesh)return;
    if(/^Cover(Inlay|Corner|Seal|Star)/.test(mesh.name)){mesh.visible=false;return}
    const material=mesh.material;
    if(material.name==='BookLeather'||mesh.name.startsWith('SpineBand')){
      if(mesh.name==='FrontCover'||mesh.name==='BookBack')mesh.geometry=softCoverGeometry(mesh.name==='FrontCover');
      mesh.geometry=mappedSurface(mesh.geometry);
      material.color.set(appearance.color);material.map=leather;
      material.bumpMap=leather;material.bumpScale=style.grain;
      material.roughness=style.roughness;material.metalness=0;
      if(mesh.name==='FrontCover'){
        const face=material.clone();face.map=appearance.title;
        mesh.material=[material,face];
      }
      if(mesh.name.startsWith('SpineBand'))material.color.multiplyScalar(.84);
    }
    if(material.name==='BookPages'){
      material.color.set(style.paper);material.roughness=.94;
      if(mesh.name.startsWith('TurnPage')){mesh.geometry=mappedSurface(mesh.geometry);material.map=appearance.page}
    }
    if(mesh.name.startsWith('PageEdges')){material.color.set(style.paper).multiplyScalar(.72);material.metalness=0;material.roughness=1}
  });
  const front=object.getObjectByName('FrontCover');
  function surface(parent,width,height,position,rotation,material) {
    const mesh=new THREE.Mesh(new THREE.PlaneGeometry(width,height),new THREE.MeshStandardMaterial(material));
    mesh.position.set(...position);mesh.rotation.x=rotation;mesh.receiveShadow=true;
    mesh.userData.bookSurface=true;mesh.raycast=()=>null;parent.add(mesh);
  }
  // The title is part of the curved outer leather; pages contain no repeated title.
  surface(front,.70,.925,[0,-.0335,0],Math.PI/2,{map:appearance.back,color:style.paper,roughness:.94});
  surface(object,.70,.925,[0,.1635,0],-Math.PI/2,pageMaterial(appearance));
  return object;
}

export function disposeBook(object) {
  const materials=new Set();
  object.traverse(mesh=>{if(mesh.isMesh){for(const material of [].concat(mesh.material))materials.add(material);if(mesh.userData.bookSurface)mesh.geometry.dispose()}});
  for(const material of materials)material.dispose();
}
