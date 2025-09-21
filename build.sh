#!/usr/bin/env bash
# Build script for Render

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setting up database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"

echo "Build completed successfully!"