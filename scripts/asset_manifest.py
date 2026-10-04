"""Record the exact local assets and GLB contents without third-party dependencies."""
from pathlib import Path
import json, struct, hashlib
root = Path(__file__).resolve().parents[1]
paths = [*sorted((root / 'public/assets/models').glob('*.glb')),
         *sorted(path for path in (root / 'public/assets/textures').iterdir() if path.suffix in ('.png', '.webp')),
         *sorted((root / 'public/assets/animation').glob('*.bin')),
         root / 'assets/source/storyos-library.blend',
         root / 'assets/source/writer-hands.blend',
         root / 'assets/source/makehuman-hands.blend']
assets = []
for path in paths:
    data = path.read_bytes()
    entry = {'path':str(path.relative_to(root)), 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}
    if path.suffix == '.glb':
        magic, version, size = struct.unpack_from('<4sII', data)
        assert (magic, version, size) == (b'glTF', 2, len(data))
        json_size, chunk = struct.unpack_from('<I4s', data, 12)
        assert chunk == b'JSON'
        gltf = json.loads(data[20:20+json_size])
        entry.update(meshes=len(gltf.get('meshes', [])), materials=len(gltf.get('materials', [])),
                     embedded_images=len(gltf.get('images', [])),
                     skins=len(gltf.get('skins', [])), joints=[len(skin['joints']) for skin in gltf.get('skins', [])],
                     primitives=sum(len(m['primitives']) for m in gltf.get('meshes', [])),
                     triangles=sum(gltf['accessors'][p['indices']]['count']//3
                                   for m in gltf['meshes'] for p in m['primitives'] if 'indices' in p))
        assert all('uri' not in b for b in gltf.get('buffers', [])), 'External buffer unexpectedly required'
        assert all('uri' not in i for i in gltf.get('images', [])), 'External image unexpectedly required'
    assets.append(entry)
lock = json.loads((root / 'apps/web/package-lock.json').read_text())
packages = ['react','vite','three','@react-three/fiber','@react-three/drei','@react-three/postprocessing']
scene = json.loads((root/'public/assets/models/scene.json').read_text())
manifest = {'version':'0.1.5-preview.4', 'room_version':scene['version'], 'baseline':scene['baseVersion'],
            'source_script':'scripts/build_library.py', 'hands_script':'scripts/build_makehuman_hands.py', 'hands_provenance':'assets/source/makehuman-hands.json', 'book_motion_provenance':'assets/source/soft-book-motion.json', 'lighting_script':'scripts/bake_room_lighting.py', 'source_blender':scene['blender'],
            'runtime_versions':{p:lock['packages']['node_modules/'+p]['version'] for p in packages},
            'assets':assets, 'texture_provenance':['assets/source/wood-texture.json','assets/source/a-study-wood.json','assets/source/a-study-rug.json','assets/source/room-lighting.json','assets/source/plaster-texture.json','assets/source/hearth-decor-atlas.json','assets/source/manuscript/provenance.json','assets/source/manuscript-soft/provenance.json'],
            'book_appearance':'Thin leather and blank paper use gravity/contact trajectories baked by tools/book-check/bake-soft-book.mjs; source and asset hashes are in assets/source/soft-book-motion.json. The right hand carries its support past the binding before release; free edges drape over the actual lectern and front lip. Runtime interpolates a shared binary. Historical text texture and book GLB are no longer loaded.',
            'visual_target':scene.get('visualTarget'), 'layout_source':scene.get('layoutSource'),
            'network_references':'Room reference images are research only. Hand mesh and skin use the documented CC0 MakeHuman sources.',
            'animation_source':'The hand GLB retains its archived bake sequence; runtime retimes and transforms its support using book-support.mjs. OpeningHands.jsx plays one baked clip with 42 anatomical joints, 48 cloth joints and 10 skin corrective morphs from makehuman-hands.glb. SoftBook.mjs samples baked elastic strips. Rejected writer-hands files are retained as experiment history and are not loaded. HearthFire.jsx and HearthBed.jsx add procedural detail over the unchanged room asset.'}
(root/'assets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'assets':len(assets),'glb_bytes':sum(a['bytes'] for a in assets if a['path'].endswith('.glb'))}))
