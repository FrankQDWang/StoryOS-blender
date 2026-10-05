import gzip,json,sys,xml.etree.ElementTree as E,datetime
from pathlib import Path
folder=Path(sys.argv[1]);window=json.loads((folder/'window.json').read_text());toc=E.parse(folder/'toc.xml');origin=datetime.datetime.fromisoformat(toc.find('.//start-date').text).timestamp()*1000
pid=next(p['id'] for p in json.loads((folder/'processes.json').read_text())['processInfo'] if p['type']=='GPU')
r=E.parse(gzip.open(folder/'gpu-intervals.xml.gz') if (folder/'gpu-intervals.xml.gz').exists() else folder/'gpu-intervals.xml').getroot();refs={e.attrib['id']:e for e in r.iter() if 'id' in e.attrib}
def element(e):return refs[e.attrib['ref']] if 'ref' in e.attrib else e
def value(e):e=element(e);return e.text or e.tag
a=(window['start']-origin)*1e6;b=(window['end']-origin)*1e6
intervals=[];rows=0
for row in r.findall('.//row'):
 c=list(row)
 if f'({pid})' not in element(c[10]).attrib.get('fmt','') or value(c[7])!='Active':continue
 start=int(value(c[0]));end=start+int(value(c[1]));start=max(a,start);end=min(b,end)
 if end>start:intervals.append((start,end));rows+=1
busy=0;end=-1
for start,stop in sorted(intervals):busy+=max(0,stop-max(start,end));end=max(end,stop)
frames=len(window['frames']);result={'scene':window['scene'],'pid':pid,'method':'Target Chrome GPU Active intervals union (Vertex/Fragment/Compute, overlap counted once), clipped to recorded wall-clock scenario window, divided by actual WebGL scene renders in that window; includes Chrome compositing. Not command-buffer frame labels, not WebGL timer queries.','seconds':(b-a)/1e9,'renderedFrames':frames,'fps':frames/((b-a)/1e9),'gpuActiveMs':busy/1e6,'gpuActiveMsPerRenderedFrame':busy/1e6/frames if frames else None,'gpuBusyPercent':busy/(b-a)*100,'matchedIntervals':rows}
(folder/'window-summary.json').write_text(json.dumps(result,indent=2));print(result)
