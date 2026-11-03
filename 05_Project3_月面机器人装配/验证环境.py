"""Verify the supplied PiPER model without opening a desktop window."""

from datetime import datetime
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import struct
import sys
import zlib

import numpy as np
import pybullet as p


ROOT = Path(__file__).resolve().parent
MODEL = ROOT / "PiPER_Load_URDF/piper_description/piper_description_pybullet.urdf"
OUTPUT = ROOT / "运行验证"


def save_png(path, rgb):
    """Write a rendered RGB frame using only Python's standard library."""
    height, width, _ = rgb.shape

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + row.tobytes() for row in rgb)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def main():
    OUTPUT.mkdir(exist_ok=True)
    client = p.connect(p.DIRECT)
    if client < 0:
        raise RuntimeError("PyBullet DIRECT connection failed")
    try:
        robot = p.loadURDF(str(MODEL), useFixedBase=True)
        joints = []
        for index in range(p.getNumJoints(robot)):
            info = p.getJointInfo(robot, index)
            joints.append({
                "index": index, "name": info[1].decode(),
                "type": info[2], "lower": info[8], "upper": info[9],
                "link": info[12].decode(),
            })
        assert sum(j["type"] == p.JOINT_REVOLUTE for j in joints) == 6
        assert sum(j["type"] == p.JOINT_PRISMATIC for j in joints) == 2
        # Zero gravity checks stepping only, not lunar dynamics or manipulation.
        p.setGravity(0, 0, 0)
        for _ in range(120):
            p.stepSimulation()
        assert all(math.isfinite(p.getJointState(robot, j["index"])[0]) for j in joints)
        view = p.computeViewMatrixFromYawPitchRoll([0.25, 0.02, 0.10], 0.78, 42, -30, 0, 2)
        projection = p.computeProjectionMatrixFOV(50, 960 / 720, 0.01, 10)
        camera = p.getCameraImage(960, 720, view, projection, renderer=p.ER_TINY_RENDERER)
        segmentation = np.asarray(camera[4]).reshape(720, 960)
        pixels = int(np.count_nonzero(segmentation >= 0))
        assert pixels > 1000, "Rendered model is missing or too small"
        rgb = np.asarray(camera[2], dtype=np.uint8).reshape(720, 960, 4)[:, :, :3]
        save_png(OUTPUT / "PiPER_模型预览.png", rgb)
        result = {
            "status": "PASS", "checked_at_local": datetime.now().astimezone().isoformat(),
            "python": sys.version, "python_executable": sys.executable,
            "base_python": sys.base_prefix, "system": platform.platform(),
            "architecture": platform.machine(),
            "packages": {name: version(name) for name in ["pybullet", "numpy"]},
            "model": str(MODEL.relative_to(ROOT)), "joints": joints,
            "simulation_steps": 120, "test_gravity": [0, 0, 0],
            "rendered_robot_pixels": pixels,
            "preview": "PiPER_模型预览.png", "gui_verified": False,
            "scope": "Import, URDF load, joint structure, finite state after stepping, CPU render. No grasp or assembly test.",
        }
        (OUTPUT / "环境验证结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        p.disconnect(client)


def run_original_gui():
    """Run the unchanged example and save a frame from its OpenGL context."""
    import runpy

    OUTPUT.mkdir(exist_ok=True)
    original_camera = p.resetDebugVisualizerCamera

    def verify_camera(*args, **kwargs):
        original_camera(*args, **kwargs)
        # Use the requested camera directly: the GUI update is asynchronous.
        view = p.computeViewMatrixFromYawPitchRoll(
            kwargs["cameraTargetPosition"], kwargs["cameraDistance"],
            kwargs["cameraYaw"], kwargs["cameraPitch"], 0, 2,
        )
        projection = p.computeProjectionMatrixFOV(50, 960 / 720, 0.01, 10)
        frame = p.getCameraImage(
            960, 720, view, projection,
            renderer=p.ER_BULLET_HARDWARE_OPENGL,
        )
        rgb = np.asarray(frame[2], dtype=np.uint8).reshape(720, 960, 4)[:, :, :3]
        save_png(OUTPUT / "PiPER_GUI渲染.png", rgb)
        record_path = OUTPUT / "环境验证结果.json"
        result = json.loads(record_path.read_text()) if record_path.exists() else {}
        result["gui_hardware_frame_saved"] = True
        result["gui_frame"] = "PiPER_GUI渲染.png"
        result["gui_frame_generated_at"] = datetime.now().astimezone().isoformat()
        record_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print("Original GUI example OpenGL frame saved.", flush=True)

    p.resetDebugVisualizerCamera = verify_camera
    try:
        runpy.run_path(str(ROOT / "PiPER_Load_URDF/demo_load_urdf.py"), run_name="__main__")
    finally:
        p.resetDebugVisualizerCamera = original_camera


if __name__ == "__main__":
    if "--gui" in sys.argv:
        run_original_gui()
    else:
        main()
