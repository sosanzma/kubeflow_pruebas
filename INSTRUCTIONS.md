# Guía Completa: Ejecutar Código Python en Kubeflow

Esta guía te llevará paso a paso desde código Python hasta un pipeline ejecutándose en Google Cloud Vertex AI.

## 📋 Requisitos Previos

- Python 3.12+
- Docker Desktop instalado
- Cuenta en Docker Hub (gratuita)
- Cuenta en Google Cloud (con créditos gratuitos)

## 🛠️ Paso 1: Preparar el Código Python

### 1.1 Crear el script de procesamiento
Crea `example1/preprocess.py`:

```python
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
df['sepal_area'] = df['sepal_length'] * df['sepal_width']
df.to_csv('/output/processed.csv', index=False)
```

### 1.2 Crear requirements.txt
Crea `example1/requirements.txt`:

```txt
pandas==2.3.1
```

## 🐳 Paso 2: Crear la Imagen Docker

### 2.1 Crear Dockerfile
Crea `example1/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY preprocess.py .

RUN mkdir -p /output

CMD ["python", "preprocess.py"]
```

### 2.2 Construir la imagen
```bash
cd example1
docker build -t preprocess:latest .
```

### 2.3 Probar localmente
```bash
docker run --rm -v ${PWD}/output:/output preprocess:latest
```

## 📦 Paso 3: Subir a Docker Hub

### 3.1 Login en Docker Hub
```bash
docker login
```

### 3.2 Tag y push
```bash
# Reemplaza TU-USUARIO con tu username de Docker Hub
docker tag preprocess:latest TU-USUARIO/preprocess:latest
docker push TU-USUARIO/preprocess:latest
```

## 🔧 Paso 4: Crear el Pipeline de Kubeflow

### 4.1 Instalar Kubeflow Pipelines SDK
```bash
pip install kfp
```

### 4.2 Crear pipeline.py
Crea `example1/pipeline.py`:

```python
from kfp import dsl

@dsl.component(base_image='TU-USUARIO/preprocess:latest')
def preprocess_data() -> str:
    return '/output/processed.csv'

@dsl.pipeline(
    name='simple-preprocessing-pipeline',
    description='Lee un CSV y hace preprocesamiento con pandas'
)
def preprocessing_pipeline():
    preprocess_task = preprocess_data()
    preprocess_task.set_display_name('Preprocess Data')
```

### 4.3 Crear script de compilación
Crea `example1/compile_pipeline.py`:

```python
import kfp
from pipeline import preprocessing_pipeline

if __name__ == '__main__':
    kfp.compiler.Compiler().compile(
        pipeline_func=preprocessing_pipeline,
        package_path='preprocessing_pipeline.yaml'
    )
    print("Pipeline compilado exitosamente en: preprocessing_pipeline.yaml")
```

### 4.4 Compilar el pipeline
```bash
python compile_pipeline.py
```

Esto genera `preprocessing_pipeline.yaml` listo para Kubeflow.

## ☁️ Paso 5: Ejecutar en Google Cloud

### 5.1 Configurar Google Cloud

1. **Crear proyecto en Google Cloud Console**
   - Ve a https://console.cloud.google.com
   - Crea un nuevo proyecto o selecciona uno existente

2. **Activar APIs necesarias**
   - Vertex AI API
   - Container Registry API (si usas GCR en lugar de Docker Hub)

3. **Configurar facturación**
   - Activa la cuenta de facturación (obtienes $300 de crédito gratuito)

### 5.2 Acceder a Vertex AI Pipelines

1. **Navegar a Vertex AI**
   - En Google Cloud Console: Vertex AI → Pipelines

2. **Subir el pipeline**
   - Click en "Upload Pipeline"
   - Selecciona tu archivo `preprocessing_pipeline.yaml`
   - Dale un nombre y descripción

3. **Crear y ejecutar un run**
   - Click en "Create run"
   - Configura los parámetros si es necesario
   - Click en "Submit"

### 5.3 Monitorear la ejecución

- Ve el progreso en tiempo real en la UI de Vertex AI
- Revisa logs y outputs de cada componente
- Descarga los artefactos generados

## 🔍 Verificación y Debugging

### Verificar imagen Docker localmente
```bash
docker run --rm TU-USUARIO/preprocess:latest
```

### Verificar pipeline compilado
```bash
# El YAML debe existir y no tener errores de sintaxis
cat preprocessing_pipeline.yaml
```

### Logs en Google Cloud
- Ve a Cloud Logging para logs detallados
- Usa Vertex AI Experiments para tracking

## 📁 Estructura Final del Proyecto

```
kubeflow/
├── README.md
├── INSTRUCTIONS.md
└── example1/
    ├── preprocess.py
    ├── requirements.txt
    ├── Dockerfile
    ├── pipeline.py
    ├── compile_pipeline.py
    └── preprocessing_pipeline.yaml
```

## 🎯 Próximos Pasos

1. **Añadir más componentes** al pipeline
2. **Pasar parámetros** entre componentes
3. **Usar artifacts** para persistir datos
4. **Implementar conditional logic**
5. **Integrar con ML frameworks** (scikit-learn, TensorFlow, etc.)

## 🐛 Problemas Comunes

### Error: "ContainerOp no existe"
- **Solución**: Usar `@dsl.component` en lugar de `ContainerOp` (KFP v2)

### Error: "Image not found"
- **Solución**: Verificar que la imagen esté en Docker Hub y sea pública

### Error de permisos en Google Cloud
- **Solución**: Verificar que las APIs estén activadas y tengas permisos

### Pipeline no ejecuta
- **Solución**: Revisar logs en Cloud Logging y verificar la sintaxis del YAML

## 📚 Recursos Adicionales

- [Documentación oficial de Kubeflow](https://kubeflow.org/docs/)
- [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines)
- [KFP SDK Reference](https://kubeflow-pipelines.readthedocs.io/)
- [Docker Hub](https://hub.docker.com/)

¡Felicidades! Ya sabes cómo ejecutar código Python en Kubeflow desde cero hasta producción. 🚀