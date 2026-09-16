from pathlib import Path
s=Path('scripts/check_scene.py').read_text();s=s[:s.index('layout = json.loads(LAYOUT_PATH')]
__file__=str(Path('scripts/check_scene.py').resolve())
exec(compile(s,'scripts/check_scene.py','exec'))
bpy.ops.wm.open_mainfile(filepath=str(CURRENT))
for c in connected_room_geometry():
 if c['material']=='ReadingWood' and abs(c['center'][1]-1.18)<.002:
  print('TOP_CANDIDATE',c['center'],c['size'])
