from typing import List

class FeatureExtractor:
    """
    Base interface for all file-type specific feature extractors.
    """
    def extract(self, file_path: str) -> List[float]:
        raise NotImplementedError("Subclasses must implement the extract() method.")
