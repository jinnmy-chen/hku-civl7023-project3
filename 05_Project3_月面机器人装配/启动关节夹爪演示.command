#!/bin/zsh
cd -- "${0:A:h}" || exit 1
exec .venv/bin/python -u B_关节与夹爪/demo_joints.py
