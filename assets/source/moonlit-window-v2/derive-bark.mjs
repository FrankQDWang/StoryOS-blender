import sharp from '../../../tools/book-check/node_modules/sharp/dist/index.mjs';
await sharp('assets/source/moonlit-window/atlas.png').extract({left:768,top:256,width:256,height:768}).webp({lossless:true}).toFile('public/assets/textures/window-bark-v2.webp');
