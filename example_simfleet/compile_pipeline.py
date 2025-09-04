import kfp
from pipeline import simfleet_basic_pipeline

if __name__ == '__main__':
    print("Compilando pipeline SimFleet básico...")
    
    kfp.compiler.Compiler().compile(
        pipeline_func=simfleet_basic_pipeline,
        package_path='simfleet_basic_pipeline.yaml'
    )
    
    print("Pipeline compilado exitosamente en: simfleet_basic_pipeline.yaml")
    print("")
