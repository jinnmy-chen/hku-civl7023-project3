# HKU CIVL 7023 · Project 3

月面构件设计与 PiPER 机械臂装配：槽榫构件 CAD、六轴运动学／雅可比、辅助抓放、路径规划，以及16件两层八边形装配仿真。

**直接下载：[项目 ZIP](https://github.com/yhdhhhhuk/hku-civl7023-project3/archive/refs/heads/main.zip)**。也可以在本页点击 **Code → Download ZIP**，或克隆：

```bash
git clone https://github.com/yhdhhhhuk/hku-civl7023-project3.git
```

## 项目内容

| 目录 | 内容 |
|---|---|
| [A：结构设计与CAD](05_Project3_月面机器人装配/A_结构设计与CAD/) | 单件／六件／16件原生CAD、STEP、网格、图纸、候选质量惯量与建模源码 |
| [B：关节与夹爪](05_Project3_月面机器人装配/B_关节与夹爪/) | 六轴与双指控制、关节映射、名义TCP |
| [B：运动学与雅可比](05_Project3_月面机器人装配/B_基础控制与雅可比/) | URDF正运动学、6×6雅可比、阻尼IK与基础反馈控制 |
| [B：构件与工作空间](05_Project3_月面机器人装配/B_工作空间与设计约束/) | 槽榫V2模型、34凸分块、几何与可达性程序 |
| [C：当前装配入口](05_Project3_月面机器人装配/C_仿真与装配/) | 16件预置料盘、五次轨迹／RRT-Connect、接触门控抓取及释放 |
| [PiPER资源](05_Project3_月面机器人装配/PiPER_Load_URDF/) | 项目使用的原始URDF与网格 |
| [最新已验证结果](05_Project3_月面机器人装配/运行验证/C_释放修复_2026-11-02/修复后从头16件_v4/) | 原始CSV、结果、物理视频、释放诊断和源码快照 |

课程原始PDF、个人环境、缓存、历史来包与旧试验归档保留在本地，不包含在此下载中。历史技术说明可能引用这些本地材料；跨电脑运行请以本README为准。

完整下载内容见[仓库文件清单](仓库文件清单.md)。

## 安装环境

使用 **Python 3.12**。下载解压后进入项目子目录，建议将外层解压目录设为简短路径。

Windows PowerShell：

```powershell
cd .\05_Project3_月面机器人装配
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

macOS／Linux：

```bash
cd 05_Project3_月面机器人装配
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

PyBullet在部分Python／平台组合上需要源码编译。Windows需要C++构建工具；macOS需要Xcode命令行工具。若本Mac出现`fdopen`相关编译错误，先激活上述环境，再按已验证的兼容方式安装：

```bash
CPPFLAGS='-Dfdopen=fdopen' .venv/bin/python -m pip install --no-build-isolation pybullet==3.2.7
```

若已出现缺少PyBullet的安装错误，完成兼容安装后重新执行`pip install -r requirements.txt`补齐其他依赖。仓库不附带作者电脑的`.venv`。

## 运行

先跑一件：场景中仍有全部16件，其余15件参与碰撞检查。

Windows：

```powershell
.\.venv\Scripts\python.exe C_仿真与装配/run_preloaded_tray_assembly_fast.py --gui --limit 1
```

macOS／Linux：

```bash
.venv/bin/python C_仿真与装配/run_preloaded_tray_assembly_fast.py --gui --limit 1
```

去掉`--limit 1`运行完整16件，加`--video`保存本次真实物理录像；去掉`--gui`可无界面运行。计算耗时可能显著长于仿真时间。结果自动写入项目`运行验证/C_装配运行/日期时间/`，网格缓存自动重建。

建好环境后，Windows也可双击[启动C装配演示.cmd](05_Project3_月面机器人装配/启动C装配演示.cmd)，macOS双击[启动C装配演示.command](05_Project3_月面机器人装配/启动C装配演示.command)。

汇总某次新运行的CSV／JSON：

```bash
.venv/bin/python C_仿真与装配/summarize_preloaded_tray.py 运行验证/C_装配运行/实际输出目录
```

Windows将上述`.venv/bin/python`替换为`.\.venv\Scripts\python.exe`。

## CAD与参数

单件原点是底面中心，STEP及`mm`网格为毫米，`m`网格和URDF为米。完整外形50×30×25mm，层距22mm；凹槽碰撞必须保留34凸分块。

当前已验证C装配使用每件70g、COM_Z=11mm及包络惯量。A另提供72.6067g、COM_Z≈10.5663mm及按实际实体计算的候选惯量，尚未替换当前仿真。原六件直墙资料保留作基线；当前流程是16件八边形。打开CAD需要相应CAD软件，运行仿真不需要安装CAD应用。

## 已验证范围

2026年11月2日本机最新修复版一次从零完成16/16件、96个运动目标，无检查点续跑：最大最终构件误差0.8226mm／0.2878°，定义外碰撞记录0，19个场景物体全程保持恒定。证据为仓库中的[物理视频](05_Project3_月面机器人装配/运行验证/C_释放修复_2026-11-02/修复后从头16件_v4/assembly.mp4)、[逐件误差](05_Project3_月面机器人装配/运行验证/C_释放修复_2026-11-02/修复后从头16件_v4/final_errors.csv)和[修复说明](05_Project3_月面机器人装配/运行验证/C_释放修复_2026-11-02/修复说明与验证.md)。这是原环境的运行结果，其他电脑仍需自行复现。

当前使用双指接触门控的辅助固定约束；材料／惯量仍临时，实际六轴关节力矩未完整记录，转角侧连接和结构稳定性待完善。离散碰撞检查结果与内部误差门槛不等同课程官方评分标准或结构安全认证。
