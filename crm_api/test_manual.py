#!/usr/bin/env python
"""Manual test runner to debug import issues."""

import sys
from pathlib import Path

# Add to path like conftest does
sys.path.insert(0, str(Path(__file__).parent))

print("Python executable:", sys.executable)
print("sys.path:", sys.path[:3])

try:
    print("\n1. Importing fastapi...")
    import fastapi
    print(f"   SUCCESS - FastAPI {fastapi.__version__} from {fastapi.__file__}")
except Exception as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

try:
    print("\n2. Importing fast API.exceptions...")
    from fastapi.exceptions import RequestValidationError, HTTPException
    print(f"   SUCCESS")
except Exception as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

try:
    print("\n3. Importing starlette.responses...")
    from starlette.responses import JSONResponse
    print(f"   SUCCESS")
except Exception as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

try:
    print("\n4. Importing app.middleware.error_handler...")
    from app.middleware.error_handler import RequestIDMiddleware, ErrorHandlerMiddleware
    print(f"   SUCCESS")
except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n5. Importing app.main...")
    from app.main import create_app
    print(f"   SUCCESS")
except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")
