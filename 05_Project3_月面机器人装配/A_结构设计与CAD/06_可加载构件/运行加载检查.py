"""Load-only verification for B/C; no robot or grasp execution."""
from pathlib import Path
import argparse,json,sys,shutil,tempfile,traceback,time
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='仅加载A候选构件，不修改当前C装配参数')
parser.add_argument('--output',type=Path,default=ROOT.parents[1]/'运行验证/A_模型加载'/time.strftime('%Y%m%d_%H%M%S')/'loading_result_LOCAL.json')
args=parser.parse_args()
report={'test':'single component URDF load only','robot_grasp_executed':False}
try:
 import pybullet as p
 from importlib.metadata import version
 report['pybullet_version']=version('pybullet')
 cache=Path(tempfile.mkdtemp(prefix='p3_A_six_load_'))
 shutil.copytree(ROOT,cache/'model',dirs_exist_ok=True)
 client=p.connect(p.DIRECT)
 body=p.loadURDF(str(cache/'model/component_V2_provisional.urdf'),basePosition=[.270,-.070,0],baseOrientation=[0,0,0,1],flags=p.URDF_USE_INERTIA_FROM_FILE,physicsClientId=client)
 p.changeDynamics(body,-1,collisionMargin=.00005,lateralFriction=.6,restitution=0,physicsClientId=client)
 info=p.getDynamicsInfo(body,-1,physicsClientId=client)
 shapes=p.getCollisionShapeData(body,-1,physicsClientId=client)
 pos,quat=p.getBasePositionAndOrientation(body,physicsClientId=client)
 rot=p.getMatrixFromQuaternion(quat)
 offset=info[3]
 bottom=[pos[i]-sum(rot[i*3+j]*offset[j] for j in range(3)) for i in range(3)]
 report.update(status='passed',mass_kg=info[0],inertia_diagonal_kg_m2=list(info[2]),local_inertial_offset_m=list(offset),collision_parts=len(shapes),base_COM_world_m=list(pos),derived_bottom_world_m=bottom,cache_path=str(cache))
 assert p.getNumJoints(body,physicsClientId=client)==0
 assert len(shapes)==34
 assert abs(info[0]-.07260666666666667)<1e-9
 assert max(abs(a-b) for a,b in zip(bottom,[.270,-.070,0]))<1e-6
 p.disconnect(client)
except Exception as e:
 report.update(status='not_passed',error=str(e),detail=traceback.format_exc())
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
sys.exit(0 if report.get('status')=='passed' else 1)
