# Kubeflow Learning Repository

Este repositorio contiene ejemplos prácticos para aprender a usar **Kubeflow** con diferentes niveles de complejidad, desde procesamiento básico de datos hasta sistemas multi-agente avanzados usando SPADE.

## 📁 Estructura del Repositorio

```
kubeflow/
├── example1/          # Ejemplo básico: Preprocesamiento de datos con pandas
├── example2/          # Ejemplo avanzado: Sistema multi-agente SPADE 
├── example3/          # Ejemplo intermedio: Testing de servidor SPADE
├── README.md          # Este archivo
├── INSTRUCTIONS.md    # Guía paso a paso completa
├── CLAUDE.md          # Instrucciones para asistente AI y patrones arquitectónicos
└── server.db          # Base de datos del servidor SPADE
```

## 🎯 Tres Niveles de Complejidad

### 📊 Example 1: Pipeline Básico (Nivel Principiante)
**Propósito**: Preprocesamiento simple de datos CSV usando pandas
- **Tecnologías**: Python, pandas, Kubeflow KFP v2, Docker
- **Archivos clave**: `pipeline.py`, `preprocess.py`, `Dockerfile`
- **Flujo**: CSV → pandas → característica nueva (sepal_area) → artefacto Kubeflow


### 🤖 Example 2: Sistema Multi-Agente Avanzado 
**Propósito**: Orquestación compleja de agentes SPADE con comunicación XMPP
- **Tecnologías**: SPADE Framework, XMPP, asyncio, gestión de procesos
- **Patrón**: PingAgent ↔ PongAgent con servidor XMPP embedded
- **Arquitectura**: 
  ```
  Container Process Tree:
  ├── ProcessManager (manejo de señales)
  ├── Servidor XMPP (spade run)
  ├── PingAgent (CyclicBehaviour)
  ├── PongAgent (CyclicBehaviour)  
  └── Recolección de resultados
  ```


### 🔧 Example 3: Test de Servidor SPADE (Nivel Intermedio)
**Propósito**: Verificación de conectividad y funcionamiento básico de SPADE
- **Componentes**: Servidor SPADE + agente de prueba simple
- **Verificaciones**: Conectividad TCP, comunicación básica de agentes
- **Duración**: ~15-25 segundos

## 🏗️ Patrones Arquitectónicos

### Integración con Kubeflow
- **Componentes KFP v2**: Uso de `@dsl.component` con imágenes Docker personalizadas
- **Gestión de Artefactos**: `Output[Dataset]` para persistencia de datos
- **Contenedorización**: Imágenes en Docker Hub (`sosanzma/[image]:latest`)

### Patrón de Código Embedded 
**Problema**: Vertex AI no puede importar módulos Python externos desde contenedores
**Solución**: Código completo del sistema embedded dentro de componentes Kubeflow
**Impacto**: Componentes de una sola archivo con cientos de líneas, pero compatibilidad completa con la nube

### Gestión de Procesos SPADE
```python
class ProcessManager:
    # Manejo de señales SIGTERM/SIGINT
    # Limpieza graceful de subprocesos
    # Asignación dinámica de puertos (5222-5322)
    # Verificación de conectividad TCP
```

## 🛠️ Comandos Principales

### Desarrollo de Pipelines
```bash
# Compilar pipelines a YAML
cd example1/ && python compile_pipeline.py
cd example2/ && python compile_pipeline.py  
cd example3/ && python compile_pipeline.py

# Construir imágenes Docker
cd example1/ && docker build -t preprocess:latest .
cd example2/ && docker build -t spade-pingpong:latest .
cd example3/ && docker build -t spade-server-test:latest .

# Probar contenedores localmente
docker run --rm -v ${PWD}/output:/output preprocess:latest
docker run --rm -v ${PWD}/output:/output spade-pingpong:latest
docker run --rm -v ${PWD}/output:/output spade-server-test:latest
```

### Servidor SPADE
```bash
# Lanzar servidor SPADE (IMPORTANTE: sin parámetros adicionales)
spade run

# Verificar salud de componentes SPADE
cd example2/ && python health_check.py
```

### Pipeline Simple (Example 1)
```
CSV Externo → pandas → Ingeniería de Características → Artefacto Dataset Kubeflow
```

### Pipeline Multi-Agente Complejo (Example 2)
```
Orquestador → Servidor XMPP → Bucle de Comunicación de Agentes → Recolección de Estadísticas → Artefactos JSON/TXT
     ↓              ↓                      ↓
ProcessManager   Puerto Dinámico     Historial de Mensajes
```
