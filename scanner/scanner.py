import os
import warnings
import zipfile
import tempfile
import shutil
from .features import extract_features
from .model_loader import get_model

# Suppress sklearn warnings about feature names since we pass raw vectors directly
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

def _scan_single_pe(file_path: str, explain: bool = False) -> dict:
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
        "score": round(confidence_score, 4),
        "raw_prob": malware_prob
    }
    
    # 4. Explain (Optional)
    if explain:
        from .explain import explain_prediction
        explanation = explain_prediction(features_vector, model)
        if "error" not in explanation:
            result["explanation"] = explanation["top_features"]
        else:
            result["explanation_error"] = explanation["error"]
            
    return result

def scan_file(file_path: str, explain: bool = False) -> dict:
    """
    Scans a single PE file or a ZIP archive containing PE files.
    Returns a prediction dict.
    Optionally returns a SHAP explanation of the features if explain=True.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
        
    try:
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.zip':
            if not zipfile.is_zipfile(file_path):
                return {"error": "Invalid ZIP archive format."}
                
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                highest_prob = -1.0
                worst_result = None
                
                # Scan inner PE files
                pe_extensions = ['.exe', '.dll', '.sys']
                pe_found = False
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        inner_path = os.path.join(root, file)
                        _, inner_ext = os.path.splitext(inner_path.lower())
                        if inner_ext in pe_extensions:
                            pe_found = True
                            try:
                                res = _scan_single_pe(inner_path, explain=explain)
                                if "error" not in res:
                                    if res["raw_prob"] > highest_prob:
                                        highest_prob = res["raw_prob"]
                                        worst_result = res
                            except Exception:
                                continue
                                
                if worst_result is not None:
                    # Clean up raw_prob before returning
                    del worst_result["raw_prob"]
                    return worst_result
                elif pe_found:
                    return {"error": "Failed to extract features from any PE file within the archive."}
                else:
                    return {"label": "safe", "score": 1.0, "message": "No executable files found in archive."}
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        elif ext in ['.exe', '.dll', '.sys']:
            res = _scan_single_pe(file_path, explain=explain)
            if "raw_prob" in res:
                del res["raw_prob"]
            return res
        else:
            return {"error": f"Unsupported file type: {ext}"}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test script pointing to the sample file in the parent directory
    sample_file = "../boy.exe"
    
    print(f"Scanning {sample_file} with explanation...\n")
    result = scan_file(sample_file, explain=True)
    
    import json
    print(json.dumps(result, indent=2))
