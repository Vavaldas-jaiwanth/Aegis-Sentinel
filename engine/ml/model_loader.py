import os
import lightgbm as lgb

_model_instance = None

def get_model(model_path: str = 'ember_model_2018.txt'):
    """
    Loads the official pre-trained EMBER LightGBM model from disk.
    Implements a singleton pattern to ensure the massive model is only loaded once per process.
    """
    global _model_instance
    
    if _model_instance is None:
        import sys
        if getattr(sys, 'frozen', False):
            # If PyInstaller packaged, use the executable's directory
            base_dir = os.path.dirname(sys.executable)
        else:
            # If standard python, use the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        full_path = os.path.join(base_dir, 'data', 'models', model_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"EMBER Model file not found at {full_path}. Please extract it from the tarball.")
            
        # LightGBM loads its model natively from the txt format
        _model_instance = lgb.Booster(model_file=full_path)
            
    return _model_instance
