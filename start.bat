@echo off
setlocal

if "%1"=="" (
    echo Please specify environment: dev or prod
    echo Usage: start.bat [dev^|prod]
    exit /b 1
)

if "%1"=="dev" (
    echo Starting development environment...
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d --build
) else if "%1"=="prod" (
    echo Starting production environment...
    docker-compose -f docker-compose.prod.yml up -d --build
) else (
    echo Invalid environment. Use 'dev' or 'prod'
    exit /b 1
)

echo Cleaning up unused Docker resources...
docker system prune -f

echo Done!
