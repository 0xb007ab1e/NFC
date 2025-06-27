#!/bin/bash
set -e

echo "Starting NFC Server entrypoint..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! nc -z "${DATABASE_HOST:-db}" "${DATABASE_PORT:-5432}"; do
    echo "Waiting for database connection..."
    sleep 2
done
echo "Database connection established!"

# Run database migrations
echo "Running database migrations..."
if [ -f "/app/db/migrations/alembic.ini" ]; then
    cd /app
    python -m alembic -c db/migrations/alembic.ini upgrade head
    echo "Database migrations completed successfully!"
else
    echo "No Alembic configuration found, skipping migrations..."
fi

# Create initial data if needed
if [ "${CREATE_INITIAL_DATA:-false}" = "true" ]; then
    echo "Creating initial data..."
    python -c "
import asyncio
from server.db.config import create_tables
asyncio.run(create_tables())
print('Initial data creation completed!')
"
fi

# Start the application
echo "Starting NFC Server application..."
exec "$@"
