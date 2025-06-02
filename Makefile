# Valet Parking System - Docker Management

.PHONY: help build up down logs shell migrate collectstatic createsuperuser backup restore clean

# Default target
help:
	@echo "Valet Parking System - Docker Commands"
	@echo ""
	@echo "Development:"
	@echo "  make up          - Start all services in development mode"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build Docker images"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Access web container shell"
	@echo ""
	@echo "Database:"
	@echo "  make migrate     - Run database migrations"
	@echo "  make superuser   - Create Django superuser"
	@echo "  make backup      - Backup database"
	@echo "  make restore     - Restore database from backup"
	@echo ""
	@echo "Maintenance:"
	@echo "  make static      - Collect static files"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make prod        - Deploy in production mode"
	@echo ""

# Development commands
up:
	docker compose up -d
	@echo "Services started! Access at http://localhost"

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

shell:
	docker compose exec web bash

# Database commands
migrate:
	docker compose exec web python manage.py migrate

superuser:
	docker compose exec web python manage.py createsuperuser

backup:
	@echo "Creating database backup..."
	docker compose exec db pg_dump -U valet_user valet_parking > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"

restore:
	@read -p "Enter backup file name: " backup_file; \
	docker compose exec -T db psql -U valet_user valet_parking < $$backup_file

# Maintenance commands
static:
	docker compose exec web python manage.py collectstatic --noinput

clean:
	docker compose down -v
	docker system prune -f

# Production deployment
prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production deployment started!"

# Quick setup for new installations
setup:
	@echo "Setting up Valet Parking System..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make up"

# Health check
health:
	@echo "Checking service health..."
	docker compose ps
	@echo ""
	@echo "Testing web service..."
	curl -f http://localhost/health/ || echo "Web service not responding"

# View service status
status:
	docker compose ps
	@echo ""
	docker compose top
