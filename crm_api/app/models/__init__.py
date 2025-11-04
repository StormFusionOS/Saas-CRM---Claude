"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

Models Package - Unified imports from both old models.py and new subdirectory modules
"""

# Import everything from the old models.py file (one level up, then models.py)
# This allows `from app.models import User, Contact, etc.` to work
import sys
import os

# Add parent directory to path to import from sibling models.py file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from the standalone models.py file
# We need to import it with a different module name to avoid circular import
import importlib.util
spec = importlib.util.spec_from_file_location(
    "app_models_file",
    os.path.join(os.path.dirname(__file__), "..", "models.py")
)
models_file = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_file)

# Re-export everything from models.py
for name in dir(models_file):
    if not name.startswith('_'):
        globals()[name] = getattr(models_file, name)

# The subdirectory modules can now be imported normally via:
# from app.models.consent import ...
# from app.models.context_pack import ...
# etc.
