FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instala dependências primeiro (cache de camada).
COPY pyproject.toml ./
COPY danzeroum_tracker ./danzeroum_tracker
COPY sql ./sql
RUN pip install --no-cache-dir .

# Roda como usuário não-root.
RUN useradd --create-home --uid 10001 tracker
USER tracker

ENTRYPOINT ["python", "-m", "danzeroum_tracker"]
CMD ["schedule"]
