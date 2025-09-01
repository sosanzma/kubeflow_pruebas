import kfp
from pipeline import spade_server_agent_test_pipeline

if __name__ == '__main__':
    print("Compilando pipeline SPADE Server + Agent Test...")
    
    kfp.compiler.Compiler().compile(
        pipeline_func=spade_server_agent_test_pipeline,
        package_path='spade_server_agent_test_pipeline.yaml'
    )
    
    print("Pipeline compilado exitosamente en: spade_server_agent_test_pipeline.yaml")
    print("")
    print("Example 3 EXTENDIDO: SPADE Server + Agent Test")
    print("   - Complejidad: Intermedia+ (servidor + agente simple)")
    print("   - Funcionalidad: Test de servidor SPADE + agente que envia mensajes")
    print("   - Output: Archivo TXT con resultado completo (servidor + agente)")
    print("")
    print("Para usar en Vertex AI:")
    print("   1. Sube 'spade_server_agent_test_pipeline.yaml' a Vertex AI")
    print("   2. Ejecuta el pipeline")
    print("   3. Descarga el artifact TXT con el resultado completo del test")