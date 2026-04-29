import pickle
import os

_model_instance = None

def get_model(model_path: str = 'model.pkl'):
    """
    Loads the machine learning model from disk.
    Implements a singleton pattern to ensure the model is only loaded once per process.
    """
    global _model_instance
    
    if _model_instance is None:
        # Resolve path relative to this file to ensure it finds model.pkl if executed from elsewhere
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, model_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Model file not found at {full_path}")
            
        with open(full_path, 'rb') as file:
            _model_instance = pickle.load(file)
            
    return _model_instance
