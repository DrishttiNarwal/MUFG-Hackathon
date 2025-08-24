@echo off
REM Script for local development

REM Stop any running containers
docker-compose down

REM Build and start containers in development mode
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

REM Remove unused images and containers
docker system prune -f
