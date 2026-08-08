import os
import sys

# ─── Make sure we can import from 'shop' ───────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from shop.recommendations.processes import load_and_preprocess_data, MODEL_PATH

def train():
    print("Loading dataset...")
    try:
        df = load_and_preprocess_data()
    except FileNotFoundError as e:
        print(e)
        print("Please place some orders first to generate the dataset!")
        return
        
    if len(df) < 5:
        print(f"Dataset too small ({len(df)} rows). Need at least 5 orders to train a good model!")
        # We can still train, but let's just warn them
        
    print(f"Dataset loaded with {len(df)} rows.")

    # 1. Define the features (X) and the target label (y)
    # We use weather data and time of day to predict what item they might want
    features = ['temperature', 'humidity', 'hour', 'category']
    target = 'item_name'
    
    X = df[features]
    y = df[target]
    
    # 2. Build a preprocessing pipeline
    # Numerical features need scaling, Categorical features need One-Hot Encoding
    numerical_features = ['temperature', 'humidity', 'hour']
    categorical_features = ['category']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ]
    )
    
    # 3. Create the Machine Learning Pipeline with Random Forest
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # 4. Train the model
    print("Training Random Forest model...")
    rf_pipeline.fit(X, y)
    
    # 5. Save the trained model to disk
    joblib.dump(rf_pipeline, MODEL_PATH)
    
    print(f"[OK] Model trained and saved successfully to -> {MODEL_PATH}")
    print(f"Classes the model learned to recommend: {list(rf_pipeline.classes_)}")

if __name__ == "__main__":
    train()
