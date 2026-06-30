#!/bin/sh
# Entrypoint da API: aplica as migrations e então sobe o uvicorn.
# Se a migration falhar, o contêiner NÃO sobe (problema fica visível; evita rodar
# a API contra um schema meio-migrado).
set -e

echo "[entrypoint] aplicando migrations..."
python -m api.migrate

echo "[entrypoint] iniciando API..."
exec "$@"
