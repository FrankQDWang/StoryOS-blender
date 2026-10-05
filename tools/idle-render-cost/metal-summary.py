import gzip,json,sys,xml.etree.ElementTree as E,statistics,collections
from pathlib import Path
folder=Path(sys.argv[1]);pid=json.loads((folder/'processes.json').read_text())['processInfo'];pid=next(p['id'] for p in pid if p['type']=='GPU')
r=E.parse(gzip.open(folder/'gpu-intervals.xml.gz') if (folder/'gpu-intervals.xml.gz').exists() else folder/'gpu-intervals.xml').getroot();refs={e.attrib['id']:e for e in r.iter() if 'id' in e.attrib}
def el(e):return refs[e.attrib['ref']] if 'ref' in e.attrib else e
def val(e):e=el(e);return e.text or e.tag
def fmt(e):e=el(e);return e.attrib.get('fmt',val(e))
def union(items):
 total=0;end=-1
 for a,b in sorted(items):total+=max(0,b-max(a,end));end=max(end,b)
 return total
frames=collections.defaultdict(list);encoders=collections.defaultdict(list)
for row in r.findall('.//row'):
 c=list(row)
 if f'({pid})' not in fmt(c[10]) or val(c[7])!='Active':continue
 start=int(val(c[0]));duration=int(val(c[1]));frame=val(c[3]);frames[frame].append((start,start+duration));encoders[frame].append({'start':start,'duration':duration,'channel':val(c[2]),'label':fmt(c[6]),'buffer':val(c[15]),'encoder':val(c[16])})
rows=[{'frame':k,'gpuActiveUnionMs':union(v)/1e6,'spanMs':(max(b for a,b in v)-min(a for a,b in v))/1e6,'start':min(a for a,b in v),'encoders':len(encoders[k])} for k,v in frames.items()];rows.sort(key=lambda x:x['start']);steady=rows[3:-3]
result={'pid':pid,'method':'Metal System Trace, target Chrome GPU process only; per-frame union of Active Vertex/Fragment/Compute intervals (overlaps not double-counted), discard first/last 3 frames; includes browser compositing','frames':len(steady),'gpuActiveUnionMsMedian':statistics.median(x['gpuActiveUnionMs'] for x in steady),'frameSpanMsMedian':statistics.median(x['spanMs'] for x in steady),'rows':rows}
(folder/'summary.json').write_text(json.dumps(result,indent=2));(folder/'encoders.json').write_text(json.dumps(encoders));print({k:v for k,v in result.items() if k!='rows'});print(rows[10:15])
s=E.parse(gzip.open(folder/'submissions.xml.gz') if (folder/'submissions.xml.gz').exists() else folder/'submissions.xml').getroot();refs.update({e.attrib['id']+'_sub':e for e in []})
srefs={e.attrib['id']:e for e in s.iter() if 'id' in e.attrib}
def se(e):return srefs[e.attrib['ref']] if 'ref' in e.attrib else e
def sv(e):e=se(e);return e.text or e.tag
subs=[]
for row in s.findall('.//row'):
 c=list(row)
 if f'({pid})' not in se(c[7]).attrib.get('fmt',''):continue
 n=int(sv(c[5]));
 if n:subs.append({'start':int(sv(c[0])),'n':n,'buffer':sv(c[14])})
intervals=collections.defaultdict(list)
for vals in encoders.values():
 for e in vals:intervals[e['buffer']].append((e['start'],e['start']+e['duration']))
groups=[]
for i,sub in enumerate(subs):
 if i>=2 and [a['n'] for a in subs[i-2:i+1]]==[16,16,4]:
  active=[v for a in subs[i-2:i+1] for v in intervals[a['buffer']]]
  if active:groups.append({'start':subs[i-2]['start'],'gpuActiveUnionMs':union(active)/1e6,'spanMs':(max(b for a,b in active)-min(a for a,b in active))/1e6})
result2={'method':'Consecutive nonempty command-buffer pattern 16+16+4 encoders = one WebGL render plus browser compositor; active interval union for target GPU pid only. Pattern inference; verify group cadence against page RAF before treating as frame time.','groups':len(groups),'patternCounts':dict(collections.Counter(s['n'] for s in subs)),'durationSeconds':(subs[-1]['start']-subs[0]['start'])/1e9,'gpuActiveUnionMsMedian':statistics.median(g['gpuActiveUnionMs'] for g in groups) if groups else None,'rows':groups}
(folder/'grouped-summary.json').write_text(json.dumps(result2,indent=2));print({k:v for k,v in result2.items() if k!='rows'})
