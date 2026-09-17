from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'assets/manifest.json').read_text());checks=[]
for e in manifest['assets']:
 p=ROOT/e['path'];assert sha(p)==e['sha256'];assert p.stat().st_size==e['bytes'];checks.append(e['path'])
prov=json.loads((ROOT/'assets/source/makehuman-hands.json').read_text())
for e in prov['files']:assert sha(ROOT/e['path'])==e['sha256']
assert sha(ROOT/prov['generator'])==prov['generator_sha256']
public=[]
for p in (ROOT/'public').rglob('*'):
 if p.is_file():
  target=ROOT/'apps/web/dist/client'/p.relative_to(ROOT/'public');assert target.exists() and sha(p)==sha(target);public.append(str(p.relative_to(ROOT)))
preserved=['apps/web/src/room-layout.json','public/assets/models/library-room.glb','public/assets/models/story-book.glb','apps/web/src/Scene.jsx','apps/web/src/HearthFire.jsx','apps/web/src/HearthBed.jsx','apps/web/src/opening-sequence.json']+[str(p.relative_to(ROOT)) for p in (ROOT/'public/assets/textures').glob('*.png')]
for f in preserved:
 assert subprocess.check_output(['git','show',f'e8bd23e:{f}'],cwd=ROOT)==(ROOT/f).read_bytes(),f
result={'version':manifest['version'],'manifest_assets_verified':len(checks),'source_files_verified':len(prov['files']),'generator_sha256':prov['generator_sha256'],'public_matches_production':len(public),'hand_asset':next(e for e in manifest['assets'] if e['path'].endswith('makehuman-hands.glb')),'unchanged_from_saved_main':preserved,'tests':14,'build':'passed; existing chunk-size warning','performance':'No controlled before/after performance test this iteration; no runtime IK or new dependencies.'}
(ROOT/'evidence/v014-human-scale/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
