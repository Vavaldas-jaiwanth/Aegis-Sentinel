import os
from typing import List
from .pe_features import PEFeatureExtractor

def extract_features(file_path: str) -> List[float]:
    """
    Detects file type based on extension and dynamically routes it to the correct feature extractor.
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.exe', '.dll', '.sys']:
        extractor = PEFeatureExtractor()
    else:
        raise ValueError(f"Unsupported file type for feature extraction: {ext}")
        
    return extractor.extract(file_path)
