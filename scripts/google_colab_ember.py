# ==============================================================================
# EMBER DATASET - GOOGLE COLAB TRAINING SCRIPT
# ==============================================================================
# INSTRUCTIONS:
# 1. Go to https://colab.research.google.com/
# 2. Create a "New Notebook"
# 3. Go to Runtime -> Change runtime type -> Select "T4 GPU" (This makes training 100x faster)
# 4. Copy and paste the blocks below into separate cells in Colab and press Play.

# ==========================================
# CELL 1: Download & Install Dependencies
# ==========================================
!pip install -q git+https://github.com/endgameinc/ember.git
!pip install -q xgboost scikit-learn

# Download the massive 2018 EMBER dataset (approx. 1.6 GB compressed)
!wget https://ember.elastic.co/ember_dataset_2018_2.tar.bz2
# Extract the dataset (this will take a few minutes)
!tar -xjf ember_dataset_2018_2.tar.bz2

# ==========================================
# CELL 2: Vectorize the Raw JSON Features
# ==========================================
import ember
import os

data_dir = "ember2018/"
print("Vectorizing EMBER dataset...")
# This reads the raw JSONs and converts them into optimized Numpy format (.dat files)
ember.create_vectorized_features(data_dir)
print("Vectorization complete!")

# ==========================================
# CELL 3: Train the Commercial XGBoost Model
# ==========================================
import ember
import xgboost as xgb
import numpy as np
import pickle
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

data_dir = "ember2018/"
print("Loading vectorized features into memory...")

# Read the numpy memmaps
X_train, y_train, X_test, y_test = ember.read_vectorized_features(data_dir)

# EMBER contains "unlabelled" data mixed in which are assigned a label of -1. 
# We must filter these out before training.
train_rows = (y_train != -1)
X_train_filtered = X_train[train_rows]
y_train_filtered = y_train[train_rows]

print(f"Training on {X_train_filtered.shape[0]} files with {X_train_filtered.shape[1]} features...")

# Initialize XGBoost, explicitly using Colab's Free GPU
clf = xgb.XGBClassifier(
    n_estimators=300,        # More estimators because the dataset is massive
    max_depth=8,             # Deeper trees to capture complex malware patterns
    learning_rate=0.1,
    tree_method='hist',      # Histogram method is REQUIRED for massive datasets
    device='cuda',           # Tells XGBoost to use the T4 GPU
    eval_metric='logloss'
)

# Start training! This will take a few minutes on the GPU.
xgbModel = clf.fit(X_train_filtered, y_train_filtered)
print("Model Training Complete!")

# ==========================================
# CELL 4: Evaluate & Download
# ==========================================
# Filter test set
test_rows = (y_test != -1)
X_test_filtered = X_test[test_rows]
y_test_filtered = y_test[test_rows]

print("Evaluating on test set...")
y_pred = xgbModel.predict(X_test_filtered)

print("\n--- EMBER MODEL METRICS ---")
print(f"Accuracy:  {accuracy_score(y_test_filtered, y_pred):.4f}")
print(f"Precision: {precision_score(y_test_filtered, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test_filtered, y_pred):.4f}")
print(f"F1-Score:  {f1_score(y_test_filtered, y_pred):.4f}")

# Save the trained model
model_path = "ember_xgboost_model.pkl"
with open(model_path, "wb") as f:
    pickle.dump(xgbModel, f)

print(f"\n[SUCCESS] Model saved to {model_path}.")
print("Look at the folder icon on the left side of Colab, right-click the .pkl file, and click 'Download'.")
