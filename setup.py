#!/usr/bin/env python3
"""
Quick Start Script
Sets up the environment and starts the services
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)


def main():
    """Main setup function"""
    print(
        """
    ╔═══════════════════════════════════════════════════════════╗
    ║   AI Agent Orchestration System - Quick Start Script      ║
    ║                                                           ║
    ║   This script will set up and start the application      ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    )

    # Check if .env exists
    if not os.path.exists(".env"):
        print("\n⚠️  .env file not found!")
        print("📝 Creating .env from .env.example...")
        run_command("cp .env.example .env", "Copy environment template")
        print("\n⚠️  Please edit .env file with your API keys before continuing!")
        print("   Required: MISTRAL_API_KEY, SECRET_KEY, DATABASE_URL")
        response = input("\nHave you configured the .env file? (y/n): ")
        if response.lower() != "y":
            print("Please configure .env and run this script again.")
            sys.exit(0)

    # Start dependencies with Docker Compose
    print("\n🐳 Starting PostgreSQL and Redis...")
    run_command("docker-compose up -d postgres redis", "Start database services")

    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    import time

    time.sleep(5)

    # Initialize database
    print("\n🗄️  Initializing database...")
    run_command(
        'python3 -c "from app.core.database import init_db; init_db()"',
        "Initialize database tables",
    )

    print(
        """
    
    ✅ Setup complete!
    
    🚀 To start the application, run these commands in separate terminals:
    
    Terminal 1 (API Server):
        uvicorn app.main:app --reload --port 8000
    
    Terminal 2 (Celery Worker):
        celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    
    📚 Documentation will be available at:
        - Swagger UI: http://localhost:8000/docs
        - ReDoc: http://localhost:8000/redoc
    
    🔍 Health check:
        curl http://localhost:8000/health
    """
    )


if __name__ == "__main__":
    main()
