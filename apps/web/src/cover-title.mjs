import {Color} from 'three';

// The two approved references apply to typography, never to the book geometry.
export function coverTitleStyle(color) {
  const {r,g,b}=new Color(color);
  // Calibrated to the user's existing dark green/blue and light brown covers.
  const dark=.2126*r+.7152*g+.0722*b<.095;
  return dark
    ? {dark,ink:'#b9b2a2',font:'"Cover Hand Latin", "Cover Brush"',weight:400,align:'center',x:.51,top:.27,width:.70,height:.40,size:112,leading:1.28}
    : {dark,ink:'#16120f',font:'"Cover Serif Latin", "Cover Serif CN"',weight:500,align:'left',x:.19,top:.16,width:.66,height:.40,size:88,leading:1.22};
}

const fontLoads=new Map();
export function loadCoverTitleFont(title,color) {
  const style=coverTitleStyle(color),font=`${style.weight} 32px ${style.font}`;
  const text=[...new Set(title)].sort().join(''),key=font+text;
  if(!fontLoads.has(key))fontLoads.set(key,document.fonts.load(font,text));
  return fontLoads.get(key);
}

const segmenter=new Intl.Segmenter(undefined,{granularity:'word'});
function titleTokens(text) {
  const tokens=[];
  for(const {segment} of segmenter.segment(text.trim())){
    // Closing punctuation stays attached to the preceding word/character.
    if(/^[，。！？、：；）》】,.!?:;)]$/.test(segment)&&tokens.length)tokens[tokens.length-1]+=segment;
    else tokens.push(segment);
  }
  return tokens;
}

function balancedLines(ctx,tokens,maxWidth) {
  const costs=Array(tokens.length+1).fill(Infinity),lines=Array(tokens.length+1);
  costs[tokens.length]=0;lines[tokens.length]=[];
  for(let start=tokens.length-1;start>=0;start--){
    let text='';
    for(let end=start;end<tokens.length;end++){
      text+=tokens[end];const line=text.trim(),width=ctx.measureText(line).width;
      if(width>maxWidth)break;
      if(!line)continue;
      const cost=(maxWidth-width)**2+costs[end+1];
      if(cost<costs[start]){costs[start]=cost;lines[start]=[line,...lines[end+1]]}
    }
  }
  return lines[0];
}

export function layoutCoverTitle(ctx,text,style,width=768,height=1024) {
  const tokens=titleTokens(text),maxWidth=style.width*width,maxHeight=style.height*height;
  const tracking=style.dark&&/^[\p{Script=Han}\p{P}\s]+$/u.test(text)?.05:0;
  for(let size=style.size;size>=24;size-=2){
    ctx.font=`${style.weight} ${size}px ${style.font}`;
    ctx.letterSpacing=`${size*tracking}px`;
    // Only words wider than the entire area at the minimum size may split.
    const lines=balancedLines(ctx,tokens,maxWidth);
    if(lines&&(lines.length-1)*size*style.leading+size<=maxHeight)
      return {lines,size,lineHeight:size*style.leading,x:style.x*width,y:style.top*height,maxWidth};
  }
  // A single unusually long identifier (up to the existing 60-character limit).
  const size=24;ctx.font=`${style.weight} ${size}px ${style.font}`;ctx.letterSpacing=`${size*tracking}px`;
  const splittable=tokens.flatMap(token=>ctx.measureText(token).width>maxWidth?Array.from(token):[token]);
  return {lines:balancedLines(ctx,splittable,maxWidth)??[text],size,lineHeight:size*style.leading,x:style.x*width,y:style.top*height,maxWidth};
}

export function paintCoverTitle(ctx,text,color) {
  const {width,height}=ctx.canvas,style=coverTitleStyle(color);
  const layout=layoutCoverTitle(ctx,text,style,width,height);
  ctx.fillStyle=style.ink;ctx.textAlign=style.align;ctx.textBaseline='top';
  for(const [index,line] of layout.lines.entries())ctx.fillText(line,layout.x,layout.y+index*layout.lineHeight);
  return {...layout,style};
}

// Reuse the existing leather/bump texture for the base, and the existing title
// texture for pigment + coverage. Both receive the same standard scene lighting.
export function applyCoverTitleMaterial(material) {
  material.onBeforeCompile=shader=>{
    shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`
      vec4 titlePigment = texture2D(map, vMapUv);
      vec3 leatherColor = texture2D(bumpMap, vBumpMapUv).rgb * diffuseColor.rgb;
      diffuseColor.rgb = mix(leatherColor, titlePigment.rgb, titlePigment.a);
    `);
  };
  material.customProgramCacheKey=()=> 'cover-title-pigment-v1';
}
