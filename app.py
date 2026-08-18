import importlib.util
import sys
import os

_vf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viral_finder")
sys.path.insert(0, _vf_dir)

# 用 importlib 取代 exec()，安全地載入 app 模組
_spec = importlib.util.spec_from_file_location(
    "viral_finder.app",
    os.path.join(_vf_dir, "app.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_mod.__file__ = os.path.join(_vf_dir, "app.py")
_spec.loader.exec_module(_mod)
