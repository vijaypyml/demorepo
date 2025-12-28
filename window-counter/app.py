import streamlit as st
import requests
from PIL import Image
import io
import base64

# Configuration
API_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="Project Antigravity", layout="wide")

st.title("Project Antigravity: Aerial Window Counter")
st.markdown("Modular detection with **Grounding DINO** (Zero-Shot) and **YOLO** (Custom), plus **SAM** segmentation.")

# Sidebar
with st.sidebar:
    st.header("Control Panel")
    
    model_choice = st.selectbox(
        "Detection Model",
        ["Zero-Shot (Grounding DINO)", "Custom (YOLOv11)"]
    )
    
    model_type_key = "zero_shot" if "Zero-Shot" in model_choice else "custom"
    
    text_prompt = "window"
    if model_type_key == "zero_shot":
        text_prompt = st.text_input("Text Prompt", value="window . glass . frame")
        st.caption("Use dot notation for classes.")
        
    confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.3, 0.05)
    
    use_sam = st.toggle("Enable SAM Segmentation", value=False)

# Main Area
col1, col2 = st.columns(2)

uploaded_file = st.file_uploader("Upload Aerial Image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Display Original
    image_bytes = uploaded_file.getvalue()
    original_image = Image.open(io.BytesIO(image_bytes))
    
    with col1:
        st.subheader("Original Image")
        st.image(original_image, use_container_width=True)
    
    # Predict Button
    if st.button("Run Detection", type="primary"):
        with st.spinner("Processing... (Slicing & Inference)"):
            try:
                files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
                data = {
                    "model_type": model_type_key,
                    "text_prompt": text_prompt,
                    "confidence": confidence,
                    "use_sam": use_sam
                }
                
                response = requests.post(API_URL, files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    count = result["count"]
                    b64_img = result["annotated_image"]
                    
                    # Decode image
                    img_data = base64.b64decode(b64_img)
                    annotated_pil = Image.open(io.BytesIO(img_data))
                    
                    with col2:
                        st.subheader("Analysis Result")
                        st.image(annotated_pil, use_container_width=True)
                        st.metric("Windows Detected", count)
                        
                        # Export Options
                        st.divider()
                        st.subheader("Export Results")
                        
                        raw_boxes = result.get("raw_boxes", [])
                        
                        if raw_boxes:
                            # JSON Export
                            import json
                            json_str = json.dumps(raw_boxes, indent=2)
                            st.download_button(
                                label="Download Bounds (JSON)",
                                data=json_str,
                                file_name="bounds.json",
                                mime="application/json"
                            )
                            
                            # CSV Export
                            import pandas as pd
                            df = pd.DataFrame(raw_boxes, columns=["x_min", "y_min", "x_max", "y_max"])
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download Bounds (CSV)",
                                data=csv,
                                file_name="bounds.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("No detections to export.")
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")
                st.warning("Ensure the FastAPI backend is running on port 8000.")
