import sys
import os

try:
    print("Checking imports...")
    import torch
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    from sahi import AutoDetectionModel
    from sahi.predict import get_sliced_prediction
    print("SAHI imported successfully.")
    
    from ultralytics import YOLO
    print("Ultralytics imported successfully.")
    
    print("\nChecking CustomDetector initialization...")
    sys.path.append(os.getcwd())
    from models import CustomDetector
    
    # Initialize detector (this will try to load yolov12n.pt)
    # Ensure yolov12n.pt is in the current directory or provide path
    if os.path.exists("yolov12n.pt"):
        print("Found yolov12n.pt")
        detector = CustomDetector(model_path="yolov12n.pt")
        print("CustomDetector initialized successfully.")
    else:
        print("Warning: yolov12n.pt not found in current directory. Skipping full init.")

    print("\nVerification Passed!")

except Exception as e:
    print(f"\nVerification Failed: {e}")
    import traceback
    traceback.print_exc()
