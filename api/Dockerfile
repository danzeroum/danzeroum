FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install tracker package first (cache layer)
COPY tracker/pyproject.toml ./tracker/pyproject.toml
COPY tracker/danzeroum_tracker ./tracker/danzeroum_tracker
COPY tracker/sql ./tracker/sql
RUN pip install --no-cache-dir ./tracker

# Install API dependencies
COPY api/requirements.txt ./api/requirements.txt
RUN pip install --no-cache-dir -r ./api/requirements.txt

# Copy API source
COPY api ./api
RUN chmod +x ./api/entrypoint.sh

# Run as non-root
RUN useradd --create-home --uid 10001 apiuser
USER apiuser

EXPOSE 8000
# O entrypoint aplica as migrations antes de subir o uvicorn (o CMD vira seus args).
ENTRYPOINT ["./api/entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
