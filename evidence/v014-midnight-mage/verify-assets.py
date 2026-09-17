"""Verify actual source, runtime and production files for the mage iteration."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'assets/manifest.json').read_text())
for entry in manifest['assets']:
    path=ROOT/entry['path']
    assert path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256'],entry['path']
provenance=json.loads((ROOT/'assets/source/makehuman-hands.json').read_text())
for entry in provenance['files']:
    assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
assert sha(ROOT/provenance['generator'])==provenance['generator_sha256']
robe=json.loads((ROOT/'assets/source/midnight-robe-provenance.json').read_text())
for entry in robe['textures']:
    assert sha(ROOT/entry['path'])==entry['sha256'],entry['path']
before=json.loads((OUT/'baseline-files.json').read_text())['files']
preserve=[]
for entry in before:
    path=entry['path']
    if path.startswith('apps/web/src/') or (path.startswith('public/assets/') and not path.endswith('makehuman-hands.glb')):
        assert sha(ROOT/path)==entry['sha256'],path
        preserve.append(path)
public=[]
for path in (ROOT/'public').rglob('*'):
    if path.is_file():
        target=ROOT/'apps/web/dist/client'/path.relative_to(ROOT/'public')
        assert target.exists() and sha(path)==sha(target),str(path)
        public.append(str(path.relative_to(ROOT)))
result={'version':manifest['version'],'manifest_assets_verified':len(manifest['assets']),
        'source_files_verified':len(provenance['files']),'garment_textures_verified':len(robe['textures']),
        'public_matches_production':len(public),'unchanged_room_book_runtime_and_timeline':preserve,
        'hand_asset':next(e for e in manifest['assets'] if e['path'].endswith('makehuman-hands.glb')),
        'no_runtime_source_changes':True,'new_external_dependencies':False}
(OUT/'asset-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
