web: sh -c 'if [ "${RUN_MIGRATIONS_ON_STARTUP:-1}" = "1" ]; then alembic upgrade head || echo "alembic failed; continuing startup"; fi; uvicorn app.main:app --host 0.0.0.0 --port $PORT'
