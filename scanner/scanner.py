import os
from features import extract_features
from model_loader import get_model

def scan_file(file_path: str) -> dict:
    """
    Scans a single PE file and returns a prediction dict.
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
        
    try:
        # 1. Extract Features
        features_vector = extract_features(file_path)
        
        # 2. Load Model (will only load from disk on first call)
        model = get_model('model.pkl')
        
        # 3. Predict
        # Using predict_proba to get the confidence score
        probabilities = model.predict_proba([features_vector])[0]
        prediction = model.predict([features_vector])[0]
        
        # In our dataset, 0 = safe (legitimate), 1 = malicious
        is_malicious = (prediction != 0)
        
        # Get the confidence score for the predicted class
        confidence_score = float(probabilities[1] if is_malicious else probabilities[0])
        
        return {
            "label": "malicious" if is_malicious else "safe",
            "score": round(confidence_score, 4)
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test script pointing to the sample file in the parent directory
    sample_file = "../boy.exe"
    
    print(f"Scanning {sample_file}...")
    result = scan_file(sample_file)
    print("Result:", result)
