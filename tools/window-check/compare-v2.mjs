import sharp from '../book-check/node_modules/sharp/dist/index.mjs';
import fs from'node:fs/promises';
const out='evidence/moonlit-window/revision-v2';await fs.mkdir(out,{recursive:true});
const paths=['design/round-12-moonlit-window/02-room-proposal.png','evidence/moonlit-window/final/overview.png',process.argv[2]??'evidence/moonlit-window/trials/v2-overview.png'];
const parts=await Promise.all(paths.map(async(path,i)=>({input:await sharp(await sharp(path).resize(1512,751).toBuffer()).extract({left:638,top:165,width:224,height:205}).resize(448,410).png().toBuffer(),left:i*448,top:0})));
await sharp({create:{width:1344,height:410,channels:3,background:'#222'}}).composite(parts).png().toFile(`${out}/reference-rejected-revision.png`);
