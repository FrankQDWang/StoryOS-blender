"""Check the shipped asset, its authored inputs and preserved room assets."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'assets/manifest.json').read_text())
for entry in manifest['assets']:
 p=ROOT/entry['path'];assert p.stat().st_size==entry['bytes'];assert sha(p)==entry['sha256'],p
source=json.loads((ROOT/'assets/source/makehuman-hands.json').read_text())
for entry in source['files']:
 p=ROOT/entry['path'];assert p.stat().st_size==entry['bytes'];assert sha(p)==entry['sha256'],p
assert sha(ROOT/'scripts/build_makehuman_hands.py')==source['generator_sha256']
robe=json.loads((ROOT/'assets/source/midnight-robe-provenance.json').read_text())
for entry in robe['textures']:assert sha(ROOT/entry['path'])==entry['sha256']
before=json.loads((ROOT/'downloads/soft-mage/baseline-preview5/assets/manifest.json').read_text())
kept=[]
for entry in before['assets']:
 if 'makehuman-hands' not in entry['path']:
  assert sha(ROOT/entry['path'])==entry['sha256'],entry['path'];kept.append(entry['path'])
products=[]
for p in (ROOT/'public').rglob('*'):
 if p.is_file():
  q=ROOT/'apps/web/dist/client'/p.relative_to(ROOT/'public')
  assert q.exists() and sha(q)==sha(p),q;products.append(str(p.relative_to(ROOT/'public')))
b=(ROOT/'public/assets/models/makehuman-hands.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);
morphs={m['name']:len(m['primitives'][0]['targets']) for m in g['meshes'] if m['primitives'][0].get('targets')}
assert sorted(morphs.values())==[5,5],morphs
result={'version':manifest['version'],'manifest_verified':len(manifest['assets']),'authored_files_verified':len(source['files']),'textures_verified':len(robe['textures']),'preserved_assets':kept,'production_files':products,'glb':{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'joints':[len(s['joints']) for s in g['skins']],'clips':len(g['animations']),'triangles':sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']),'morph_target_counts':morphs}}
(OUT/'asset-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
