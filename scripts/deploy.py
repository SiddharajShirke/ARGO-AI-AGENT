"""
Deployment Script for Indian Ocean Argo AI Agent
Handles production deployment, environment setup, and service management
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_command(command, description="", check=True, cwd=None):
    """Run a command with proper error handling."""
    print(f"⚙️ {description or command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True,
            cwd=cwd or PROJECT_ROOT
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def build_docker_images():
    """Build Docker images for production."""
    print("🐳 Building Docker images...")
    
    # Build backend image
    dockerfile_backend = PROJECT_ROOT / "Dockerfile.backend"
    if not dockerfile_backend.exists():
        print("Creating backend Dockerfile...")
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app/main.py", "--mode", "backend"]
"""
        with open(dockerfile_backend, 'w') as f:
            f.write(dockerfile_content)
    
    if not run_command(
        "docker build -f Dockerfile.backend -t argo-ai-backend .",
        "Building backend image"
    ):
        return False
    
    # Build dashboard image
    dockerfile_dashboard = PROJECT_ROOT / "Dockerfile.dashboard"
    if not dockerfile_dashboard.exists():
        print("Creating dashboard Dockerfile...")
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY config/ ./config/

# Expose port
EXPOSE 8501

# Run dashboard
CMD ["python", "app/main.py", "--mode", "dashboard"]
"""
        with open(dockerfile_dashboard, 'w') as f:
            f.write(dockerfile_content)
    
    return run_command(
        "docker build -f Dockerfile.dashboard -t argo-ai-dashboard .",
        "Building dashboard image"
    )


def create_production_compose():
    """Create production docker-compose file."""
    print("📄 Creating production docker-compose.yml...")
    
    compose_content = """version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: indian_ocean_argo
      POSTGRES_USER: argo_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./config/database_migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U argo_user -d indian_ocean_argo"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  chromadb:
    image: chromadb/chroma:0.4.24
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_HTTP_PORT=8001
    volumes:
      - chromadb_data:/chroma/chroma
    ports:
      - "8001:8001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: argo-ai-backend
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DB_HOST=postgres
      - REDIS_HOST=redis
      - CHROMADB_HOST=chromadb
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      chromadb:
        condition: service_healthy
    restart: unless-stopped

  dashboard:
    image: argo-ai-dashboard
    environment:
      - ENVIRONMENT=production
      - API_HOST=backend
      - DASHBOARD_HOST=0.0.0.0
    ports:
      - "8501:8501"
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - dashboard
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
"""
    
    prod_compose_file = PROJECT_ROOT / "docker-compose.prod.yml"
    with open(prod_compose_file, 'w') as f:
        f.write(compose_content)
    
    print("✅ Production docker-compose.yml created")
    return True


def create_nginx_config():
    """Create Nginx configuration for reverse proxy."""
    print("🌐 Creating Nginx configuration...")
    
    nginx_content = """events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream dashboard {
        server dashboard:8501;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Dashboard routes
        location / {
            proxy_pass http://dashboard;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
"""
    
    nginx_file = PROJECT_ROOT / "nginx.conf"
    with open(nginx_file, 'w') as f:
        f.write(nginx_content)
    
    print("✅ Nginx configuration created")
    return True


def create_env_production():
    """Create production environment file."""
    print("🔐 Creating production environment template...")
    
    env_content = """# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=indian_ocean_argo
DB_USER=argo_user
DB_PASSWORD=your_secure_db_password_here

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# ChromaDB Configuration
CHROMADB_HOST=chromadb
CHROMADB_PORT=8001

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your_very_secure_secret_key_here_min_32_chars
"""
    
    env_file = PROJECT_ROOT / ".env.production"
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Production environment template created")
    print("⚠️  Please update .env.production with actual secure values")
    return True


def deploy_production():
    """Deploy to production."""
    print("🚀 Deploying to production...")
    
    # Build images
    if not build_docker_images():
        return False
    
    # Start production services
    return run_command(
        "docker-compose -f docker-compose.prod.yml --env-file .env.production up -d",
        "Starting production services"
    )


def deploy_staging():
    """Deploy to staging environment."""
    print("🧪 Deploying to staging...")
    
    # Create staging environment
    env_content = """ENVIRONMENT=staging
DEBUG=true
LOG_LEVEL=debug
DB_PASSWORD=staging_password
SECRET_KEY=staging_secret_key_change_me
"""
    
    env_file = PROJECT_ROOT / ".env.staging"
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    # Build and deploy
    if not build_docker_images():
        return False
    
    return run_command(
        "docker-compose -f docker-compose.prod.yml --env-file .env.staging up -d",
        "Starting staging services"
    )


def stop_services(env="production"):
    """Stop running services."""
    env_file = f".env.{env}"
    return run_command(
        f"docker-compose -f docker-compose.prod.yml --env-file {env_file} down",
        f"Stopping {env} services"
    )


def show_logs(env="production", service=None):
    """Show service logs."""
    env_file = f".env.{env}"
    service_arg = f" {service}" if service else ""
    return run_command(
        f"docker-compose -f docker-compose.prod.yml --env-file {env_file} logs -f{service_arg}",
        f"Showing {env} logs"
    )


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deployment tool for Argo AI Agent")
    parser.add_argument(
        "action",
        choices=[
            "setup", "build", "deploy-prod", "deploy-staging",
            "stop-prod", "stop-staging", "logs", "status"
        ],
        help="Deployment action"
    )
    parser.add_argument("--service", help="Specific service for logs")
    parser.add_argument("--env", default="production", help="Environment")
    
    args = parser.parse_args()
    
    print("🚀 Argo AI Agent - Deployment Tool")
    print("=" * 50)
    
    if args.action == "setup":
        print("Setting up production configuration...")
        create_production_compose()
        create_nginx_config()
        create_env_production()
        print("✅ Production setup complete")
        
    elif args.action == "build":
        build_docker_images()
        
    elif args.action == "deploy-prod":
        deploy_production()
        
    elif args.action == "deploy-staging":
        deploy_staging()
        
    elif args.action == "stop-prod":
        stop_services("production")
        
    elif args.action == "stop-staging":
        stop_services("staging")
        
    elif args.action == "logs":
        show_logs(args.env, args.service)
        
    elif args.action == "status":
        env_file = f".env.{args.env}"
        run_command(
            f"docker-compose -f docker-compose.prod.yml --env-file {env_file} ps",
            f"Checking {args.env} status"
        )


if __name__ == "__main__":
    main()
