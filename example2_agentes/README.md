# Example 2: SPADE Multi-Agent System

**Sistema multi-agente con comunicación Ping-Pong** usando SPADE framework.

## Objetivo

Demostrar comunicación entre dos agentes SPADE en tiempo real a través de servidor XMPP integrado en Vertex AI.

## Arquitectura del Sistema

### **Diseño Embebido**
```
Kubeflow Component (pipeline.py)
├── ProcessManager              # Manejo seguro de procesos  
├── XMPP Server (spade run)     # Servidor de mensajería
├── PingAgent                   # Envía mensajes ping
├── PongAgent                   # Responde con pong
└── Orchestrator                # Coordina todo el sistema
```

### **Flujo de Ejecución**
```
1. Inicia ProcessManager con cleanup automático
2. Encuentra puerto disponible (5222+)
3. Lanza servidor XMPP (spade run)
4. Espera a que servidor esté listo (10s)
5. Crea y inicia PingAgent y PongAgent
6. PingAgent envía N mensajes ping
7. PongAgent recibe y responde con pong
8. Recolecta estadísticas detalladas
9. Cleanup automático de procesos
10. Genera reporte completo
```

## Componentes del Sistema

### **PingAgent**
- **JID**: `ping@localhost`
- **Comportamiento**: `CyclicBehaviour` que envía mensajes cada 2 segundos
- **Límite**: Configurable via `max_pings` (default: 10)

### **PongAgent**
- **JID**: `pong@localhost` 
- **Comportamiento**: `CyclicBehaviour` que escucha mensajes
- **Timeout**: 30 segundos por mensaje

### **Servidor XMPP**
- **Comando**: `spade run` (sin parámetros adicionales)
- **Puerto**: Dinámico (encuentra puerto disponible)
- **Base de datos**: En memoria (para containerización)

## Estructura

```
example2_agentes/
├── pipeline.py                     # Pipeline embebido completo
├── compile_pipeline.py             # Compilador del pipeline
├── spade_ping_pong_pipeline.yaml   # Pipeline listo para Vertex AI
└── README.md                       # Esta documentación
```

## Uso

### **1. Compilar Pipeline**
```bash
cd example2_agentes
python compile_pipeline.py
```

### **2. Subir a Vertex AI**
1. Ve a **Google Cloud Console** → **Vertex AI** → **Pipelines**
2. Sube `spade_ping_pong_pipeline.yaml`
3. Dale nombre: "SPADE Ping-Pong System"

### **3. Configurar Parámetros**
- `max_pings`: Número de mensajes (recomendado: 5-15)
- `ping_interval`: Intervalo entre pings (actualmente no usado)

### **4. Ejecutar y Verificar**
- Ejecuta el pipeline
- Monitorea logs en tiempo real  
- Descarga artifact TXT con resultados

## Resultado Esperado

### **Archivo TXT de Resultado:**
```
SPADE Ping-Pong System Results (Embebido)
==============================================
Overall Test Success: True/False

Ping-Pong Communication:
- Messages Sent (Ping): 10
- Messages Received (Pong): 9-10
- Communication Success: True/False
- Expected Messages: 10

System Performance:
- Total Duration: ~45-60 seconds
- XMPP Server Port: 5222
- System Error: None

Agent Statistics:
- Ping Agent Status: completed
- Pong Agent Status: completed
- Message History Count: 9-10

RESULTADO FINAL: SUCCESS / FAILED
```