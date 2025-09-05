# Example 4 SimFleet: Fleet Simulation System

**Sistema de simulación de flota multi-agente** usando SimFleet framework con vehículos autónomos.

## Objetivo

Demostrar una **simulación completa de flota de vehículos** funcionando en **Vertex AI**, donde vehículos drone ejecutan misiones de transporte coordinadas por SimFleet con servidor SPADE integrado.

## Arquitectura del Sistema

### **Diseño Embebido**
```
Kubeflow Component (pipeline.py)
├── SPADE Server (spade run)    # Servidor XMPP para comunicación
├── SimFleet Simulator          # Motor de simulación de flota
├── VehicleAgent (drone1)       # Vehículo autónomo 1
├── VehicleAgent (drone2)       # Vehículo autónomo 2
└── ProcessManager              # Gestión de procesos y cleanup
```

### **Flujo de Ejecución**
```
1. Inicia servidor SPADE (puerto dinámico)
2. Crea configuración JSON temporal con vehículos
3. Ejecuta SimFleet con --autorun (modo headless)
4. Vehículos ejecutan misiones durante N segundos
5. Captura logs y resultados de simulación
6. Cleanup automático de procesos
7. Genera reporte con estadísticas reales
```



## Estructura

```
example4_simfleet/
├── requirements.txt                    # Dependencias SimFleet
├── vehicles.json                       # Configuración de prueba local
├── run_simulation.py                   # Ejecutor local con SPADE
├── pipeline.py                         # Componente Kubeflow embebido
├── compile_pipeline.py                 # Compilador del pipeline
├── simfleet_basic_pipeline.yaml        # Pipeline compilado
└── README.md                           # Esta documentación
```

## Uso

### **1. Compilar Pipeline**
```bash
cd example4_simfleet
python compile_pipeline.py
```

### **2. Subir a Vertex AI**
1. Ve a **Google Cloud Console** → **Vertex AI** → **Pipelines**
2. Sube `simfleet_basic_pipeline.yaml`
3. Dale nombre: "SimFleet Fleet Simulation"

### **3. Configurar Parámetros**
- `max_simulation_time`: Duración en segundos (default: 30)
- `num_vehicles`: Número de vehículos (1-2, default: 2)

### **4. Ejecutar y Verificar**
- Ejecuta el pipeline
- Monitorea logs en tiempo real
- Descarga artifact TXT con resultados

## Resultado Esperado

### **Archivo TXT de Resultado:**
```
SimFleet Basic Simulation Results
====================================
Overall Simulation Success: True

Configuration:
- Simulation Time: 30 seconds
- Number of Vehicles: 2
- Simulation Name: kubeflow_fleet

Execution Details:
- Return Code: 0
- Execution Time: 30 seconds
- Error: None

SimFleet Output:
2025-09-03 09:18:19.927 | INFO | Starting SimFleet (kubeflow_fleet)
2025-09-03 09:18:19.947 | INFO | Creating 2 vehicles
2025-09-03 09:18:20.754 | INFO | Simulator agent running
...

RESULTADO FINAL: SUCCESS
```

## Pruebas Locales

### **Ejecutar Simulación Local**
```bash
pip install simfleet
python run_simulation.py
```

