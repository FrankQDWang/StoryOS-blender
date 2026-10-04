import {useEffect,useMemo} from 'react';
import {useTexture} from '@react-three/drei';
import * as THREE from 'three';
import {bookMaterial} from './book-materials.mjs';

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
  const [leather,paper]=useTexture(['/assets/textures/manuscript-soft-leather.webp','/assets/textures/manuscript-page-filled.webp']);
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
    return {style,color:book.color??style.color,leather,back:paper,title:canvasTexture(title),page:paper};
  },[leather,paper,style,book.title,book.color]);
  useEffect(()=>{
    return()=>appearance.title.dispose();
  },[appearance]);
  return appearance;
}
