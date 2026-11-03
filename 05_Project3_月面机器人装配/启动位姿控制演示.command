#!/bin/zsh
cd "${0:A:h}" || exit 1
./.venv/bin/python B_基础控制与雅可比/run_pose_control.py --gui --hold
