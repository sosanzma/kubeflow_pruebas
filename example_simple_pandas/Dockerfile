FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Health check para verificar que pandas está disponible
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pandas; print('Pandas OK')" || exit 1

# Comando por defecto (será sobrescrito por Kubeflow)
CMD ["echo", "Pandas container ready for Kubeflow execution"]