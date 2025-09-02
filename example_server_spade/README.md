# Example SPADE Server Test

**Ejemplo intermedio** entre la simplicidad del example1 y la complejidad del example2.

## 🎯 Objetivo

Probar que el servidor SPADE (XMPP) puede iniciarse correctamente en un contenedor de Kubeflow y verificar su conectividad.

## 🔧 Qué hace este ejemplo

1. **Inicia servidor SPADE**: Ejecuta `spade run` con configuración básica
2. **Verifica conectividad**: Prueba conexión TCP al puerto XMPP
3. **Mantiene servidor activo**: Durante ~10 segundos para verificación
4. **Genera reporte**: Crea archivo TXT con resultado del test

## 📊 Complejidad

- **Example 1**: Simple procesamiento de datos con pandas
- **Example 3**: Test de servidor SPADE (este ejemplo) ⬅️ 
- **Example 2**: Sistema multi-agente completo con comunicación

## 📁 Estructura

```
example_server_spade/
├── requirements.txt              # Dependencias SPADE
├── pipeline.py                   # Componente Kubeflow con código embebido
├── compile_pipeline.py           # Compilador del pipeline
├── spade_server_agent_test_pipeline.yaml  # Pipeline compilado
└── README.md                     # Esta documentación
```

## 🚀 Cómo usar

### 1. Compilar pipeline

```bash
cd example_server_spade
python compile_pipeline.py
```

### 2. Ejecutar en Vertex AI

1. Sube `spade_server_agent_test_pipeline.yaml` a Vertex AI Pipelines
2. Ejecuta el pipeline
3. Descarga el artifact TXT con el resultado

## 📋 Resultado esperado

El pipeline generará un archivo de texto como este:

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

🎯 RESULTADO FINAL: ✅ SUCCESS
```

## 🐛 Debugging

Si el test falla, el archivo TXT incluirá información de error:

- `Server Started: False` → Problema iniciando servidor SPADE
- `Server Accessible: False` → Servidor inició pero no acepta conexiones
- `Error: [mensaje]` → Error específico durante la ejecución

## 🔍 Logs importantes

En los logs del componente Kubeflow verás:

- `🎯 Iniciando test del servidor SPADE...`
- `🔌 Puerto disponible: 5222`
- `📡 Iniciando servidor SPADE...`
- `🚀 Servidor iniciado (PID: 123)`
- `✅ Servidor SPADE iniciado correctamente`
- `🔍 Probando conectividad al puerto 5222...`
- `✅ Servidor accesible en puerto 5222`
- `📋 Resultado del test: ✅ EXITOSO`

## 🎯 Propósito del ejemplo

Este ejemplo demuestra:

- **Integración SPADE básica**: Cómo ejecutar servidor SPADE en Kubeflow con pip runtime installation
- **Manejo de procesos**: Iniciar, verificar y terminar procesos correctamente  
- **Verificación de servicios**: Test de conectividad a servicios de red
- **Artifact generation**: Crear archivos de resultado para Kubeflow
- **Error handling**: Manejo robusto de errores y cleanup
- **Embedded code approach**: Todo el código embebido en el componente para Vertex AI

Es el **paso previo perfecto** antes de implementar sistemas multi-agente más complejos como el example2.