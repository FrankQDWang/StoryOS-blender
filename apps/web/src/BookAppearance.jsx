import {use,useEffect,useMemo} from 'react';
import {useTexture} from '@react-three/drei';
import * as THREE from 'three';
import {bookMaterial} from './book-materials.mjs';
import {paintCoverTitle,loadCoverTitleFont} from './cover-title.mjs';
import './cover-fonts.css';

function canvasTexture(canvas) {
  const texture=new THREE.CanvasTexture(canvas);
  texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=8;
  return texture;
}

export function useBookAppearance(book) {
  const style=bookMaterial(book);
  const fonts=loadCoverTitleFont(book.title,book.color??style.color);
  const [leather,paper]=useTexture(['/assets/textures/manuscript-soft-leather.webp','/assets/textures/manuscript-page-filled.webp']);
  use(fonts);
  const appearance=useMemo(()=>{
    leather.colorSpace=THREE.SRGBColorSpace;leather.anisotropy=8;paper.colorSpace=THREE.SRGBColorSpace;paper.anisotropy=8;
    const title=document.createElement('canvas');title.width=768;title.height=1024;
    const ink=title.getContext('2d');
    paintCoverTitle(ink,book.title,book.color??style.color);
    return {style,color:book.color??style.color,leather,back:paper,title:canvasTexture(title),page:paper};
  },[leather,paper,style,book.title,book.color]);
  useEffect(()=>{
    return()=>appearance.title.dispose();
  },[appearance]);
  return appearance;
}
