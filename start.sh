#!/bin/bash

set -e

# Wait for the database service to be available
wait_for_db_service() {
  local host="$1"
  local port="$2"

  echo "Waiting for $host:$port to be available..."

  while true; do
    # Check if the port is open using /dev/tcp
    if bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
      echo "$host:$port is available!"
      return 0
    fi
    echo "Still waiting for $host:$port..."
    sleep 3
  done
}

# Wait for MySQL to be ready
MYSQL_HOST=${MYSQL_HOST:-mysql}
MYSQL_PORT=${MYSQL_PORT:-3306}
wait_for_db_service "$MYSQL_HOST" "$MYSQL_PORT"

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Start Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=3000
