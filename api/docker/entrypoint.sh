#!/bin/bash

set -e

# Set UTF-8 encoding to address potential encoding issues in containerized environments
export LANG=${LANG:-en_US.UTF-8}
export LC_ALL=${LC_ALL:-en_US.UTF-8}
export PYTHONIOENCODING=${PYTHONIOENCODING:-utf-8}

if [[ "${MODE}" == "worker" ]]; then
  echo "worker"
else
  if [[ "${DEBUG}" == "true" ]]; then
    exec flask run --host=${APP_BIND_ADDRESS:-0.0.0.0} --port=${APP_PORT:-5001} --debug
  else
    exec gunicorn \
      --bind "${APP_BIND_ADDRESS:-0.0.0.0}:${APP_PORT:-5001}" \
      --workers ${SERVER_WORKER_AMOUNT:-1} \
      --worker-class ${SERVER_WORKER_CLASS:-gevent} \
      --worker-connections ${SERVER_WORKER_CONNECTIONS:-10} \
      --timeout ${GUNICORN_TIMEOUT:-200} \
      app:app
  fi
fi