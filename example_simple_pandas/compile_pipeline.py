import kfp
from pipeline import preprocessing_pipeline

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(
        pipeline_func=preprocessing_pipeline,
        package_path='preprocessing_pipeline.yaml'
    )
    print("Pipeline compilado exitosamente en: preprocessing_pipeline.yaml")