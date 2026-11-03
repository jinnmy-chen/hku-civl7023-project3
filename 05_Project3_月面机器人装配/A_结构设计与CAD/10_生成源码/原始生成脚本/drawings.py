from pathlib import Path
import json,math,html
import FreeCAD as A,Part
from FreeCAD import Vector as V
from PySide import QtCore,QtGui,QtSvg
R=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d')
O=R/'outputs/PartA_Stage1/03_Drawings'
S=Part.Shape();S.read(str(R/'outputs/PartA_Stage1/01_CAD/P3_V2_mm.brep'))
app=QtGui.QGuiApplication.instance() or QtGui.QGuiApplication([])
class Page:
 def __init__(self,title,num):
  self.elements=[];self.dxf=[];self.num=num
  self.elements.append('<defs><marker id="a" markerWidth="9" markerHeight="7" refX="4.5" refY="3.5" orient="auto-start-reverse"><path d="M9 0L0 3.5L9 7" fill="none" stroke="#23748c"/></marker><pattern id="h" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M0 10L10 0" stroke="#a3bac2" stroke-width="1"/></pattern></defs>')
  self.text(50,58,title,29);self.text(50,92,'P3-GrooveKey-v2 | 长度 mm | 名义设计，未含制造公差 | 2026-11-03',17)
  self.line(40,112,1560,112,'#c7d5dc');self.line(40,1030,1560,1030,'#c7d5dc')
  self.text(50,1064,'A / CIVL 7023    ·    来源：实际CAD实体投影与参数；不代表动态装配或结构强度验收',16)
  self.text(1480,1064,num,16)
 def text(self,x,y,t,size=18,color='#203a48'):
  self.elements.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-family="Microsoft YaHei,Arial,sans-serif">{html.escape(str(t))}</text>')
  self.dxf+=['0','TEXT','8','TEXT','10',str(x/8),'20',str((1100-y)/8),'40',str(size/8),'1',str(t),'7','Standard']
 def line(self,x1,y1,x2,y2,color='#203a48',dash=False):
  self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"'+(' stroke-dasharray="7 5"' if dash else '')+'/>')
  self.dxf+=['0','LINE','8','GEOMETRY','10',str(x1/8),'20',str((1100-y1)/8),'11',str(x2/8),'21',str((1100-y2)/8)]
 def dim(self,a,b,t,tx=0,ty=-8):
  x1,y1=a;x2,y2=b
  self.elements.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#23748c" stroke-width="1.3" marker-start="url(#a)" marker-end="url(#a)"/>')
  self.text((x1+x2)/2+tx,(y1+y2)/2+ty,t,18,'#16657b')
  # DXF contains editable dimension reference geometry and text (not associative DIM entities).
  self.dxf+=['0','LINE','8','DIMREF','10',str(x1/8),'20',str((1100-y1)/8),'11',str(x2/8),'21',str((1100-y2)/8)]
 def proj(self,shape,axes,ox,oy,k=8):
  def q(v):return (ox+v[axes[0]]*k,oy-v[axes[1]]*k)
  for e in shape.Edges:
   pts=e.discretize(Deflection=.01)
   for a,b in zip(pts,pts[1:]):self.line(*q(a),*q(b))
 def polygon(self,pts):
  self.elements.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in pts)+'" fill="url(#h)" stroke="#203a48" stroke-width="2"/>')
 def save(self,name):
  svg='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100" viewBox="0 0 1600 1100"><rect width="1600" height="1100" fill="white"/>'+''.join(self.elements)+'</svg>'
  (O/(name+'.svg')).write_text(svg,encoding='utf8')
  renderer=QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode('utf8')));im=QtGui.QImage(1600,1100,QtGui.QImage.Format_ARGB32);im.fill(QtGui.QColor('white'));p=QtGui.QPainter(im);renderer.render(p);p.end();im.save(str(O/(name+'.png')))
  content=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1021','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']+self.dxf+['0','ENDSEC','0','EOF']
  (O/(name+'.dxf')).write_text('\n'.join(content)+'\n',encoding='utf8')

p=Page('A01  单件三视图与抓取坐标','1/4')
p.text(150,160,'俯视 XY（含内部投影轮廓）',20);p.proj(S,(0,1),350,345,8)
p.dim((150,195),(550,195),'50',-10);p.dim((600,225),(600,465),'30',10,0)
p.dim((198,495),(502,495),'38',-10);p.text(145,535,'两侧槽：38 × 4 × 12，顶部敞开',18)
p.text(145,565,'两夹持面 Y=±11，间距22；两端各留6',18)
p.text(850,160,'正视 XZ（含内部投影轮廓）',20);p.proj(S,(0,2),1110,430,8)
p.dim((1370,230),(1370,430),'25',10,0);p.dim((1325,254),(1325,430),'22',-35,0)
p.dim((910,475),(1310,475),'50',-10);p.text(865,530,'凸台中心 X=±20，根部4×8、顶部2×6',18)
p.text(865,560,'底部凹口是非通孔，总深3.5含入口0.5',18)
p.text(150,650,'侧视 YZ（含内部投影轮廓）',20);p.proj(S,(1,2),350,920,8)
p.dim((230,965),(470,965),'30',-10)
p.text(780,680,'坐标与机器人接口',23)
for y,t in enumerate(['O=(0,0,0)：底面中心；+X长边，+Y宽边，+Z向上。','名义抓取TCP相对O：(0,0,14)mm。','槽底Z=10；主体顶Z=22；凸台顶Z=25。','接近开口36mm；C闭合指令22mm（不是已验证夹持性能）。','CAD毫米 → 仿真米：坐标乘0.001。','原点不等于质心；不得自动居中导出。','绘图参考比例：8px/mm；DXF为排版参考图，禁止按图量取。']):p.text(780,730+y*36,t,17)
p.save('A01_ThreeViews')

p=Page('A02  接口剖视与两层插合','2/4')
def sec(shape,x,ox,oy,k):
 wires=shape.slice(V(1,0,0),x)
 for w in wires:
  pts=w.discretize(Deflection=.005);p.polygon([(ox+v.y*k,oy-v.z*k) for v in pts])
p.text(110,160,'A—A：X=20 的 YZ 剖面，单件',21);sec(S,20,350,820,20)
p.dim((700,320),(700,820),'总高25',15,0);p.dim((230,865),(470,865),'入口Y宽12',-55)
p.text(100,935,'剖切经过凸台和凹口中心；X方向尺寸见下表',17)
p.text(900,160,'同向两层插合局部（X=20）',21)
up=S.copy();up.translate(V(0,0,22));both=Part.makeCompound([S,up]);sec(both,20,1170,900,12)
p.dim((1470,336),(1470,900),'47',15,0);p.dim((1390,636),(1390,900),'层距22',10,0)
p.text(890,965,'上层底面Z=22；凸台插入3；顶余量0.5',17)
for y,t in enumerate(['接口名义尺寸（X×Y，mm）','凸台根部 4×8 → 顶部2×6，高3','凹口入口 8×12 → 内部6×10','入口导向深0.5；总深3.5','内部与根部比较：X/Y每侧1','以上均为几何间隙，不是制造公差']):p.text(760,185+y*27,t,15)
p.save('A02_InterfaceSections')

rows=list(__import__('csv').DictReader((Path(r'C:\Users\Administrator\Desktop\PartA_Codex配套资料_2026-11-03\数据与参考模型')/'C_16件初始与目标位姿.csv').open(encoding='utf-8-sig')))
p=Page('A03  16件八边形装配候选版：目标、朝向与顺序','3/4')
for r in rows[:8]:
 x=float(r['target_x_m'])*1000;y=float(r['target_y_m'])*1000;a=float(r['target_yaw_rad']);t=S.copy();t.rotate(V(0,0,0),V(0,0,1),math.degrees(a));t.translate(V(x-260,y-30,0));p.proj(t,(0,1),470,540,3.6)
 px=470+(x-260)*4.8;py=540-(y-30)*4.8;p.text(px-26,py,f'{r["item"]}/{int(r["item"])+8}',19)
p.line(440,540,500,540,'#23748c');p.line(470,510,470,570,'#23748c');p.text(330,558,'中心(260,30,0)',16)
p.text(75,980,'标号：下层/对应上层；同层顺序按表，不按圆周。',18)
p.text(945,180,'世界底面原点，mm；yaw绕+Z，deg',20)
for xx,t in zip([945,1010,1130,1250,1350],['件号','X','Y','Z','yaw']):p.text(xx,224,t,17)
for i,r in enumerate(rows):
 vals=[float(r['target_'+c+'_m'])*1000 for c in 'xyz']
 for xx,t in zip([945,1010,1130,1250,1350],[f'{int(r["item"]):02d}',f'{vals[0]:.3f}',f'{vals[1]:.3f}',f'{vals[2]:.1f}',f'{float(r["target_yaw_deg"]):.1f}']):p.text(xx,263+i*34,t,17)
p.text(930,865,'底面中心半径76；第二层底面22；最高点47。',17)
p.text(930,905,'转角开缝、无横向连接；非气密/承重验证。',17)
p.text(930,945,'精确坐标与四元数见随附CSV，图表数值有舍入。',16)
p.save('A03_OctagonTargets')

p=Page('A04  设计、质量属性与验证范围','4/4')
m=json.loads((R/'outputs/PartA_Stage1/04_Mass/CAD_mass_and_validation.json').read_text())
sections=[('几何与质量（均匀材料假设）',[f'CAD体积：{m["volume_mm3"]:.7f} mm³','密度ρ=2500 kg/m³：暂定建模假设，不是本组材料实测值。',f'单件质量：{m["mass_kg"]*1000:.6f} g；几何质心Z={m["com_mm"][2]:.8f} mm。',f'质心惯量Ixx/Iyy/Izz：{m["inertia_COM_kg_m2"][0][0]:.9g} / {m["inertia_COM_kg_m2"][1][1]:.9g} / {m["inertia_COM_kg_m2"][2][2]:.9g} kg·m²。','对称性使非对角项理论为0；原始计算残差另存JSON。']),('设计理由与待验证事项',['重复单件与统一接口便于制造、抓取和定位；槽向上敞开便于退出。','顶部斜面与底部入口提供几何导向空间，尚未证明动态自纠偏。','上下为松配合，未锁止抗拔；各列/转角无侧向连接。','烧结收缩、粗糙度、细凸台脆弱性、制造公差尚待材料与工艺验证。']),('本阶段检查与交接',['实际生成AutoCAD DWG实体、参数化FCStd、STEP与mm/m STL。','单件体积/包络/闭合性、STEP重开、参数编辑重算、装配体积干涉已检查。','C已有结果使用临时参数与接触触发辅助约束，物理过程经过检查点续跑。','更换质量/惯量后须由B/C复测；现有数据不含实际关节力矩。'])]
y=175
for title,lines in sections:
 p.text(90,y,title,23);y+=43
 for t in lines:p.text(110,y,t,19);y+=39
 y+=28
p.save('A04_DesignAndMass')
print('DRAWINGS_COMPLETE')
