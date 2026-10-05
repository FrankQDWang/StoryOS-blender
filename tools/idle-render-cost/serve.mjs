import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('.cache/idle-render-cost',process.argv[2]??'baseline');
http.createServer((req,res)=>{
 const file=path.join(root,decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\/+/, '')||'apps/web/index.html');
 const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.webp':'image/webp','.glb':'model/gltf-binary','.woff2':'font/woff2'};
 if(!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end();return}
 res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);
}).listen(Number(process.argv[3]??4190),'127.0.0.1');
