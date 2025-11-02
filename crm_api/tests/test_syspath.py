import sys

def test_syspath():
    print("\n\nPython executable:", sys.executable)
    print("\nsys.path:")
    for p in sys.path:
        print(f"  {p}")

    # Try importing fastapi
    try:
        import fastapi
        print(f"\nFastAPI version: {fastapi.__version__}")
        print(f"FastAPI location: {fastapi.__file__}")
    except Exception as e:
        print(f"\nFailed to import fastapi: {e}")

    # Try importing fastapi.responses
    try:
        from fastapi import responses
        print(f"fastapi.responses module: {responses}")
    except Exception as e:
        print(f"\nFailed to import fastapi.responses: {e}")
