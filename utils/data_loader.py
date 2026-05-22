import os
import pandas as pd

def load_market_data():
    """
    Loads, cleans, and optimizes the 2026 Global Markets dataset.
    Automatically parses categorizes assets to save memory.
    """
    # Look for the data file relative to the project root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file = os.listdir(base_dir + '/data')[0]
    file_path = os.path.join(base_dir, 'data', file)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing Kaggle file at: {file_path}. Please download it.")
        
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Clean string white spaces out of categorical columns
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Optimize memory usage for your layout dropdowns
    if 'asset_class' in df.columns:
        df['asset_class'] = df['asset_class'].astype('category')
        
    return df

if __name__ == '__main__':
    # Test execution to verify the data reads cleanly
    try:
        data = load_market_data()
        print("Data successfully loaded!")
        print(f"Dataset Shape: {data.shape[0]} rows, {data.shape[1]} columns.")
        print("\n Available columns include:")
        print(list(data.columns[:10]))  # Print first 10 metrics out of 131
    except Exception as e:
        print(f"Error reading file: {e}")