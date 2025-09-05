# Kubeflow + SPADE

**Integración de agentes SPADE en Kubeflow** con ejemplos de complejidad progresiva para Google Vertex AI.

## Propósito

Desarrollar sistemas multi-agente usando framework SPADE en pipelines Kubeflow. Todos los ejemplos optimizados para **Google Cloud Vertex AI**.

## Estructura del Repositorio

```
kubeflow/
├── example_simple_pandas/     # Nivel 1: procesamiento con pandas
├── example2_agentes/          # Nivel 2: sistema multi-agente SPADE  
├── example_server_spade/      # Nivel 3: testing de servidor SPADE
├── example_simfleet/          # Nivel 4: simulación de flota SimFleet
├── CLAUDE.md                  # Instrucciones para Claude Code
└── README.md                  # Este documento
```

## Cuatro Niveles de Complejidad

### **Nivel 1: Procesamiento Básico**
**Directorio**: `example_simple_pandas/`
- **Tecnología**: Python 3.12, pandas, Kubeflow KFP v2
- **Flujo**: CSV remoto → procesamiento pandas → artefacto Kubeflow
- **Características**: Sin Docker, instalación pip runtime

### **Nivel 2: Sistema Multi-Agente** 
**Directorio**: `example2_agentes/`
- **Tecnología**: SPADE 4.0.3, protocolo XMPP, asyncio
- **Agentes**: PingAgent (emisor) y PongAgent (receptor)
- **Arquitectura**:
  ```
  ProcessManager → Servidor XMPP → Comunicación Agentes → Resultados
  ```

### **Nivel 3: Testing Servidor SPADE**
**Directorio**: `example_server_spade/`
- **Objetivo**: Verificar arranque servidor y conectividad TCP
- **Duración**: ~20-30 segundos
- **Validación**: Salud servidor, puerto accesible

### **Nivel 4: Simulación Flota SimFleet**
**Directorio**: `example_simfleet/`
- **Tecnología**: SimFleet 2.0.1, vehículos drone, modo headless
- **Arquitectura**:
  ```
  SimFleet Engine → SPADE Server → Vehicle Agents → Mission Execution
  ```

## Patrones de Integración

### **Vertex AI (Sin Docker)**
```python
@dsl.component(
    base_image='python:3.12',
    packages_to_install=['spade==4.0.3', 'pandas==2.3.1']
)
def mi_componente(results: Output[Dataset] = None):
    # Todo el código embebido aquí
```

### **Gestión Servidor SPADE**
```python
# Puerto dinámico
port = find_available_port(start_port=5222)

# Servidor estándar  
subprocess.Popen(["spade", "run"])

# Cleanup procesos
process_manager.add_process(server_process)
```

## Compilar y Desplegar

### **Compilar Pipelines**
```bash
cd example_simple_pandas && python compile_pipeline.py
cd example2_agentes && python compile_pipeline.py  
cd example_server_spade && python compile_pipeline.py
cd example_simfleet && python compile_pipeline.py
```

### **Desplegar en Vertex AI**
1. Subir archivos `*.yaml` a Google Cloud Vertex AI Pipelines
2. Configurar parámetros (max_messages, timeouts, etc.)
3. Ejecutar y descargar artefactos (TXT, JSON)

## Arquitectura Embebida

**Problema**: Kubeflow no puede importar módulos Python externos en contenedores.

**Solución**: Código completo embebido en componentes Kubeflow.

```python
@dsl.component(base_image='python:3.12', packages_to_install=['spade==4.0.3'])
def sistema_spade(results: Output[Dataset] = None):
    # TODO EL CÓDIGO EMBEBIDO AQUÍ
    import asyncio, subprocess
    from spade.agent import Agent
    
    class PingAgent(Agent):
        # Implementación completa...
    
    # Ejecución completa del sistema
    results = asyncio.run(main())
```

## Documentación

- **INSTRUCTIONS.md**: guía práctica de consulta rápida para crear cualquier ejemplo nuevo en Kubeflow.


