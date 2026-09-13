"""Record the exact local assets and GLB contents without third-party dependencies."""
from pathlib import Path
import json, struct, hashlib
root = Path(__file__).resolve().parents[1]
paths = [*sorted((root / 'public/assets/models').glob('*.glb')),
         *sorted((root / 'public/assets/textures').glob('*.png')),
         root / 'assets/source/storyos-library.blend']
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
                     triangles=sum(gltf['accessors'][p['indices']]['count']//3
                                   for m in gltf['meshes'] for p in m['primitives'] if 'indices' in p))
        assert all('uri' not in b for b in gltf.get('buffers', [])), 'External buffer unexpectedly required'
        assert all('uri' not in i for i in gltf.get('images', [])), 'External image unexpectedly required'
    assets.append(entry)
lock = json.loads((root / 'apps/web/package-lock.json').read_text())
packages = ['react','vite','three','@react-three/fiber','@react-three/drei','@react-three/postprocessing']
manifest = {'source_script':'scripts/build_library.py', 'source_blender':json.loads((root/'public/assets/models/scene.json').read_text())['blender'],
            'runtime_versions':{p:lock['packages']['node_modules/'+p]['version'] for p in packages},
            'assets':assets, 'texture_provenance':['assets/source/wood-texture.json','assets/source/plaster-texture.json'],
            'network_references':'Design research only; not shipped as scene content.',
            'animation_source':'Deterministic runtime transforms in apps/web/src/Scene.jsx, using Blender CoverPivot/PagePivot and prebuilt hands. No baked skeletal clips.'}
(root/'assets/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'assets':len(assets),'glb_bytes':sum(a['bytes'] for a in assets if a['path'].endswith('.glb'))}))
