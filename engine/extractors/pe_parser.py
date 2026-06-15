import os
import numpy as np
from typing import List
from engine.extractors.base import FeatureExtractor

class PEFeatureExtractor(FeatureExtractor):
    def extract(self, file_path: str) -> List[float]:
        try:
            import lief
            # LIEF 0.17+ removed several exception classes that EMBER 2018 hardcoded.
            # We dynamically mock them here so EMBER can gracefully catch parsing errors without crashing.
            for legacy_exc in ['bad_format', 'bad_file', 'pe_error', 'parser_error', 'read_out_of_bound']:
                if not hasattr(lief, legacy_exc):
                    setattr(lief, legacy_exc, type(legacy_exc, (Exception,), {}))
                    
            import numpy as np
            # Numpy 1.24+ removed np.int, np.float, and np.bool which EMBER uses. We alias them back.
            if not hasattr(np, 'int'): np.int = int
            if not hasattr(np, 'float'): np.float = float
            if not hasattr(np, 'bool'): np.bool = bool
            
            # Scikit-learn 1.3+ strictly enforces iterable of iterables for FeatureHasher, which breaks EMBER.
            import sklearn.feature_extraction
            original_transform = sklearn.feature_extraction.FeatureHasher.transform
            def patched_transform(self, raw_X):
                try:
                    return original_transform(self, raw_X)
                except ValueError as e:
                    if "iterable over iterables" in str(e):
                        return original_transform(self, [raw_X])
                    raise
            sklearn.feature_extraction.FeatureHasher.transform = patched_transform
            
            import ember
        except ImportError:
            raise ImportError("The 'ember' Python package is required. Run: pip install git+https://github.com/endgameinc/ember.git lief")

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")

        # Instantiate the EMBER 2018 feature extractor (version 2)
        extractor = ember.PEFeatureExtractor(2)
        
        try:
            # Extract the raw 2,351 features
            features = np.array(extractor.feature_vector(file_data), dtype=np.float32)
            return features.tolist()
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise ValueError(f"EMBER Extraction Failed (file might be corrupt or not a valid PE): {e}")
