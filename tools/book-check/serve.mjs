import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve(process.argv[2]);
const injection=process.argv[4]?await fs.readFile(process.argv[4],'utf8'):null;
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.glb':'model/gltf-binary','.png':'image/png','.webp':'image/webp','.woff2':'font/woff2','.woff':'font/woff'};
http.createServer(async(req,res)=>{
  const url=new URL(req.url,'http://localhost');
  let file=path.join(root,decodeURIComponent(url.pathname));
  if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return}
  if(url.pathname.endsWith('/'))file=path.join(file,'index.html');
  try{let data=await fs.readFile(file);if(injection&&file.endsWith('.html'))data=Buffer.from(data.toString().replace('<head>',`<head><script>${injection}</script>`));res.writeHead(200,{'Content-Type':types[path.extname(file)]??'application/octet-stream','Cache-Control':file.endsWith('.html')?'no-cache':'public, max-age=3600'});res.end(data)}
  catch{res.writeHead(404);res.end('Not found')}
}).listen(Number(process.argv[3]),'127.0.0.1',()=>console.log(`Serving ${root} on ${process.argv[3]}`));
