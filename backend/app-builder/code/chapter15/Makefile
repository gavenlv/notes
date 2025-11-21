# Variables
.PHONY: install init-db seed-data run test build-docker start-docker stop-docker logs-docker shell-docker clean

# Install dependencies
install:
	pip install -r requirements.txt

# Initialize database tables
init-db:
	python -m flask init-db

# Seed sample data into database
seed-data:
	python -m flask seed-data

# Run development server
run:
	python run.py

# Run tests
test:
	python -m pytest tests/

# Build Docker image
build-docker:
	docker-compose build

# Start services with Docker Compose
start-docker:
	docker-compose up -d

# Stop services
stop-docker:
	docker-compose down

# View logs
logs-docker:
	docker-compose logs -f

# Enter container shell
shell-docker:
	docker-compose exec web bash

# Clean up
clean:
	docker-compose down -v
	rm -rf migrations/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete