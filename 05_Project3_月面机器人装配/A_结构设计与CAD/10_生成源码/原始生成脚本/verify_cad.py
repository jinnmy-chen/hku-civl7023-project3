import FreeCAD as A,Part,Mesh,Import,json
from pathlib import Path
R=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d')
O=R/'outputs/PartA_Stage1';S=Part.Shape();S.read(str(O/'01_CAD/P3_V2_mm.brep'))
report={}
for name,count,folder in [('P3_V2_mm',1,'01_CAD'),('SixWall_Baseline_mm',6,'02_Assembly'),('Octagon16_Candidate_mm',16,'02_Assembly')]:
 d=A.newDocument(name);Import.insert(str(O/folder/(name+'.step')),d.Name);d.recompute()
 shapes=[o.Shape for o in d.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
 # Imported STEP uses an assembly tree. Count only leaf geometry (no duplicated parents).
 leaves=[o.Shape for o in d.Objects if hasattr(o,'Shape') and len(o.Shape.Solids)>0 and not any(hasattr(c,'Shape') and len(c.Shape.Solids)>0 for c in o.OutList)]
 comp=Part.makeCompound(leaves)
 n=len(comp.Solids);assert n==count,(name,n)
 assert all(x.isValid() and x.isClosed() for x in comp.Solids)
 assert abs(comp.Volume-count*S.Volume)<1e-5
 report[name]={'reopened_solids':n,'volume_mm3':comp.Volume,'valid':True,'bounds':[comp.BoundBox.XMin,comp.BoundBox.YMin,comp.BoundBox.ZMin,comp.BoundBox.XMax,comp.BoundBox.YMax,comp.BoundBox.ZMax]}
for unit,scale in [('mm',1),('m',.001)]:
 m=Mesh.Mesh(str(O/'01_CAD'/('P3_V2_'+unit+'.stl')))
 report['STL_'+unit]={'solid':m.isSolid(),'volume':m.Volume,'facets':m.CountFacets,'x_length':m.BoundBox.XLength}
 assert m.isSolid() and abs(m.BoundBox.XLength-50*scale)<1e-6
b=Mesh.Mesh(r'C:\Users\Administrator\Desktop\PartA_Codex配套资料_2026-11-03\数据与参考模型\groove_key_block_mm.stl')
sh=Part.Shape();sh.makeShapeFromMesh(b.Topology,.00001);solid=Part.makeSolid(Part.makeShell(sh.Faces));valid=solid.isValid()
diff=S.cut(solid).Volume+solid.cut(S).Volume
report['B_reference_mesh_comparison']={'valid_mesh_solid':valid,'reference_volume_mm3':solid.Volume,'symmetric_difference_mm3':diff,'comparison_tolerance_mm3':.01,'pass':diff<.01}
assert diff<.01,report
(O/'06_Handoff'/'reopen_and_mesh_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
