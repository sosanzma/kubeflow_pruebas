from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(
    packages_to_install=['pandas==2.3.1']
)
def preprocess_data(processed_data: Output[Dataset]) -> None:
    """
    Preprocesses CSV data and outputs as Kubeflow artifact
    
    Args:
        processed_data: Output dataset artifact containing the processed CSV
    """
    import pandas as pd
    
    print("🔄 Starting data preprocessing...")
    
    # Load and process the data (same logic as preprocess.py)
    df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
    print(f"📊 Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Add feature engineering
    df['sepal_area'] = df['sepal_length'] * df['sepal_width']
    print("✅ Added sepal_area feature")
    
    # Save directly to the Kubeflow artifact path
    df.to_csv(processed_data.path, index=False)
    print(f"💾 Processed data saved to artifact: {processed_data.path}")
    
    # Log summary statistics
    print(f"📄 Final dataset: {len(df)} rows, {len(df.columns)} columns")
    print(f"📈 Columns: {list(df.columns)}")
    
    return None

@dsl.pipeline(
    name='simple-preprocessing-pipeline',
    description='Lee un CSV y hace preprocesamiento con pandas'
)
def preprocessing_pipeline():
    preprocess_task = preprocess_data()
    preprocess_task.set_display_name('Preprocess Data')
