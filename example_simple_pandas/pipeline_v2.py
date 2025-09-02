from kfp import dsl
from kfp.dsl import Output, Input, Dataset

@dsl.component(
    base_image='python:3.12',
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

@dsl.component(
    base_image='python:3.12',
    packages_to_install=['pandas==2.3.1']
)
def validate_data(input_data: Input[Dataset]) -> str:
    """
    Validates the processed dataset and returns summary statistics
    
    Args:
        input_data: Input dataset to validate
        
    Returns:
        Summary statistics as string
    """
    import pandas as pd
    
    print(f"🔍 Validating dataset at: {input_data.path}")
    
    # Read the processed data
    df = pd.read_csv(input_data.path)
    
    # Perform validation
    validation_results = {
        "rows": len(df),
        "columns": len(df.columns),
        "has_sepal_area": "sepal_area" in df.columns,
        "no_nulls": df.isnull().sum().sum() == 0,
        "columns_list": list(df.columns)
    }
    
    print(f"✅ Validation results: {validation_results}")
    
    return f"Dataset validated: {validation_results['rows']} rows, {validation_results['columns']} columns"

@dsl.pipeline(
    name='enhanced-preprocessing-pipeline',
    description='Preprocesses CSV data with validation step'
)
def enhanced_preprocessing_pipeline():
    """
    Enhanced pipeline that preprocesses data and validates the output
    """
    # Step 1: Preprocess the data
    preprocess_task = preprocess_data()
    preprocess_task.set_display_name('Preprocess Data')
    preprocess_task.set_cpu_limit('1')
    preprocess_task.set_memory_limit('512Mi')
    
    # Step 2: Validate the processed data
    validate_task = validate_data(input_data=preprocess_task.outputs['processed_data'])
    validate_task.set_display_name('Validate Processed Data')
    validate_task.set_cpu_limit('0.5')
    validate_task.set_memory_limit('256Mi')
    
    # Set execution order (validate_task depends on preprocess_task)
    validate_task.after(preprocess_task)