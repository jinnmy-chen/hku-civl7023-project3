#!/bin/zsh
cd -- "${0:A:h}" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  print '项目虚拟环境不存在，请先按环境配置说明建立环境。'
  exit 1
fi
exec .venv/bin/python -u PiPER_Load_URDF/demo_load_urdf.py
