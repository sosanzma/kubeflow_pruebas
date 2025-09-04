# Instrucciones para Crear Ejemplos Kubeflow

## Archivos Requeridos

### Mínimo para funcionamiento
1. `pipeline.py` - Componente con código embebido
2. `compile_pipeline.py` - Compilador del pipeline

### Archivos generados
3. `nombre_pipeline.yaml` - Archivo para subir a Vertex AI

### Opcionales
4. `requirements.txt` - Lista de dependencias para referencia
5. `README.md` - Documentación del ejemplo

## Estructura de Directorio

```
ejemplo_nuevo/
├── pipeline.py
├── compile_pipeline.py
├── requirements.txt (opcional)
└── README.md (opcional)
```

## Paso 1: Crear pipeline.py

```python
from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(
    base_image='python:3.12',
    packages_to_install=['nombre_paquete']
)
def mi_componente(results_output: Output[Dataset] = None) -> None:
    # Importaciones dentro de la función
    import subprocess
    import json
    
    # Todo el código embebido aquí
    # No se pueden importar archivos externos
    
    # Guardar resultados
    with open(results_output.path, 'w') as f:
        f.write("Resultados de la simulación")

@dsl.pipeline(
    name='nombre-pipeline',
    description='Descripción del pipeline'
)
def mi_pipeline():
    task = mi_componente()
    task.set_display_name('Nombre del Componente')
    task.set_cpu_limit('2')
    task.set_memory_limit('2Gi')
```

## Paso 2: Crear compile_pipeline.py

```python
import kfp
from pipeline import mi_pipeline

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(
        pipeline_func=mi_pipeline,
        package_path='nombre_pipeline.yaml'
    )
    print("Pipeline compilado: nombre_pipeline.yaml")
```

## Paso 3: Compilar Pipeline

```bash
cd ejemplo_nuevo
python compile_pipeline.py
```

## Paso 4: Subir a Vertex AI

1. Abrir Google Cloud Console
2. Ir a Vertex AI → Pipelines
3. Subir archivo `nombre_pipeline.yaml`
4. Configurar parámetros
5. Ejecutar pipeline

## Reglas Importantes

### Código Embebido
- Todo el código debe estar dentro de la función del componente
- No se pueden importar archivos Python externos
- Todas las importaciones van dentro de la función

### Base Images
- `python:3.12` para la mayoría de casos
- `python:3.7` solo si el paquete lo requiere específicamente

### Packages
- SPADE: `packages_to_install=['spade==4.0.3']`
- SimFleet: `packages_to_install=['simfleet']`
- Pandas: `packages_to_install=['pandas==2.3.1']`

### Recursos
- CPU básico: `task.set_cpu_limit('1')`
- CPU intensivo: `task.set_cpu_limit('2')`
- Memoria básica: `task.set_memory_limit('1Gi')`
- Memoria intensiva: `task.set_memory_limit('2Gi')`

### Nombres
- Pipeline: usar guiones `mi-pipeline-nombre`
- Archivos: usar guiones bajos `mi_pipeline.yaml`
- Funciones: usar guiones bajos `mi_funcion()`

## Ejemplos de Referencia

- `example_simple_pandas/` - Pipeline básico con pandas
- `example2_agentes/` - Sistema multi-agente SPADE
- `example_server_spade/` - Test de servidor SPADE
- `example4_simfleet/` - Simulación de flota SimFleet