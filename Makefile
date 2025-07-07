# =============================================================================
# EVA-Dev Makefile
# Development and deployment automation
# =============================================================================

.PHONY: help dev prod test clean build deploy logs stop restart

# Default target
help:
	@echo "EVA-Dev Development Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-build    - Build and start development environment"
	@echo "  make logs         - View development logs"
	@echo "  make stop         - Stop all services"
	@echo "  make restart      - Restart all services"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend- Run frontend tests only"
	@echo "  make test-integration - Run integration tests"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-build   - Build and start production environment"
	@echo "  make deploy       - Deploy to production"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean up containers and volumes"
	@echo "  make build        - Build all images"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code"

# =============================================================================
# Development Commands
# =============================================================================

dev:
	@echo "🚀 Starting EVA-Dev development environment..."
	docker-compose up -d
	@echo "✅ Development environment started!"
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend API: http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

dev-build:
	@echo "🔨 Building and starting development environment..."
	docker-compose up -d --build
	@echo "✅ Development environment built and started!"

logs:
	@echo "📋 Viewing development logs..."
	docker-compose logs -f

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ All services stopped!"

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart
	@echo "✅ All services restarted!"

# =============================================================================
# Testing Commands
# =============================================================================

test:
	@echo "🧪 Running all tests..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down
	@echo "✅ All tests completed!"

test-backend:
	@echo "🧪 Running backend tests..."
	docker-compose -f docker-compose.test.yml up backend-test --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down
	@echo "✅ Backend tests completed!"

test-frontend:
	@echo "🧪 Running frontend tests..."
	docker-compose -f docker-compose.test.yml up frontend-test --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down
	@echo "✅ Frontend tests completed!"

test-integration:
	@echo "🧪 Running integration tests..."
	docker-compose -f docker-compose.test.yml up integration-test --build --abort-on-container-exit
	docker-compose -f docker-compose.test.yml down
	@echo "✅ Integration tests completed!"

# =============================================================================
# Production Commands
# =============================================================================

prod:
	@echo "🚀 Starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"

prod-build:
	@echo "🔨 Building and starting production environment..."
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "✅ Production environment built and started!"

deploy:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  Make sure you have:"
	@echo "   - Set all environment variables"
	@echo "   - SSL certificates in nginx/ssl/"
	@echo "   - Proper DNS configuration"
	@read -p "Continue with deployment? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f docker-compose.prod.yml pull
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "✅ Production deployment completed!"

# =============================================================================
# Maintenance Commands
# =============================================================================

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker-compose -f docker-compose.test.yml down -v --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

build:
	@echo "🔨 Building all images..."
	docker-compose build
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ All images built!"

lint:
	@echo "🔍 Running code linting..."
	@echo "Backend linting..."
	cd backend && python -m flake8 app/
	cd backend && python -m mypy app/
	@echo "Frontend linting..."
	cd frontend && npm run lint
	@echo "✅ Linting completed!"

format:
	@echo "✨ Formatting code..."
	@echo "Backend formatting..."
	cd backend && python -m black app/
	cd backend && python -m isort app/
	@echo "Frontend formatting..."
	cd frontend && npm run format
	@echo "✅ Code formatting completed!"

# =============================================================================
# Development Helpers
# =============================================================================

shell-backend:
	@echo "🐚 Opening backend shell..."
	docker-compose exec backend bash

shell-frontend:
	@echo "🐚 Opening frontend shell..."
	docker-compose exec frontend sh

shell-redis:
	@echo "🐚 Opening Redis CLI..."
	docker-compose exec redis redis-cli

db-reset:
	@echo "🗄️ Resetting database..."
	docker-compose exec redis redis-cli FLUSHALL
	@echo "✅ Database reset completed!"

health:
	@echo "🏥 Checking service health..."
	@echo "Backend health:"
	curl -f http://localhost:8000/health || echo "❌ Backend unhealthy"
	@echo ""
	@echo "Frontend health:"
	curl -f http://localhost:3000/health || echo "❌ Frontend unhealthy"
	@echo ""
	@echo "Redis health:"
	docker-compose exec redis redis-cli ping || echo "❌ Redis unhealthy"

# =============================================================================
# SSL Certificate Generation (for development)
# =============================================================================

ssl-dev:
	@echo "🔐 Generating development SSL certificates..."
	mkdir -p nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/fixverse.key \
		-out nginx/ssl/fixverse.crt \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
	@echo "✅ Development SSL certificates generated!"

# =============================================================================
# Monitoring
# =============================================================================

monitor:
	@echo "📊 Service monitoring..."
	@echo "Docker containers:"
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "Resource usage:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
