import kfp
from pipeline_v2 import enhanced_preprocessing_pipeline

if __name__ == '__main__':
    print("Compiling enhanced preprocessing pipeline...")
    
    kfp.compiler.Compiler().compile(
        pipeline_func=enhanced_preprocessing_pipeline,
        package_path='enhanced_preprocessing_pipeline.yaml'
    )
    print("Enhanced pipeline compiled successfully: enhanced_preprocessing_pipeline.yaml")