import sys
import os
import traceback

print("Starting diagnosis...")

try:
    print("Attempting to import main module...")
    # This will trigger the global initialization in main.py
    import main
    print("Successfully imported main.")
    
    print("Checking app instance...")
    if hasattr(main, 'app'):
        print("FastAPI app instance found.")
    else:
        print("ERROR: 'app' not found in main.")
        
    print("Diagnosis complete. The backend code seems to initialize correctly.")
    print("If you still see connection errors, check:")
    print("1. If 'uvicorn' is actually running.")
    print("2. If port 8000 is occupied by another process.")
    print("3. Firewall settings.")

except ImportError as e:
    print(f"ImportError during diagnosis: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Exception during diagnosis: {e}")
    traceback.print_exc()
