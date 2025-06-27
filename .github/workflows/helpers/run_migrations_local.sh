#!/bin/bash

set -e

# Create temporary database directory
mkdir -p /tmp/test_db

# Change to the migrations directory
cd server/db/migrations

# Create a temporary alembic.ini for testing
cp alembic.ini alembic_test.ini
sed -i 's|sqlite:///../../data/nfc_data.db|sqlite:////tmp/test_db/test.db|g' alembic_test.ini

# Run migrations
echo "Running migrations against a clean SQLite database..."
alembic -c alembic_test.ini upgrade head

# Verify success
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
else
    echo "❌ Migration failed!"
    exit 1
fi

# Clean up temporary config
rm alembic_test.ini
