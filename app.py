import sys
import os

_vf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viral_finder")
sys.path.insert(0, _vf_dir)

exec(
    open(os.path.join(_vf_dir, "app.py")).read(),
    {"__file__": os.path.join(_vf_dir, "app.py"), "__name__": "__main__"},
)
