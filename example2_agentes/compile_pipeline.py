import kfp
from pipeline import spade_ping_pong_embedded_pipeline

if __name__ == '__main__':
    print("Compilando pipeline SPADE Ping-Pong EMBEBIDO...")
    
    kfp.compiler.Compiler().compile(
        pipeline_func=spade_ping_pong_embedded_pipeline,
        package_path='spade_ping_pong_pipeline.yaml'
    )
    
    print("Pipeline compilado exitosamente en: spade_ping_pong_pipeline.yaml")
