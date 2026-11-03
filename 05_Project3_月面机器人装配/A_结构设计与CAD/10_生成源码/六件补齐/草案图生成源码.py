from pathlib import Path
import FreeCAD as A,Part,html
from PySide import QtCore,QtGui,QtSvg
R=Path(r'C:\Users\Administrator\Documents\Codex\2026-11-03\co-d')
O=R/'outputs/PartA_Six_Stage1_20261104/01_草案与坐标图'
app=QtGui.QGuiApplication.instance() or QtGui.QGuiApplication([])
def start(title):return ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M8 0L0 4L8 8" fill="none" stroke="#197c91"/></marker></defs><rect width="1600" height="1100" fill="white"/>',text(60,65,title,30),text(60,104,'P3-GrooveKey-v2 | 六件两层第一阶段 | 名义长度 mm | 2026-11-04',18)]
def text(x,y,s,h=18):return f'<text x="{x}" y="{y}" font-family="Microsoft YaHei,Arial,sans-serif" font-size="{h}" fill="#203e4a">{html.escape(str(s))}</text>'
def line(a,b,color='#25434f',arrow=False):return f'<path d="M{a[0]},{a[1]}L{b[0]},{b[1]}" fill="none" stroke="{color}" stroke-width="1.5"'+(' marker-start="url(#a)" marker-end="url(#a)"' if arrow else '')+'/>'
def save(parts,n):
 svg=''.join(parts)+'</svg>';(O/(n+'.svg')).write_text(svg,encoding='utf8');rend=QtSvg.QSvgRenderer(QtCore.QByteArray(svg.encode()));im=QtGui.QImage(1600,1100,QtGui.QImage.Format_ARGB32);im.fill(QtGui.QColor('white'));p=QtGui.QPainter(im);rend.render(p);p.end();im.save(str(O/(n+'.png')))
s=Part.Shape();s.read(str(R/'outputs/PartA_Stage1/02_Assembly/SixWall_Baseline_mm.brep'))
p=start('F01  六件两层墙体草案：编号、夹持面与物体坐标')
p.append(text(100,180,'墙体正视 XZ（含内部投影轮廓）',22))
def q(v):return (100+(v.x-215)*5.3,610-v.z*5.3)
for e in s.Edges:
 vs=e.discretize(Deflection=.01)
 for a,b in zip(vs,vs[1:]):p.append(line(q(a),q(b)))
for row in range(2):
 for col in range(3):p.append(text(100+(25+50*col)*5.3-25,610-(7+22*row)*5.3,f'L{row+1}_{col+1}',22))
p+=[line((100,300),(895,300),'#197c91',True),text(460,285,'150'),line((930,610),(930,610-47*5.3),'#197c91',True),text(945,490,'47'),text(110,660,'层距22；上层底面Z=22；各件同向，先下层后上层。',19),text(110,700,'各列底面原点X=240、290、340；Y=80；Z=0或22。',19)]
p.append(text(1050,180,'单件俯视 XY：夹持面与原点投影',21))
single=Part.Shape();single.read(str(R/'outputs/PartA_Stage1/01_CAD/P3_V2_mm.brep'))
def qt(v):return (1250+v.x*6,380-v.y*6)
for e in single.Edges:
 vs=e.discretize(Deflection=.01)
 for a,b in zip(vs,vs[1:]):p.append(line(qt(a),qt(b),'#879aa1'))
for y in [-11,11]:p.append(f'<path d="M{1250-19*6},{380-y*6}L{1250+19*6},{380-y*6}" stroke="#009eb0" stroke-width="4"/>')
p+=[line((1250,380),(1442,380),'#197c91'),text(1448,385,'+X'),line((1250,380),(1250,230),'#197c91'),text(1260,230,'+Y'),text(1258,405,'O投影'),text(1030,505,'青色：夹持面Y=±11，间距22。',18),text(1030,545,'O在底面中心，Z向上；不是质心。',18),text(1030,585,'名义TCP相对O=(0,0,14)。',18),text(1030,625,'两凸台/凹口中心X=±20，Y=0。',18),text(1030,665,'顶部凸台高3；底凹口总深3.5。',18)]
for i,t in enumerate(['结构意图：重复构件形成150×30×47的小型墙体单元，采用上下松配合定位。','单件主体50×30×22，总高25；开放夹槽38×4×12；接口详见随附剖视图。','原构件设计来自B协作基线；A完成参数化CAD、质量属性与六件交接整理，未擅自改形状。','连接局限：三列没有横向锁固、上下没有抗拔锁止；不是已验证承重或气密建筑。','本图为设计草案与数据说明；CAD几何、参数表和精确位姿JSON/CSV是数值依据。']):p.append(text(100,795+i*45,t,19))
save(p,'F01_六件墙体草案与夹持坐标')

p=start('F02  六件取料与装配目标：世界坐标和首个单件交接')
def wp(x,y):return (100+x*3,535-y*2.5)
p+=[line(wp(0,0),wp(400,0),'#197c91'),text(*wp(405,0),'+X'),line(wp(0,-170),wp(0,140),'#197c91'),text(110,175,'+Y'),text(45,560,'机器人基座O'),text(820,180,'目标区：Y=80；上下层XY重合，Z分别0/22',20)]
sources=[(210,-70),(270,-70),(330,-70),(210,-130),(270,-130),(330,-130)]
def block(x,y,c):
 px,py=wp(x-25,y+15);return f'<rect x="{px}" y="{py}" width="150" height="75" fill="{c}" fill-opacity="0.15" stroke="{c}" stroke-width="2"/>'
for i,(x,y) in enumerate(sources):
 p.append(block(x,y,'#0099a9' if i==1 else '#738b96'));px,py=wp(x,y);p.append(text(px-14,py+6,'S'+str(i+1),20));p.append(text(px-65,py+65,f'({x},{y},0)',16))
for i,x in enumerate([240,290,340]):
 p.append(block(x,80,'#0099a9' if i==1 else '#738b96'));px,py=wp(x,80);p.append(text(px-58,py+6,f'L1_{i+1}/L2_{i+1}',18));p.append(text(px-60,py-65,f'({x},80,0/22)',16))
p+=[text(350,660,'取料区：所有构件底面Z=0；姿态XYZW=(0,0,0,1)。',19),text(180,980,'首个测试：S2(270,-70,0) → L1_2(290,80,0)。',21),text(180,1020,'名义抓放TCP_Z=14；搬运/上方TCP_Z=82；工具朝下XYZW=(0,1,0,0)。',19),text(180,1060,'这是目标布局，不是已规划或已执行的运动轨迹。精确SI数据见JSON/CSV。',18)]
save(p,'F02_六件取料目标与世界坐标')
print('SIX_SUPPLEMENT_DRAWINGS_DONE')
