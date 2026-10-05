import {build} from '../../apps/web/node_modules/vite/dist/node/index.js';
import react from '../../apps/web/node_modules/@vitejs/plugin-react/dist/index.js';
import path from 'node:path';
const root=process.cwd();
const label=process.argv[2]??'baseline';
await build({root,configFile:false,resolve:{alias:{react:path.join(root,'apps/web/node_modules/react')}},publicDir:path.join(root,'public'),plugins:[react(),{
 name:'measurement-only-probe',enforce:'pre',transformIndexHtml:{order:'pre',handler:html=>html.replace('/src/main.jsx','/apps/web/src/main.jsx')},transform(code,id){
  if(id.endsWith('/src/Scene.jsx'))return "import {Probe} from '../../../tools/idle-render-cost/Probe.jsx';\n"+code.replace("frameloop={visible&&!paused?'always':'demand'}","frameloop={window.__deterministic?'never':visible&&!paused?'always':'demand'}").replace('<Performance onMetrics={onMetrics}/>','<Performance onMetrics={onMetrics}/><Probe/>');
 }
}],build:{outDir:path.join(root,'.cache/idle-render-cost',label),emptyOutDir:true,rollupOptions:{input:{app:path.join(root,'apps/web/index.html'),deterministic:path.join(root,'tools/idle-render-cost/deterministic.html')}}}});
