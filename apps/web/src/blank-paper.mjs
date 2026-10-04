import * as THREE from 'three';
let paper;
// Shared, unprinted paper. Grain is material detail; it contains no text or symbols.
export function blankPaper(){
 if(paper)return paper;
 const size=768,data=new Uint8Array(size*size*4);let seed=7143;
 for(let i=0;i<size*size;i++){
  seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  const grain=(seed>>>24)/255-.5,fibre=(i%size%17===0?-.45:0),value=Math.round(244+grain*7+fibre);
  data[i*4]=value;data[i*4+1]=value-3;data[i*4+2]=value-10;data[i*4+3]=255;
 }
 paper=new THREE.DataTexture(data,size,size);paper.colorSpace=THREE.SRGBColorSpace;
 paper.magFilter=THREE.LinearFilter;paper.minFilter=THREE.LinearMipmapLinearFilter;paper.generateMipmaps=true;paper.anisotropy=8;paper.needsUpdate=true;
 return paper;
}
