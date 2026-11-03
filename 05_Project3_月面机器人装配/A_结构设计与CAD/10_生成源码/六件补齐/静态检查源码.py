from pathlib import Path
import json,csv,hashlib,xml.etree.ElementTree as ET
import FreeCAD,Mesh
R=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d')
O=R/'outputs/PartA_Six_Stage1_20261104'
B=Path(r'C:\Users\Administrator\Desktop\7023(1)\Project32026-10-30\Project3_B_to_C_2026-10-30\05_Project3_月面机器人装配\B_工作空间与设计约束\构件模型')
source=json.loads((B/'parameters.json').read_text(encoding='utf8'))
model=O/'06_可加载构件';tree=ET.parse(model/'component_V2_provisional.urdf').getroot()
assert len(tree.findall('link'))==1 and not tree.findall('joint')
assert len(tree.findall('.//collision'))==34
for mesh in tree.findall('.//mesh'):
 assert (model/mesh.attrib['filename']).is_file(),mesh.attrib
 assert mesh.attrib.get('scale')=='1 1 1'
checked=[]
for f in source['collision_parts']:
 h=hashlib.sha256((model/'meshes'/f).read_bytes()).hexdigest();assert h==source['file_sha256'][f]
 checked.append({'mesh':f,'sha256':h})
visual=Mesh.Mesh(str(model/'meshes/component_m.stl'))
assert visual.isSolid()
assert abs(visual.BoundBox.XLength-.05)<1e-7 and abs(visual.BoundBox.YLength-.03)<1e-7 and abs(visual.BoundBox.ZLength-.025)<1e-7
rows=list(csv.DictReader((O/'03_抓放目标与顺序/六件初始与抓放目标.csv').open(encoding='utf-8-sig')))
assert len(rows)==6
for i,r in enumerate(rows):
 assert int(r['order'])==i+1
 assert abs(float(r['place_tcp_z_m'])-float(r['target_z_m'])-.014)<1e-10
 assert abs(float(r['pick_tcp_z_m'])-.014)<1e-10
 assert float(r['travel_tcp_z_m'])==.082
r={'static_checks':'passed','URDF_links':1,'URDF_collisions':34,'mesh_paths_exist':True,'all_collision_meshes_match_B_hashes':True,'visual_mesh_solid':True,'visual_mesh_envelope_m':[visual.BoundBox.XLength,visual.BoundBox.YLength,visual.BoundBox.ZLength],'nominal_goal_records_checked':6,'source':'B V2 baseline; A CAD outputs','URDF_runtime_load':'not executed; PyBullet build unavailable locally (MSVC required)','robot_pick_place':'not executed in this supplement','team_interface_confirmation':'not received','collision_files':checked}
(O/'05_BC交接/本次补齐静态检查记录.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('STATIC_CHECKS_PASSED; runtime load and robot execution remain pending')
