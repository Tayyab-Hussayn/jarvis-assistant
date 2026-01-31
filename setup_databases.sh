#!/bin/bash
"""
JARVIS Database Setup Script
"""

echo "🗄️  Setting up JARVIS Databases..."
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is required but not installed"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python database dependencies..."
pip install -r requirements_db.txt

# Start databases with Docker Compose
echo "🚀 Starting database containers..."
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to initialize..."
sleep 10

# Check database status
echo "🔍 Checking database connections..."
python -c "
import asyncio
import sys
sys.path.append('.')

from core.database.database_manager import db_manager

async def check_databases():
    await db_manager.initialize()
    status = await db_manager.health_check()
    
    print('Database Status:')
    print(f'  PostgreSQL: {\"✅\" if status[\"postgres\"] else \"❌\"}')
    print(f'  Qdrant:     {\"✅\" if status[\"qdrant\"] else \"❌\"}')
    print(f'  Redis:      {\"✅\" if status[\"redis\"] else \"❌\"}')
    print(f'  Overall:    {\"✅\" if status[\"overall\"] else \"❌\"}')
    
    if status['overall']:
        print('\\n🎉 All databases are ready!')
        return True
    else:
        print('\\n❌ Some databases failed to connect')
        return False

success = asyncio.run(check_databases())
exit(0 if success else 1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database setup complete!"
    echo ""
    echo "Available services:"
    echo "  PostgreSQL: localhost:5432 (jarvis/jarvis_secure_2024)"
    echo "  Qdrant:     localhost:6333"
    echo "  Redis:      localhost:6379"
    echo ""
    echo "To stop databases: docker-compose down"
    echo "To view logs: docker-compose logs -f"
else
    echo ""
    echo "❌ Database setup failed!"
    echo "Check logs with: docker-compose logs"
fi
