from abc import ABC, abstractmethod
import torch
import numpy as np
from PIL import Image
import supervision as sv
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor
from groundingdino.util.inference import load_model, load_image, predict, annotate

class WindowDetector(ABC):
    @abstractmethod
    def detect(self, image: Image.Image, text_prompt: str = None, conf_threshold: float = 0.3) -> sv.Detections:
        pass

class ZeroShotDetector(WindowDetector):
    def __init__(self, config_path: str = None, weights_path: str = None):
        # Placeholder for GroundingDINO loading. 
        # In a real scenario, you'd point to the config and weight files.
        # For SAHI, we typically use the AutoDetectionModel wrapper.
        pass

    def detect(self, image: Image.Image, text_prompt: str = "window", conf_threshold: float = 0.3) -> sv.Detections:
        # NOTE: This is a simplified implementation structure. 
        # SAHI requires a specific model wrapper for GroundingDINO or uses the 'huggingface' integration.
        # For this boilerplate, we'll demonstrate the SAHI slicing call structure.
        
        # In production, you would initialize the SAHI model wrapper here or in __init__
        # detection_model = AutoDetectionModel.from_pretrained(
        #    model_type='grounding_dino',
        #    model_path=...,
        #    config_path=...,
        #    confidence_threshold=conf_threshold,
        #    device="cuda" if torch.cuda.is_available() else "cpu"
        # )
        
        # result = get_sliced_prediction(
        #     image,
        #     detection_model,
        #     slice_height=640,
        #     slice_width=640,
        #     overlap_height_ratio=0.2,
        #     overlap_width_ratio=0.2
        # )
        
        # For now, returning specific dummy structure to allow the rest of the app to build
        # untill weights are actually downloaded.
        
        return sv.Detections.empty() 

class CustomDetector(WindowDetector):
    def __init__(self, model_path: str = "yolov12n.pt"):
        self.model_path = model_path
        # self.model = YOLO(model_path) # Auto-downloads if not present

    def detect(self, image: Image.Image, text_prompt: str = None, conf_threshold: float = 0.3) -> sv.Detections:
        # SAHI Integration
        # We use 'yolov8' as the model_type because SAHI uses this key to wrap the Ultralytics YOLO interface,
        # which handles v8, v11, v12 etc.
        detection_model = AutoDetectionModel.from_pretrained(
            model_type='yolov8',
            model_path=self.model_path,
            confidence_threshold=conf_threshold,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
        result = get_sliced_prediction(
            image,
            detection_model,
            slice_height=640,
            slice_width=640,
            overlap_height_ratio=0.2,
            overlap_width_ratio=0.2
        )
        
        # Convert SAHI prediction to Supervision Detections
        xyxy = []
        conf = []
        class_ids = []
        
        for prediction in result.object_prediction_list:
            # SAHI bbox is [minx, miny, maxx, maxy] for to_xyxy()
            xyxy.append(prediction.bbox.to_xyxy())
            conf.append(prediction.score.value)
            class_ids.append(prediction.category.id)
            
        if not xyxy:
            return sv.Detections.empty()
            
        return sv.Detections(
            xyxy=np.array(xyxy),
            confidence=np.array(conf),
            class_id=np.array(class_ids)
        )

class Segmenter:
    def __init__(self, model_path="sam2_b.pt"): # Defaulting to sam2_b.pt (Base) which is supported
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Ultralytics supports SAM models via the SAM class (wrapper around their engine)
        try:
            from ultralytics import SAM
            self.model = SAM(model_path)
            # self.model.to(self.device) # Ultralytics handles device internally usually during predict
        except Exception as e:
            print(f"Error loading Ultralytics SAM: {e}")
            self.model = None

    def predict_masks(self, image: Image.Image, detections: sv.Detections) -> sv.Detections:
        if self.model is None or len(detections) == 0:
            return detections

        # Ultralytics SAM expects prompts. 
        # We can pass bounding boxes as prompts.
        bboxes = detections.xyxy
        
        # Run inference
        # The Ultralytics SAM API typically accepts 'bboxes' argument for prompting
        results = self.model(image, bboxes=bboxes, verbose=False)
        
        # Extract masks
        # results[0].masks.data contains the masks
        if results[0].masks is not None:
            # Convert to numpy boolean masks
            # masks shape: (N, H, W)
            generated_masks = results[0].masks.data.cpu().numpy().astype(bool)
            
            # Ensure the number of masks matches detections. 
            # SAM might return multiple masks per box or none. 
            # We assume 1-to-1 if prompt was boxes.
            if len(generated_masks) == len(detections):
                detections.mask = generated_masks
            else:
                print(f"Warning: Mask count ({len(generated_masks)}) != Box count ({len(detections)})")
                
        return detections
