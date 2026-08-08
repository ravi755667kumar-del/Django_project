import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'rf_model.joblib')

def load_and_preprocess_data():
    """
    Loads the dataset.csv and performs basic preprocessing 
    to extract useful features like the 'hour' of the day.
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")
        
    df = pd.read_csv(DATASET_PATH)
    
    # Extract 'hour' from the 'time' column
    # The time might look like '17:14:18.427401'
    df['time'] = df['time'].fillna('12:00:00')
    
    # Safely extract hour
    try:
        df['hour'] = pd.to_datetime(df['time'], errors='coerce').dt.hour
    except:
        df['hour'] = 12
        
    df['hour'] = df['hour'].fillna(12).astype(int)
    
    # Fill missing values for numerical weather data
    df['temperature'] = df['temperature'].fillna(df['temperature'].mean())
    df['humidity'] = df['humidity'].fillna(df['humidity'].mean())
    df['category'] = df['category'].fillna('Normal')
    
    return df
