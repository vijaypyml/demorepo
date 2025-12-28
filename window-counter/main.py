from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
import numpy as np
import supervision as sv
from typing import List, Optional
import cv2

# Import our models
from models import ZeroShotDetector, CustomDetector, Segmenter

app = FastAPI(title="Project Antigravity API")

# Initialize models (lazy loading recommended in production, but here we init key wrappers)
# Real implementation would manage model persistence to avoid reloading per request if possible, 
# or use a dependency injection pattern.
zero_shot_detector = ZeroShotDetector()
custom_detector = CustomDetector()
segmenter = Segmenter()

@app.post("/predict")
async def predict_windows(
    file: UploadFile = File(...),
    model_type: str = Form("zero_shot"), # 'zero_shot' or 'custom'
    text_prompt: str = Form("window"),
    confidence: float = Form(0.3),
    use_sam: bool = Form(False)
):
    try:
        # Read Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Detection
        detections = sv.Detections.empty()
        
        if model_type == "zero_shot":
            detections = zero_shot_detector.detect(image, text_prompt=text_prompt, conf_threshold=confidence)
        elif model_type == "custom":
            detections = custom_detector.detect(image, conf_threshold=confidence)
        else:
            raise HTTPException(status_code=400, detail="Invalid model_type. Use 'zero_shot' or 'custom'.")

        # Segmentation (Optional)
        masks_list = []
        if use_sam and len(detections) > 0:
            detections = segmenter.predict_masks(image, detections)
            # Encode masks if necessary, or just rely on xyxy for basic viz in prototype
            if detections.mask is not None:
                # Convert boolean masks to list for JSON serialization if needed,
                # but sending simplified data or returning an annotated image is often better for MVP.
                pass

        # Annotate Image for Frontend Display
        # We can implement a helper to annotate and return the base64 string
        annotated_image = np.array(image)
        
        # Box Annotator
        box_annotator = sv.BoxAnnotator()
        annotated_image = box_annotator.annotate(scene=annotated_image, detections=detections)
        
        # Mask Annotator if masks exist
        if detections.mask is not None:
            mask_annotator = sv.MaskAnnotator()
            annotated_image = mask_annotator.annotate(scene=annotated_image, detections=detections)

        # Convert back to base64
        pil_annotated = Image.fromarray(annotated_image)
        buffered = io.BytesIO()
        pil_annotated.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return JSONResponse(content={
            "count": len(detections),
            "annotated_image": img_str,
            "raw_boxes": detections.xyxy.tolist() if len(detections) > 0 else []
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
