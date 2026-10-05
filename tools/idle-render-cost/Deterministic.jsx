import React from 'react';
import {createRoot} from '../../apps/web/node_modules/react-dom/client';
import {LibraryScene} from '../../apps/web/src/Scene';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
import '../../apps/web/src/styles.css';
window.__deterministic=true;
const noop=()=>{},root=createRoot(document.getElementById('root'));
const all=fiveBookPreview(initialLibrary()).books;
window.renderCase=(options={})=>{
 const {view='overview',opening=false,crafting=false,deleted=false}=options;
 const cameras={window:{position:[.2,1.65,-2.8],target:[0,2.3,-4.8],fov:53},shadow:{position:[-1.7,1.7,1.5],target:[-3,.3,-1],fov:53},book:{position:[-2.25,2.4,2.25],target:[-3,1.1,.6],fov:53}};
 window.__caseReady=false;
 root.render(<main className="app"><div className="scene"><LibraryScene key={options.persistent?'persistent':JSON.stringify(options)} books={deleted?all.slice(0,4):all} selected={opening?all[0].id:null} mode={opening?'focus':'overview'} setMode={noop} onSelect={noop} onCreate={noop} onReady={()=>window.__caseReady=true} onNear={noop} onMetrics={noop} opening={opening} crafting={crafting?all[4]:null} appearing={null} reduced={false} resetToken={0} paused={true} onLockChange={noop} inspection={{time:options.time??0,camera:cameras[view]}}/></div></main>);
};
window.renderCase();
