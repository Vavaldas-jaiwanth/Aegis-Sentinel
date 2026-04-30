import os
import warnings
from .features import extract_features
from .model_loader import get_model

# Suppress sklearn warnings about feature names since we pass raw vectors directly
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

def scan_file(file_path: str, explain: bool = False) -> dict:
    """
    Scans a single PE file and returns a prediction dict.
    Optionally returns a SHAP explanation of the features if explain=True.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
        
    try:
        # 1. Extract Features
        features_vector = extract_features(file_path)
        
        # 2. Load Model (will only load from disk on first call)
        model = get_model('ember_model_2018.txt')
        
        # 3. Predict
        # LightGBM Booster.predict() natively returns an array of probabilities, not classes
        import numpy as np
        probabilities = model.predict(np.array([features_vector]))
        malware_prob = float(probabilities[0])
        
        # The EMBER 2018 model's mathematically optimal threshold for a 1% False Positive Rate is 0.8336
        is_malicious = malware_prob >= 0.8336
        
        # Normalize the confidence score for display
        confidence_score = malware_prob if is_malicious else (1.0 - malware_prob)
        
        result = {
            "label": "malicious" if is_malicious else "safe",
            "score": round(confidence_score, 4)
        }
        
        # 4. Explain (Optional)
        # We only compute SHAP if explicitly asked to keep standard scans lightning fast
        if explain:
            from .explain import explain_prediction
            explanation = explain_prediction(features_vector, model)
            if "error" not in explanation:
                result["explanation"] = explanation["top_features"]
            else:
                result["explanation_error"] = explanation["error"]
                
        return result
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test script pointing to the sample file in the parent directory
    sample_file = "../boy.exe"
    
    print(f"Scanning {sample_file} with explanation...\n")
    result = scan_file(sample_file, explain=True)
    
    import json
    print(json.dumps(result, indent=2))

