import zipfile
import tempfile
import os
import shutil
from typing import List
from .base import FeatureExtractor

class ArchiveFeatureExtractor(FeatureExtractor):
    def extract(self, file_path: str) -> List[float]:
        # Local import to avoid circular dependency since dispatcher imports us
        from .dispatcher import extract_features 
        
        if not zipfile.is_zipfile(file_path):
            raise ValueError("Invalid ZIP archive format.")
            
        temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Scan inner files and aggregate features
            max_risk_vector = [0.0] * 2381
            
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    inner_path = os.path.join(root, file)
                    try:
                        features = extract_features(inner_path)
                        # Aggregate by taking the highest value across each feature in the archive
                        for i in range(len(max_risk_vector)):
                            if abs(features[i]) > abs(max_risk_vector[i]):
                                max_risk_vector[i] = float(features[i])
                    except Exception:
                        continue # Skip unsupported or unparseable inner files
                        
            return max_risk_vector
            
        finally:
            # Clean up extracted temporary files to prevent disk leaks
            shutil.rmtree(temp_dir, ignore_errors=True)
