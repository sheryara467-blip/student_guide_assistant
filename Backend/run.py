import sys
import os

# Set path BEFORE uvicorn spawns its subprocess — this is the key fix.
# We also write the path into the environment so the subprocess inherits it.
_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)
os.environ["PYTHONPATH"] = _root

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[_root]
    )