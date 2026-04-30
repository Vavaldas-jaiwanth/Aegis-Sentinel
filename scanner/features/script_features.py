import math
import os
from collections import Counter
from typing import List
from .base import FeatureExtractor

class ScriptFeatureExtractor(FeatureExtractor):
    def extract(self, file_path: str) -> List[float]:
        """
        Extracts script-specific features.
        Returns a 10-element vector to maintain pipeline consistency with the PE model.
        """
        keywords = ['eval', 'cmd', 'powershell', 'base64', 'wscript', 'shell', 'exec', 'invoke']
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read script: {e}")
            
        content_lower = content.lower()
        size = len(content)
        
        # 1. Calculate general string entropy
        entropy = 0.0
        if size > 0:
            counts = Counter(content)
            # Keeping the negative entropy logic consistent with PE training
            entropy = sum((count / size) * math.log2(count / size) for count in counts.values())
            
        # 2. Count keywords
        keyword_counts = sum(content_lower.count(kw) for kw in keywords)
        
        # 3. Suspicious patterns (e.g. heavily obfuscated long lines)
        lines = content.split('\n')
        max_line_length = max((len(line) for line in lines), default=0)
        
        # We map these script heuristics and pad them to satisfy the massive 2351-float EMBER signature.
        base_features = [
            float(size),                 # Machine -> File Size
            float(keyword_counts),       # SizeOfOptionalHeader -> Keyword hits
            float(max_line_length),      # MajorSubsystemVersion -> Max Line Length
            0.0,                         # DllCharacteristics
            0.0,                         # SizeOfStackReserve
            float(entropy),              # SectionsMeanEntropy -> Script Entropy
            float(entropy),              # SectionsMaxEntropy
            0.0,                         # Subsystem
            0.0,                         # ResourcesMaxEntropy
            0.0,                         # VersionInformationSize
            float(entropy),              # OverallEntropy
            0.0,                         # NumImports
            0.0,                         # SuspiciousAPICount
            0.0,                         # NumSections
            0.0,                         # EntryPoint
            0.0,                         # SizeOfCode
            0.0                          # IsSigned
        ]
        
        # Pad the remaining features with zeroes to prevent LightGBM from crashing
        return base_features + [0.0] * (2381 - len(base_features))
