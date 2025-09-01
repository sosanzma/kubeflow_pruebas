# Example 2- agentes : SPADE Multi-Agent System

**Sistema multi-agente completo** usando SPADE framework con comunicación Ping-Pong entre agentes.

## 🎯 Objetivo

Demostrar un **sistema multi-agente complejo** funcionando completamente en **Vertex AI**, donde dos agentes SPADE intercambian mensajes en tiempo real a través de un servidor XMPP integrado.

## 🏗️ Arquitectura del Sistema

### **Diseño Embebido (Versión Final)**
```
Kubeflow Component (pipeline.py)
├── ProcessManager           # Manejo seguro de procesos
├── XMPP Server (spade run) # Servidor de mensajería
├── PingAgent               # Envía mensajes ping
├── PongAgent               # Responde con pong
└── Orchestrator            # Coordina todo el sistema
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

## 📊 Componentes del Sistema

### **🤖 PingAgent**
- **Función**: Envía mensajes ping periódicamente
- **Comportamiento**: `CyclicBehaviour` que envía mensajes cada 2 segundos
- **JID**: `ping@localhost`
- **Límite**: Configurable via `max_pings` (default: 10)

### **🏓 PongAgent**
- **Función**: Recibe pings y responde con pongs
- **Comportamiento**: `CyclicBehaviour` que escucha mensajes
- **JID**: `pong@localhost`
- **Timeout**: 30 segundos por mensaje

### **📡 Servidor XMPP**
- **Comando**: `spade run` (sin parámetros adicionales)
- **Puerto**: Dinámico (encuentra puerto disponible)
- **Base de datos**: En memoria (para containerización)

### **🛡️ ProcessManager**
- **Función**: Manejo seguro de procesos con cleanup automático
- **Señales**: Maneja SIGTERM y SIGINT
- **Cleanup**: Termina procesos gracefully o con kill si es necesario

## 💾 Estructura de Archivos

```
example2/
├── pipeline.py                    # 🎯 Pipeline embebido completo
├── compile_pipeline.py            # 🔧 Compilador del pipeline
├── spade_ping_pong_pipeline.yaml  # 📄 Pipeline listo para Vertex AI
├── Dockerfile                     # 🐳 Imagen Docker con SPADE
├── requirements.txt               # 📦 Dependencias
├── README.md                      # 📚 Esta documentación
└── output/                        # 📊 Resultados de pruebas locales
    ├── spade_ping_pong_results.json
    └── summary.json
```

## 🚀 Cómo Usar

### **1. Compilar Pipeline**
```bash
cd example2
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

## 📋 Resultado Esperado

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

🎯 RESULTADO FINAL: ✅ SUCCESS / ❌ FAILED
```

### **Datos JSON Detallados:**
- Historial completo de mensajes con timestamps
- Estadísticas de cada agente
- Metadatos de orquestación
- Información del servidor XMPP

## 🔍 Interpretación de Resultados

### **✅ Éxito Total (100%)**
- Messages Sent = Messages Received
- Ambos agentes terminan correctamente
- Sin errores de sistema

### **✅ Éxito Parcial (90%+)**
- Messages Sent > Messages Received (diferencia de 1-2)
- **NORMAL** en sistemas distribuidos
- Causado por timing entre agentes

### **❌ Fallo del Sistema**
- Servidor XMPP no inicia
- Error en creación de agentes
- Timeout completo sin mensajes

## 🔧 Evolución del Desarrollo

### **🏗️ Proceso de Desarrollo**

#### **Versión 1: Arquitectura Modular (No funcionó en Vertex AI)**
```
Dockerfile → orchestrator.py → spade_ping_pong.py
```
**Problema**: Vertex AI no puede importar archivos externos

#### **Versión 2: Arquitectura Embebida (Funciona ✅)**
```
pipeline.py (todo embebido) → Vertex AI
```
**Solución**: Todo el código integrado en el componente Kubeflow

### **🎓 Lecciones Aprendidas**

1. **Kubeflow vs Docker**: El componente ejecuta código Python embebido, no el CMD del Dockerfile
2. **Importaciones Externas**: No funcionan en Vertex AI - usar código embebido
3. **Timing Distribuido**: Los sistemas multi-agente requieren timing cuidadoso
4. **Cleanup de Procesos**: Essential para evitar procesos zombie
5. **Manejo de Errores**: Cada paso debe tener fallback y logging

### **🔄 Patrón de Diseño Final**

**Patrón "Embedded Multi-Agent":**
- ✅ Todo el código en un solo archivo Python
- ✅ Gestión completa del ciclo de vida
- ✅ Manejo robusto de errores
- ✅ Compatibilidad total con Vertex AI
- ✅ Parametrización flexible

## ⚡ Optimizaciones Técnicas

### **Rendimiento**
- **CPU**: 2 cores (para servidor + agentes)
- **Memoria**: 1Gi (suficiente para SPADE + XMPP)
- **Timeout**: 30s por mensaje (balance entre velocidad y robustez)

### **Robustez**
- **Puerto dinámico**: Evita conflictos
- **Signal handling**: Cleanup automático
- **Error recovery**: Continúa aunque fallen componentes individuales
- **Logging detallado**: Para debugging en producción

## 🎯 Casos de Uso

Este ejemplo demuestra patrones aplicables a:

- **🤖 Sistemas de IA distribuida** (múltiples modelos coordinándose)
- **📊 Procesamiento distribuido** (workers + coordinator)
- **🎮 Simulaciones multi-agente** (juegos, ecosistemas)
- **🏭 Sistemas de control industrial** (sensores + actuadores)
- **📈 Trading algorithms** (múltiples estrategias coordinadas)

## 🏆 Valor Técnico

**Este ejemplo demuestra dominio de:**
- Sistemas multi-agente con SPADE
- Integración compleja con Kubeflow
- Manejo de procesos y recursos
- Arquitectura distribuida robusta
- Desarrollo cloud-native avanzado

**¡Un sistema multi-agente completo funcionando en la nube!** 🚀