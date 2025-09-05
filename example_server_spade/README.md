# Example 3: SPADE Server Test

**Test de conectividad del servidor SPADE** en contenedor Kubeflow.

## Objetivo

Verificar que el servidor SPADE (XMPP) inicia correctamente y acepta conexiones TCP en Vertex AI.

## Arquitectura

### **Flujo de Ejecución**
```
1. Encuentra puerto disponible (5222+)
2. Inicia servidor SPADE (spade run)
3. Verifica conectividad TCP
4. Mantiene servidor activo ~10 segundos
5. Genera reporte de resultado
6. Cleanup automático
```

## Estructura

```
example_server_spade/
├── pipeline.py                          # Componente Kubeflow embebido
├── compile_pipeline.py                  # Compilador del pipeline
├── spade_server_agent_test_pipeline.yaml # Pipeline compilado
└── README.md                            # Esta documentación
```

## Uso

### **1. Compilar Pipeline**
```bash
cd example_server_spade
python compile_pipeline.py
```

### **2. Ejecutar en Vertex AI**
1. Sube `spade_server_agent_test_pipeline.yaml` a Vertex AI Pipelines
2. Ejecuta el pipeline
3. Descarga el artifact TXT con resultado

## Resultado Esperado

### **Archivo TXT de Resultado:**
```
SPADE Server Test Results
========================
Test Success: True
Server Started: True
Server Accessible: True
Port Used: 5222
Duration: 25.34 seconds
Error: None

Summary: SPADE server test PASSED
Timestamp: 2024-01-15T10:30:45.123456

RESULTADO FINAL: SUCCESS
```

## Debug

### **Estados de Fallo:**
- `Server Started: False` → Error iniciando servidor SPADE
- `Server Accessible: False` → Servidor inició pero no acepta conexiones
- `Error: [mensaje]` → Error específico durante ejecución