import sharp from 'sharp';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const source='assets/source/manuscript-soft/leather.png';
const output='public/assets/textures/manuscript-soft-leather.webp';
await sharp(source).resize(768,768).grayscale().linear(.9,110).webp({quality:86}).toFile(output);
const files=[];
for(const path of [source,output,'assets/source/manuscript-soft/prompt.txt','design/round-10-five-book-materials/warm-umber.png']){
 const bytes=await fs.readFile(path);files.push({path,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
}
await fs.writeFile('assets/source/manuscript-soft/provenance.json',JSON.stringify({tool:'built-in ImageGen',date:'2026-10-04',referenceRole:'Approved book material, correcting preview.1 stiffness',originalOutput:'/Users/frankqdwang/.codex/generated_images/01a10277-6227-7be3-8a41-42c814b07908/exec-1965fcf6-1cfc-452f-a70b-63bfedd84e20.png',processing:'768 square, neutralized grayscale at 0.9 contrast +110 for runtime tint; WebP quality 86',files},null,2)+'\n');
console.log(files);
