import shap
import numpy as np

def get_ember_feature_name(index: int) -> str:
    """
    Maps an EMBER 2018 feature index (0 to 2380) to its human-readable security category.
    """
    if 0 <= index < 256:
        return f"Byte Histogram (Raw Bytes) [Idx: {index}]"
    elif 256 <= index < 512:
        return f"Byte Entropy (Obfuscation/Packing) [Idx: {index}]"
    elif 512 <= index < 616:
        return f"String Properties (Embedded Text) [Idx: {index}]"
    elif 616 <= index < 626:
        return f"General File Info (Size/Layout) [Idx: {index}]"
    elif 626 <= index < 688:
        return f"Header Info (Timestamps/Architecture) [Idx: {index}]"
    elif 688 <= index < 943:
        return f"Section Properties (Code/Data Segments) [Idx: {index}]"
    elif 943 <= index < 2223:
        return f"Imports (API Calls/Dependencies) [Idx: {index}]"
    elif 2223 <= index < 2351:
        return f"Exports (Exposed Functions) [Idx: {index}]"
    elif 2351 <= index < 2381:
        return f"Data Directories (Resources/Certificates) [Idx: {index}]"
    else:
        return f"Unknown Feature [Idx: {index}]"

def explain_prediction(features: list, model) -> dict:
    """
    Uses SHAP to explain why the LightGBM model made its prediction across 2381 features.
    Returns the top contributing feature categories and their impact scores.
    """
    try:
        # We use TreeExplainer because it is highly optimized for LightGBM
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values for the single input feature vector
        shap_values_raw = explainer.shap_values(np.array([features]))
        
        # Handle different SHAP output formats (binary classification vs regression)
        if isinstance(shap_values_raw, list):
            # Binary classification usually returns a list [class_0_shap, class_1_shap]
            shap_values = shap_values_raw[1][0]
        elif len(shap_values_raw.shape) == 3:
             # Some newer shap versions output (n_samples, n_features, n_classes)
             shap_values = shap_values_raw[0, :, 1]
        else:
            # Single array output
            shap_values = shap_values_raw[0]
            
        # Dynamically map the highest impact indices
        feature_impacts = []
        for i, impact in enumerate(shap_values):
            if impact != 0:
                feature_impacts.append({
                    "feature": get_ember_feature_name(i),
                    "impact": round(float(impact), 4),
                    "absolute_impact": abs(float(impact))
                })
            
        # Sort by highest absolute impact (positive pushes towards malicious, negative pushes towards safe)
        feature_impacts.sort(key=lambda x: x["absolute_impact"], reverse=True)
        
        # Return top 5 most critical features driving the AI's decision
        top_features = [{"feature": f["feature"], "impact": f["impact"]} for f in feature_impacts[:5]]
        
        return {"top_features": top_features}
        
    except Exception as e:
        return {"error": f"Failed to generate EMBER explanation: {str(e)}"}
