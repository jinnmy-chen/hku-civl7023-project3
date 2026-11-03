import FreeCAD as A,Part,json
from FreeCAD import Vector as V
from pathlib import Path
O=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d\outputs\PartA_Stage1')
s=Part.Shape();s.read(str(O/'01_CAD/P3_V2_mm.brep'))
top=[f for f in s.Faces if f.BoundBox.ZLength<1e-7 and abs(f.BoundBox.ZMin-22)<1e-7]
bottom=[f for f in s.Faces if f.BoundBox.ZLength<1e-7 and abs(f.BoundBox.ZMin)<1e-7]
area=0
for a in top:
 for b in bottom:
  b=b.copy();b.translate(V(0,0,22));area+=a.common(b).Area
mass=s.Volume*2500e-9;weight=mass*1.62
test=Part.makeBox(2,1,1);test.rotate(V(0,0,0),V(0,0,1),45)
r={'ideal_planar_bearing_area_mm2':area,'density_kg_m3_assumed':2500,'upper_component_weight_N':weight,'average_bearing_pressure_Pa':weight/(area*1e-6),'scope':'ideal centered gravity load, nominal parallel planes; excludes contact deformation, tolerance, material strength, lateral loads and overturning','inertia_convention_probe_rotated_2x1x1_box_A12':test.MatrixOfInertia.A12,'expected_physical_tensor_A12':-.25}
(O/'04_Mass/ideal_support_check.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r))
