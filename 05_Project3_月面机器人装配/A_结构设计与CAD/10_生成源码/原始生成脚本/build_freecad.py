import FreeCAD as A, Part, Sketcher, Mesh, Import
from FreeCAD import Vector as V
import FreeCADGui as Gui
Gui.showMainWindow()
Gui.getMainWindow().hide()
from PySide import QtWidgets
Gui.activateWorkbench('PartWorkbench')
import json, csv, math, os, traceback
from pathlib import Path
ROOT=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d')
OUT=Path(os.environ.get('PARTA_OUTPUT',str(ROOT/'outputs'/'PartA_Stage1')))
SRC=Path(os.environ.get('PARTA_INPUT',r'C:\Users\Administrator\Desktop\PartA_Codex配套资料_2026-11-03\数据与参考模型'))
for n in ['01_CAD','02_Assembly','03_Drawings','04_Mass','05_Notes','06_Handoff']:(OUT/n).mkdir(parents=True,exist_ok=True)
PARAMS={'L':50,'W':30,'H':22,'slotL':38,'slotD':4,'slotZ':10,'bossC':20,'bossH':3,'bossX':4,'bossY':8,'tipX':2,'tipY':6,'entryX':8,'entryY':12,'socketX':6,'socketY':10,'entryH':0.5,'socketH':3.5}
def expr(o,p,e):o.setExpression(p,e)
def model(name):
 d=A.newDocument(name); p=d.addObject('Spreadsheet::Sheet','Parameters');p.Label='Edit dimensions here (mm)'
 for i,(key,val) in enumerate(PARAMS.items(),1):p.set('A'+str(i),key);p.set('B'+str(i),str(val));p.setAlias('B'+str(i),'p_'+key)
 def box(n,dim,pos):
  o=d.addObject('Part::Box',n)
  for k,e in zip(['Length','Width','Height'],dim):expr(o,k,'Parameters.p_'+e if e in PARAMS else e)
  for k,e in zip(['x','y','z'],pos):expr(o,'Placement.Base.'+k,e)
  d.recompute();return o
 def rect(n,xsize,ysize,cx,z):
  s=d.addObject('Sketcher::SketchObject',n)
  w=PARAMS[xsize];h=PARAMS[ysize];c=20 if cx=='Parameters.p_bossC' else -20
  ps=[(c-w/2,-h/2),(c+w/2,-h/2),(c+w/2,h/2),(c-w/2,h/2)]
  for i in range(4):s.addGeometry(Part.LineSegment(V(*ps[i],0),V(*ps[(i+1)%4],0)),False)
  for i in range(4):s.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%4,1))
  for i in [0,2]:s.addConstraint(Sketcher.Constraint('Horizontal',i))
  for i in [1,3]:s.addConstraint(Sketcher.Constraint('Vertical',i))
  k=s.addConstraint(Sketcher.Constraint('Distance',0,w));s.setExpression('Constraints[%d]'%k,'Parameters.p_'+xsize)
  k=s.addConstraint(Sketcher.Constraint('Distance',1,h));s.setExpression('Constraints[%d]'%k,'Parameters.p_'+ysize)
  k=s.addConstraint(Sketcher.Constraint('DistanceX',0,1,ps[0][0]));s.setExpression('Constraints[%d]'%k,cx+'-Parameters.p_'+xsize+'/2')
  k=s.addConstraint(Sketcher.Constraint('DistanceY',0,1,ps[0][1]));s.setExpression('Constraints[%d]'%k,'-Parameters.p_'+ysize+'/2')
  expr(s,'Placement.Base.z',z);d.recompute();return s
 def loft(n,sections):
  l=d.addObject('Part::Loft',n);l.Sections=sections;l.Solid=True;l.Ruled=True;l.Closed=False;d.recompute();return l
 def cut(n,b,t):
  q=d.addObject('Part::Cut',n);q.Base=b;q.Tool=t;q.Refine=True;d.recompute();return q
 base=box('Body',('L','W','H'),('-Parameters.p_L/2','-Parameters.p_W/2','0 mm'))
 for sign in [-1,1]:
  yy='-Parameters.p_W/2' if sign<0 else 'Parameters.p_W/2-Parameters.p_slotD'
  tool=box('GripSlot'+str(sign+1),('slotL','slotD','Parameters.p_H-Parameters.p_slotZ'),('-Parameters.p_slotL/2',yy,'Parameters.p_slotZ'))
  base=cut('CutGrip'+str(sign+1),base,tool)
 bosses=[];sockets=[]
 for idx,cx in enumerate(['-Parameters.p_bossC','Parameters.p_bossC']):
  bosses.append(loft('Boss%d'%idx,[rect('BossRoot%d'%idx,'bossX','bossY',cx,'Parameters.p_H'),rect('BossTip%d'%idx,'tipX','tipY',cx,'Parameters.p_H+Parameters.p_bossH')]))
  entry=loft('SocketEntry%d'%idx,[rect('Mouth%d'%idx,'entryX','entryY',cx,'0 mm'),rect('Throat%d'%idx,'socketX','socketY',cx,'Parameters.p_entryH')])
  wall=loft('SocketWall%d'%idx,[rect('WallStart%d'%idx,'socketX','socketY',cx,'Parameters.p_entryH'),rect('WallEnd%d'%idx,'socketX','socketY',cx,'Parameters.p_socketH')])
  fu=d.addObject('Part::Fuse','SocketTool%d'%idx);fu.Base=entry;fu.Tool=wall;fu.Refine=True;d.recompute();sockets.append(fu)
 fu=d.addObject('Part::MultiFuse','AddBosses');fu.Shapes=[base]+bosses;fu.Refine=True;d.recompute()
 for i,t in enumerate(sockets):fu=cut('CutSocket%d'%i,fu,t)
 fu.Label='P3-GrooveKey-v2 | final solid';d.recompute()
 for o in d.Objects:
  if hasattr(o,'ViewObject'):o.ViewObject.Visibility=False
 fu.ViewObject.Visibility=True;fu.ViewObject.ShapeColor=(0.86,0.49,0.12)
 return d,fu,p
def vec(v):return [v.x,v.y,v.z]
def stats(s):
 b=s.BoundBox;solid=s.Solids[0];m=solid.MatrixOfInertia
 return {'valid':s.isValid(),'closed':all(x.isClosed() for x in s.Solids),'solids':len(s.Solids),'volume_mm3':s.Volume,'com_mm':vec(solid.CenterOfMass),'bounds_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'unit_density_centroid_inertia_mm5':[[m.A11,m.A12,m.A13],[m.A21,m.A22,m.A23],[m.A31,m.A32,m.A33]],'faces':len(s.Faces)}
def run():
 d,f,p=model('P3_V2_Parametric');s=f.Shape;st=stats(s)
 assert st['valid'] and st['closed'] and st['solids']==1,st
 assert abs(s.Volume-29042.6666666667)<1e-5,st
 d.recompute();d.saveAs(str(OUT/'01_CAD'/'P3_V2_Parametric.FCStd'))
 Gui.setActiveDocument(d.Name);QtWidgets.QApplication.processEvents()
 Gui.getDocument(d.Name).activeView().viewAxonometric();Gui.getDocument(d.Name).activeView().fitAll()
 Gui.getDocument(d.Name).activeView().saveImage(str(OUT/'03_Drawings'/'single_CAD.png'),1500,1100,'White')
 Import.export([f],str(OUT/'01_CAD'/'P3_V2_mm.step'))
 s.exportBrep(str(OUT/'01_CAD'/'P3_V2_mm.brep'))
 me=Mesh.Mesh(s.tessellate(0.01));me.write(str(OUT/'01_CAD'/'P3_V2_mm.stl'));mt=A.Matrix();mt.scale(0.001,0.001,0.001);me.transform(mt);me.write(str(OUT/'01_CAD'/'P3_V2_m.stl'))
 # Validate exported STEP by reopening via the CAD kernel.
 rd=A.newDocument('StepReopened');Import.insert(str(OUT/'01_CAD'/'P3_V2_mm.step'),rd.Name);rd.recompute()
 rst=stats(Part.makeCompound([o.Shape for o in rd.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]))
 # Native parameter edit, recompute and restore: proves editable dependency chain.
 p.set('B1','52');d.recompute();edit=stats(f.Shape);assert abs(f.Shape.BoundBox.XLength-52)<1e-7
 p.set('B1','50');d.recompute();assert abs(f.Shape.Volume-s.Volume)<1e-5
 d.save()
 st['step_reopened']=rst;st['parameter_edit_test_L52']=edit;st['freecad_version']=A.Version()
 rho=2500.0 # Explicit provisional modelling assumption; not measured lunar material.
 st['density_kg_m3']=rho;st['density_status']='provisional uniform solid modelling assumption, not certified material'
 st['mass_kg']=s.Volume*1e-9*rho;st['com_m']=[x*1e-3 for x in st['com_mm']]
 st['inertia_COM_kg_m2']=[[x*rho*1e-15 for x in row] for row in st['unit_density_centroid_inertia_mm5']]
 (OUT/'04_Mass'/'CAD_mass_and_validation.json').write_text(json.dumps(st,indent=2),encoding='utf8')
 rows=list(csv.DictReader((SRC/'C_16件初始与目标位姿.csv').open(encoding='utf-8-sig')))
 six=[(240+50*i,80,22*j,0,'L%d_%d'%(j+1,i+1)) for j in range(2) for i in range(3)]
 octa=[(float(r['target_x_m'])*1000,float(r['target_y_m'])*1000,float(r['target_z_m'])*1000,float(r['target_yaw_deg']),'Part%02d'%int(r['item'])) for r in rows]
 for name,poses in [('SixWall_Baseline',six),('Octagon16_Candidate',octa)]:
  ad,af,ap=model(name);links=[]
  af.ViewObject.Visibility=False
  for x,y,z,yaw,n in poses:
   o=ad.addObject('App::Link',n);o.setLink(af);o.LinkPlacement=A.Placement(V(x,y,z),A.Rotation(V(0,0,1),yaw));o.ViewObject.Visibility=True;links.append(o)
  ad.recompute();ad.saveAs(str(OUT/'02_Assembly'/(name+'.FCStd')))
  Gui.setActiveDocument(ad.Name);QtWidgets.QApplication.processEvents()
  Gui.getDocument(ad.Name).activeView().viewAxonometric();Gui.getDocument(ad.Name).activeView().fitAll()
  Gui.getDocument(ad.Name).activeView().saveImage(str(OUT/'03_Drawings'/(name+'_CAD.png')),1600,1100,'White')
  Import.export(links,str(OUT/'02_Assembly'/(name+'_mm.step')))
  comp=Part.makeCompound([o.Shape for o in links]);comp.exportBrep(str(OUT/'02_Assembly'/(name+'_mm.brep')))
  Mesh.Mesh(comp.tessellate(0.01)).write(str(OUT/'02_Assembly'/(name+'_mm.stl')))
  checks=[]
  for i in range(len(links)):
   for j in range(i):
    vol=links[i].Shape.common(links[j].Shape).Volume
    if vol>1e-6:checks.append([j+1,i+1,vol])
  (OUT/'02_Assembly'/(name+'_validation.json')).write_text(json.dumps({'count':len(links),'intersection_volume_failures_mm3':checks,'sum_volume_mm3':comp.Volume,'coordinate_frame':'robot world, mm','source_hidden_at_origin':True,'instances_exported_only':True},indent=2),encoding='utf8')
 # Edge projections for dimensioned vector drawings, from actual CAD shape.
 def edges(shape):
  out=[]
  for e in shape.Edges:
   points=e.discretize(Deflection=0.01);out.append([vec(v) for v in points])
  return out
 (OUT/'03_Drawings'/'cad_edges.json').write_text(json.dumps({'single':edges(s),'section_x20':edges(s.section(Part.makePlane(100,100,V(20,-50,-25),V(1,0,0)))),'wall':edges(Part.makeCompound([s.copy().translated(V(x,y,z)) for x,y,z,a,n in six]))}),encoding='utf8')
 print('PARTA_FREECAD_SUCCESS',json.dumps(st))
try:run()
except Exception:
 (OUT/'06_Handoff'/'build_failure.txt').write_text(traceback.format_exc(),encoding='utf8');print(traceback.format_exc())

