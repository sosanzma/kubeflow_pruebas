# Kubeflow + SPADE

**Guía práctica para integrar agentes SPADE en Kubeflow**, con ejemplos de complejidad progresiva optimizados para despliegue en Google Vertex AI.

## Propósito

Este repositorio enseña cómo desarrollar sistemas multi-agente usando el framework SPADE dentro de pipelines de Kubeflow. Dado que Kubeflow es complejo de instalar localmente, todos los ejemplos están optimizados para ejecutarse en **Google Cloud Vertex AI**.

## Estructura del Repositorio

```
kubeflow/
├── example_simple_pandas/     # Nivel básico: procesamiento con pandas
├── example2_agentes/          # Nivel avanzado: sistema multi-agente SPADE  
├── example_server_spade/      # Nivel intermedio: testing de servidor SPADE
├── example4_simfleet/         # Nivel avanzado: simulación de flota con SimFleet
├── GUIA_SPADE_VERTEX_AI.md   # Guía del desarrollador para SPADE en Vertex AI
├── README.md                  # Este documento
└── INSTRUCTIONS.md            # Instrucciones detalladas de configuración
```

## Cuatro Niveles de Aprendizaje

### Nivel 1: Procesamiento Básico de Datos
**Directorio**: `example_simple_pandas/`

**Objetivo**: Aprender los fundamentos de Kubeflow con procesamiento de datos usando pandas

- **Tecnología**: Python 3.12, pandas, Kubeflow KFP v2
- **Archivos clave**: `pipeline.py`, `pipeline_v2.py` (componente único vs múltiple)
- **Flujo de datos**: CSV remoto → procesamiento pandas → ingeniería de características → artefacto Kubeflow
- **Características**: Instalación pip en tiempo de ejecución, sin Docker requerido

### Nivel 2: Sistema Multi-Agente SPADE
**Directorio**: `example2_agentes/`

**Objetivo**: Sistema de comunicación multi-agente de calidad de producción usando framework SPADE

- **Tecnología**: SPADE 4.0.3, protocolo XMPP, asyncio, gestión de procesos
- **Agentes**: PingAgent (emisor) y PongAgent (receptor)
- **Comunicación**: Servidor XMPP con asignación dinámica de puertos
- **Arquitectura**:
  ```
  ProcessManager → Servidor XMPP → Comunicación de Agentes → Recolección de Resultados
       ↓              ↓               ↓                        ↓
   Manejo Señales  Puerto Dinámico  Intercambio Mensajes  Artefactos JSON
  ```


### Nivel 3: Testing de Servidor SPADE
**Directorio**: `example_server_spade/`

**Objetivo**: Pruebas intermedias de conectividad del servidor SPADE y comunicación básica de agentes

- **Pruebas**: Arranque del servidor, conectividad TCP, mensajería simple de agentes
- **Duración**: 20-30 segundos aproximadamente
- **Validación**: Salud del servidor, accesibilidad de puerto, intercambio de mensajes

### Nivel 4: Simulación de Flota SimFleet
**Directorio**: `example4_simfleet/`

**Objetivo**: Simulación completa de flota de vehículos usando framework SimFleet con vehículos autónomos

- **Tecnología**: SimFleet 2.0.1, SPADE backend, vehículos drone, modo headless
- **Vehículos**: VehicleAgent con misiones origen-destino
- **Simulación**: Ejecución automática con --autorun, sin interfaz web
- **Arquitectura**:
  ```
  SimFleet Engine → SPADE Server → Vehicle Agents → Mission Execution
       ↓              ↓              ↓                ↓
   JSON Config   Puerto Dinámico  Drone Movement   Results Capture
  ```


## Patrones 

### Integración con Vertex AI (Sin Docker)
```python
@dsl.component(
    base_image='python:3.12',  # Imagen estándar de Python
    packages_to_install=['spade==4.0.3', 'pandas==2.3.1']  # Instalación pip en tiempo de ejecución
)
def mi_componente(results: Output[Dataset] = None):
    # Todo el código embebido aquí - listo para Vertex AI
```

### Gestión del Servidor SPADE
```python
# Asignación dinámica de puerto
port = find_available_port(start_port=5222)

# Comando estándar del servidor SPADE  
subprocess.Popen(["spade", "run"])

# Limpieza de procesos con señales
process_manager.add_process(server_process)
```

### Compilar Pipelines

Al compilar las pipelines se crean los archivcos `*.yaml` con toda la informacion necesaria para ser ejecutados en Kubleflow/Vertex AI 
```bash
# Procesamiento básico con pandas
cd example_simple_pandas && python compile_pipeline.py

# Sistema multi-agente avanzado  
cd example2_agentes && python compile_pipeline.py

# Testing de servidor SPADE
cd example_server_spade && python compile_pipeline.py

# Simulación de flota SimFleet
cd example4_simfleet && python compile_pipeline.py
```

### Desplegar en Vertex AI
1. Subir archivos `*.yaml` generados a Google Cloud Vertex AI Pipelines
2. Configurar parámetros en la UI (max_messages, timeouts, etc.)
3. Ejecutar y descargar artefactos (reportes TXT, datos JSON)


## Arquitectura Embebida

**Desafío**: Kubeflow ejecuta cada componente en contenedores aislados de Kubernetes, por lo que no puede importar módulos Python externos

**Solución**: Todo el código embebido dentro de componentes Kubeflow

```python
@dsl.component(base_image='python:3.12', packages_to_install=['spade==4.0.3'])
def sistema_spade(results: Output[Dataset] = None):
    # ============================================
    # TODO EL CÓDIGO SPADE EMBEBIDO AQUÍ
    # ============================================
    import asyncio, subprocess
    from spade.agent import Agent
    
    class PingAgent(Agent):
        # Implementación completa del agente...
    
    class PongAgent(Agent):
        # Implementación completa del agente...
    
    # Sistema de orquestación completo...
    async def main():
        # Ejecución completa del sistema...
    
    # Ejecutar todo
    results = asyncio.run(main())
```

## Documentación

- **INSTRUCTIONS.md**: guía práctica de consulta rápida para crear cualquier ejemplo nuevo en Kubeflow.


