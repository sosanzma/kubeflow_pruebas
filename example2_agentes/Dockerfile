FROM python:3.12-slim

# Instalar dependencias del sistema necesarias para SPADE
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Health check para verificar que SPADE está disponible
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import spade; print('SPADE OK')" || exit 1

# Comando por defecto (será sobrescrito por Kubeflow)
CMD ["echo", "SPADE container ready for Kubeflow execution"]