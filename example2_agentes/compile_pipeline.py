import kfp
from pipeline import spade_ping_pong_embedded_pipeline

if __name__ == '__main__':
    print("Compilando pipeline SPADE Ping-Pong EMBEBIDO...")
    
    kfp.compiler.Compiler().compile(
        pipeline_func=spade_ping_pong_embedded_pipeline,
        package_path='spade_ping_pong_pipeline.yaml'
    )
    
    print("Pipeline compilado exitosamente en: spade_ping_pong_pipeline.yaml")
    print("")
    print("Example 2 EMBEBIDO: SPADE Ping-Pong System")
    print("   - Complejidad: Avanzada (sistema multi-agente completo)")
    print("   - Funcionalidad: PingAgent + PongAgent + Servidor XMPP")
    print("   - Arquitectura: TODO embebido en pipeline.py para Vertex AI")
    print("   - Output: Archivo TXT completo con estadisticas detalladas")
    print("")
    print("VENTAJAS de la version embebida:")
    print("   - Funciona 100% en Vertex AI (sin importaciones externas)")
    print("   - Manejo robusto de errores y cleanup")
    print("   - Estadisticas detalladas y logs completos")
    print("   - Compatible con parametros de pipeline")
    print("")
    print("Para usar en Vertex AI:")
    print("   1. Sube 'spade_ping_pong_pipeline.yaml' a Vertex AI")
    print("   2. Configura parametros: max_pings (ej: 5, 10, 15)")
    print("   3. Ejecuta el pipeline")
    print("   4. Descarga el artifact TXT con resultados completos")