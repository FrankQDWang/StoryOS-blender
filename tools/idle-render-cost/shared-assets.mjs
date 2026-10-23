// Use identical static files and one server process for a loading comparison.
import fs from 'node:fs';
import path from 'node:path';
const [baseline,candidate,label]=process.argv.slice(2);
const cache=path.resolve('.cache/idle-render-cost'),root=path.join(cache,label);
function overlay(from,to){
 fs.mkdirSync(to,{recursive:true});
 for(const entry of fs.readdirSync(from,{withFileTypes:true})){
  const source=path.join(from,entry.name),target=path.join(to,entry.name);
  if(entry.isDirectory())overlay(source,target);
  else if(fs.existsSync(target)){
   if(!fs.readFileSync(source).equals(fs.readFileSync(target)))throw new Error(`Different shared asset: ${entry.name}; use separate full builds`);
  }else fs.symlinkSync(source,target);
 }
}
for(const build of [baseline,candidate])overlay(path.join(cache,build,'assets'),path.join(root,'assets'));
for(const [version,build] of [['baseline',baseline],['candidate',candidate]])fs.copyFileSync(path.join(cache,build,'apps/web/index.html'),path.join(root,`${version}.html`));
