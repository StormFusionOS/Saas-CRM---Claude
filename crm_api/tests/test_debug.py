"""Debug test to understand pytest environment."""
import sys

def test_debug_python():
    """Print debug info about Python environment."""
    print("\n\nPython executable:", sys.executable)
    print("\nsys.path:")
    for i, p in enumerate(sys.path):
        print(f"  [{i}] {p}")

    print("\n\nTrying import fastapi...")
    try:
        import fastapi
        print(f"  ✓ fastapi {fastapi.__version__} from {fastapi.__file__}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    print("\n\nTrying import fastapi.exceptions...")
    try:
        import fastapi.exceptions
        print(f"  ✓ fastapi.exceptions from {fastapi.exceptions.__file__}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    print("\n\nChecking fastapi module contents...")
    try:
        import fastapi
        print(f"  Has 'exceptions' attr: {hasattr(fastapi, 'exceptions')}")
        if hasattr(fastapi, 'exceptions'):
            print(f"  fastapi.exceptions type: {type(fastapi.exceptions)}")
    except Exception as e:
        print(f"  ✗ FAILED: {e}")
