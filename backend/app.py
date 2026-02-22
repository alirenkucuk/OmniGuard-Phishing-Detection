from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import torch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cpp_engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml_core')))
import url_engine
from models import OmniGuardNet

app = FastAPI(title="OmniGuard Inference API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

# 1. Start by initializing the C++ feature extraction engine
engine = url_engine.FeatureExtractor()

# 2. Load the trained PyTorch model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = OmniGuardNet(tabular_feature_dim=2).to(device)

try:
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ml_core', 'saved_models', 'omniguard_best.pth'))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval() # Get the model ready for inference
    print("[+] OmniGuard Neural Network loaded successfully!")
except Exception as e:
    print(f"[-] CRITICAL ERROR: Could not load model weights! {e}")

@app.post("/api/v1/analyze")
async def analyze_url(request: URLRequest):
    try:
        # Step 1: Get URL features from the C++ engine
        features_map = engine.extract_url_features(request.url)
        features_list = [features_map.get("length", 0.0), features_map.get("entropy", 0.0)]
        tabular_tensor = torch.tensor([features_list], dtype=torch.float32).to(device)
        
        # Step 2: Create a dummy image tensor (since our model expects both image and tabular data)
        image_tensor = torch.zeros((1, 3, 224, 224)).to(device)
        
        # Step 3: Guess the risk score using the neural network
        with torch.no_grad():
            output = model(image_tensor, tabular_tensor)
            risk_score = output.item()
            
        is_phishing = risk_score > 0.5

        return {
            "target_url": request.url,
            "risk_score": round(risk_score, 4),
            "is_phishing": is_phishing,
            "message": "🚨 Phishing Threat Detected!" if is_phishing else "✅ Site appears legitimate."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))