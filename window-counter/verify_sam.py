import sys
import os

try:
    print("Checking SAM imports...")
    from models import Segmenter
    import numpy as np
    import supervision as sv
    
    print("Initializing Segmenter (expecting warning if weight not found)...")
    # verification mode: don't actually load heavy weights if we don't have them
    # But we want to test the class init logic
    segmenter = Segmenter(model_path="dummy_path.pt") 
    
    if segmenter.model is None:
        print("Segmenter initialized safely (model not loaded, as expected without weights).")
    else:
        print("Segmenter initialized with model.")

    print("SAM Integration Logic Verified.")

except Exception as e:
    print(f"Verification Failed: {e}")
    import traceback
    traceback.print_exc()
