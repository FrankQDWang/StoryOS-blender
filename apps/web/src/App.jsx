import React,{Component,useCallback,useEffect,useRef,useState} from 'react';
import {BookOpen,Books,Plus,ArrowUpRight,ArrowLeft,X,MagnifyingGlass,PersonSimpleWalk,SpeakerHigh,SpeakerSlash,Check,Feather,Moon,ArrowCounterClockwise,Eye,Pause} from '@phosphor-icons/react';
import {LibraryScene} from './Scene';
import {STORAGE_KEY,COLORS,initialLibrary,normalizeLibrary,createBook,visitBook,recentBooks} from './library-model.mjs';

class SceneBoundary extends Component {
 state={error:false};static getDerivedStateFromError(){return {error:true}};
 componentDidCatch(error){console.error('Library scene failed',error);this.props.onFail();}
 render(){return this.state.error?<div className="scene-unavailable"><Moon size={32}/><h2>藏书室暂时无法显示</h2><p>你仍可从作品列表继续写作。</p></div>:this.props.children}
}
function load(){try{const raw=localStorage.getItem(STORAGE_KEY);return raw?normalizeLibrary(JSON.parse(raw)):{...initialLibrary(),reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches}}catch{return initialLibrary()}}
function useAmbient(enabled){useEffect(()=>{
 if(!enabled)return;const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)return;
 const ctx=new Ctx();const gain=ctx.createGain();gain.gain.value=.012;gain.connect(ctx.destination);
 [98,146.83,196].forEach((hz,i)=>{const o=ctx.createOscillator();o.type='sine';o.frequency.value=hz;const g=ctx.createGain();g.gain.value=[.35,.15,.10][i];o.connect(g);g.connect(gain);o.start()});
 ctx.resume().catch(()=>{});return()=>ctx.close().catch(()=>{});
 },[enabled]);}
function Modal({title,children,onClose,wide=false}){
 const ref=useRef();useEffect(()=>{const prev=document.activeElement;ref.current?.focus();const key=e=>{
  if(e.key==='Escape'){e.preventDefault();e.stopImmediatePropagation();onClose()}
  if(e.key==='Tab'){const el=ref.current?.querySelectorAll('button:not(:disabled),input,textarea,[tabindex="0"]');if(!el?.length)return;const first=el[0],last=el[el.length-1];if(e.shiftKey && (document.activeElement===first||document.activeElement===ref.current)){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}
 };window.addEventListener('keydown',key,true);return()=>{window.removeEventListener('keydown',key,true);prev?.focus?.()}},[onClose]);
 return <div className="modal-shade" onMouseDown={e=>{if(e.target===e.currentTarget)onClose()}}><section ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={title} className={`modal ${wide?'wide':''}`}><button className="icon close" onClick={onClose} aria-label="关闭"><X size={20}/></button>{children}</section></div>;
}
export function App(){
 const [library,setLibrary]=useState(load),[mode,setMode]=useState('overview'),[lookLocked,setLookLocked]=useState(false),[selected,setSelected]=useState(null),[workspace,setWorkspace]=useState(null);
 const [panel,setPanel]=useState(null),[query,setQuery]=useState(''),[ready,setReady]=useState(false),[failed,setFailed]=useState(false),[opening,setOpening]=useState(false),[crafting,setCrafting]=useState(false),[appearing,setAppearing]=useState(null),[near,setNear]=useState(null),[resetToken,setResetToken]=useState(0),[toast,setToast]=useState(''),[metrics,setMetrics]=useState(null),[storageError,setStorageError]=useState(false);
 const [title,setTitle]=useState(''),[description,setDescription]=useState(''),[color,setColor]=useState(COLORS[3]);
 const timer=useRef(null),creationLock=useRef(false),openingLock=useRef(false),started=useRef(performance.now()),loadTime=useRef(null);
 const current=library.books.find(b=>b.id===selected),working=library.books.find(b=>b.id===workspace),recent=recentBooks(library),resume=library.books.find(b=>b.id===library.lastBookId)||recent[0];
 useAmbient(library.sound);
 useEffect(()=>{try{localStorage.setItem(STORAGE_KEY,JSON.stringify(library));setStorageError(false)}catch{setStorageError(true)}},[library]);
 useEffect(()=>()=>clearTimeout(timer.current),[]);
 useEffect(()=>{if(!toast)return;const t=setTimeout(()=>setToast(''),4500);return()=>clearTimeout(t)},[toast]);
 const sceneReady=useCallback(()=>{setReady(true);if(loadTime.current===null)loadTime.current=(performance.now()-started.current)/1000},[]);
 const enter=useCallback(id=>{if(!id)return;clearTimeout(timer.current);openingLock.current=false;setOpening(false);setPanel(null);setMode('overview');setWorkspace(id);setLibrary(s=>visitBook(s,id));document.exitPointerLock?.()},[]);
 const select=useCallback(id=>{if(openingLock.current||creationLock.current)return;setSelected(id);setMode('focus');setPanel(null);document.exitPointerLock?.()},[]);
 const beginOpen=useCallback(id=>{if(openingLock.current)return;openingLock.current=true;setSelected(id);setMode('focus');setPanel(null);document.exitPointerLock?.();
  if(library.reducedMotion||failed){enter(id);return}setOpening(true);timer.current=setTimeout(()=>enter(id),2600);
 },[library.reducedMotion,failed,enter]);
 const closePanel=useCallback(()=>setPanel(null),[]);
 const showCreate=useCallback(()=>{if(openingLock.current||creationLock.current)return;document.exitPointerLock?.();setMode('overview');setTitle('');setDescription('');setPanel('create')},[]);
 const returnRoom=()=>{setWorkspace(null);setMode('overview');setSelected(null);setResetToken(x=>x+1)};
 useEffect(()=>{const key=e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();if(!openingLock.current&&!creationLock.current){document.exitPointerLock?.();setMode('overview');setPanel('books')}return}
  if(['INPUT','TEXTAREA'].includes(document.activeElement?.tagName)||panel)return;
  if(e.code==='KeyE'&&mode==='roam'&&near)select(near);
  if(e.key==='Escape'&&!openingLock.current){setSelected(null);setMode('overview')}
 };window.addEventListener('keydown',key);return()=>window.removeEventListener('keydown',key)},[panel,mode,near,select]);
 const submit=e=>{e.preventDefault();if(creationLock.current||!title.trim())return;creationLock.current=true;
  const id=crypto.randomUUID();const next=createBook(library,{title,description,color},id);const b=next.books.at(-1);
  setLibrary(next);setPanel(null);setCrafting(b);setSelected(null);setMode('overview');
  const finish=()=>{setCrafting(false);creationLock.current=false;setAppearing(null);setToast(b.slot===null?'新书已创建，展示位已满，可从全部作品打开。':`《${b.title}》已放入藏书室`)};
  if(library.reducedMotion||failed)finish();else timer.current=setTimeout(finish,3100);
 };
 const allBooks=()=>{if(openingLock.current||creationLock.current)return;setQuery('');setPanel('books');document.exitPointerLock?.();setMode('overview')};
 return <main className={workspace?'app workspace-app':'app'}>
  {!workspace&&<div className="scene"><SceneBoundary onFail={()=>{setFailed(true);setReady(true)}}><LibraryScene books={library.books} selected={selected} mode={mode} setMode={setMode} onSelect={select} onCreate={showCreate} onReady={sceneReady} onNear={setNear} onMetrics={setMetrics} opening={opening} crafting={crafting} appearing={appearing} reduced={library.reducedMotion} resetToken={resetToken} paused={Boolean(panel)} onLockChange={setLookLocked}/></SceneBoundary></div>}
  {!workspace&&!ready&&!failed&&<div className="loading"><BookOpen size={34} weight="thin"/><p>点亮你的藏书室</p><span>正在准备空间与书本…</span><button className="secondary" onClick={allBooks}>先从作品列表进入</button></div>}
  <header className="topbar"><a className="brand" href="#" onClick={e=>{e.preventDefault();workspace?returnRoom():(setMode('overview'),setSelected(null),setResetToken(x=>x+1))}} aria-label="StoryOS 藏书室"><BookOpen size={27} weight="thin"/><span>StoryOS</span><i/></a><div className="top-location"><span>{workspace?'写作空间':'私人藏书室'}</span><span className="demo-tag">体验样片</span></div><nav>
   {!workspace&&<><button className="icon quiet-option" title={library.sound?'关闭环境音':'开启环境音'} aria-label={library.sound?'关闭环境音':'开启环境音'} onClick={()=>setLibrary(s=>({...s,sound:!s.sound}))}>{library.sound?<SpeakerHigh size={20}/>:<SpeakerSlash size={20}/>}</button><button className={`icon quiet-option ${library.reducedMotion?'active':''}`} title="减少动态效果" aria-label="减少动态效果" aria-pressed={library.reducedMotion} onClick={()=>setLibrary(s=>({...s,reducedMotion:!s.reducedMotion}))}><Pause size={19}/></button></>}
   <button className="top-books" onClick={allBooks}><Books size={18}/>全部作品<span>{library.books.length}</span></button>
  </nav></header>
  {workspace&&working?<section className="workspace"><button className="back-link" onClick={returnRoom}><ArrowLeft size={18}/>返回藏书室</button><div className="workspace-kicker">STORYOS / WRITING ROOM</div><h1>{working.title}</h1><p className="workspace-description">{working.description||'一个新的世界，正在等待你的第一句话。'}</p><div className="workspace-rule"/><div className="placeholder-note"><Feather size={25} weight="thin"/><div><h2>故事，从这里继续。</h2><p>你已进入《{working.title}》的工作区。</p><p>这是入口体验的占位页面，正式编辑器将在后续接入。</p></div></div><button className="light-button" onClick={returnRoom}>回到我的藏书室 <ArrowUpRight size={17}/></button></section>:!workspace&&<>
   {ready&&!opening&&mode!=='roam'&&<div className="room-caption"><span>THE WRITER’S ROOM</span><h1>我的藏书室</h1><p>每一本书，都是你创造的世界。</p></div>}
   {ready&&!failed&&mode==='overview'&&!opening&&!crafting&&<button className="magic-hint" onClick={showCreate}><Plus size={15}/>写下一个新世界</button>}
   {ready&&!opening&&mode==='focus'&&current&&<section className="focus-card"><button className="icon card-close" aria-label="返回房间全景" onClick={()=>{setMode('overview');setSelected(null)}}><X size={17}/></button><span className="eyebrow">你的作品 / {String((current.slot??0)+1).padStart(2,'0')}</span><h2>{current.title}</h2><p>{current.description||'故事的第一句话，正等你落笔。'}</p><div className="book-meta">{current.words.toLocaleString()} 字 <span>·</span> 本地体验作品</div><button className="primary" onClick={()=>beginOpen(current.id)}>打开这本书 <ArrowUpRight size={18}/></button></section>}
   {mode==='roam'&&<><div className="crosshair"/><div className="roam-help">W A S D 移动 · {lookLocked?'鼠标环顾':'按住鼠标拖拽环顾'} · Esc 退出<button onClick={()=>setMode('overview')}>返回全景</button>{near&&<button onClick={()=>select(near)}>按 E 查看《{library.books.find(b=>b.id===near)?.title}》</button>}</div></>}
   {opening&&<div className="cinema-caption"><span>正在翻开</span><h2>{current?.title}</h2><button onClick={()=>enter(selected)}>跳过动画 <ArrowUpRight size={15}/></button></div>}
   {crafting&&<div className="cinema-caption"><span>纸页相遇，世界诞生</span><h2>{crafting.title}</h2></div>}
   {!opening&&!crafting&&mode!=='roam'&&<footer className="bottom-bar"><div className="continue-wrap">{resume?<button className="continue-card" onClick={()=>enter(resume.id)}><span className="continue-icon"><Feather size={24} weight="thin"/></span><span><small>继续最近的写作</small><strong>{resume.title}</strong></span><ArrowUpRight size={20}/></button>:<button className="continue-card" onClick={showCreate}>创建你的第一本书</button>}</div><div className="bottom-center"><span className="tiny-dot"/>{failed?'从作品列表继续写作':'点选书本，翻开你的世界'}</div><div className="bottom-actions"><button id="roam-button" disabled={!ready||failed} className="secondary" onClick={()=>{setSelected(null);setMode('roam')}}><PersonSimpleWalk size={17}/>自由漫游</button><button className="primary create-button" onClick={showCreate}><Plus size={17}/>新建作品</button></div></footer>}
  </>}
  {storageError&&<div className="storage-warning" role="alert">浏览器未允许本地保存，本次修改刷新后可能丢失。</div>}
  {toast&&<div className="toast" role="status"><Check size={17}/>{toast}</div>}
  {panel==='books'&&<Modal title="全部作品" onClose={closePanel} wide><span className="eyebrow">YOUR WORLDS</span><h2>全部作品 <em>{library.books.length}</em></h2><p className="modal-subtitle">随时回到你正在书写的世界。</p><label className="search"><MagnifyingGlass size={20}/><input autoFocus value={query} onChange={e=>setQuery(e.target.value)} placeholder="搜索书名" aria-label="搜索书名"/><kbd>⌘ K</kbd></label><div className="book-list">{recent.filter(b=>b.title.toLowerCase().includes(query.toLowerCase())).map(b=><button className="book-row" key={b.id} onClick={()=>enter(b.id)}><span className="row-icon" style={{color:b.color}}><BookOpen size={29} weight="duotone"/></span><span><strong>{b.title}</strong><small>{b.words.toLocaleString()} 字 · {b.slot===null?'在作品列表中':`展示位 ${b.slot+1}`}</small></span><ArrowUpRight size={18}/></button>)}{!recent.some(b=>b.title.toLowerCase().includes(query.toLowerCase()))&&<p className="empty">没有找到这本书。换个书名试试。</p>}</div><button className="new-row" onClick={showCreate}><Plus size={18}/>创建新作品</button><p className="local-note">体验数据仅保存在当前浏览器</p></Modal>}
  {panel==='create'&&<Modal title="创建新作品" onClose={closePanel}><span className="eyebrow">A WORLD OF YOUR OWN</span><h2>让一个世界诞生</h2><p className="modal-subtitle">先为它取个名字，故事可以慢慢写。</p><form onSubmit={submit}><label className="field">书名<input autoFocus required maxLength={60} value={title} onChange={e=>setTitle(e.target.value)} placeholder="这个世界，叫什么名字？"/></label><label className="field">一句话介绍 <small>选填</small><textarea maxLength={180} value={description} onChange={e=>setDescription(e.target.value)} placeholder="记下此刻的灵感…" rows={2}/></label><fieldset className="colors"><legend>封面颜色</legend>{COLORS.map((c,i)=><button key={c} type="button" className={c===color?'chosen':''} style={{background:c}} aria-label={`封面颜色 ${['松绿','陶棕','靛蓝','烟紫','麦金'][i]}`} aria-pressed={c===color} onClick={()=>setColor(c)}>{c===color&&<Check size={16}/>}</button>)}</fieldset>{library.books.filter(b=>b.slot!==null).length>=5&&<p className="capacity-note">五个展示位已满，新作品会保存在「全部作品」中。</p>}<button type="submit" disabled={!title.trim()} className="primary submit">创造这本书 <Feather size={18}/></button></form></Modal>}
  {import.meta.env.DEV&&<output className="perf" title="本地渲染统计">{metrics?`${metrics.fps} FPS`:'加载中'}{loadTime.current?` · ${loadTime.current.toFixed(1)}s`:''}</output>}
 </main>;
}
