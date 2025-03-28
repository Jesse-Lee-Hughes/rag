#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists docker; then
    echo "Docker is required but not installed."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "Docker Compose is required but not installed."
    exit 1
fi

# Function to start the development environment
start_dev() {
    echo "Starting development environment..."
    docker-compose -f docker-compose.dev.yml up --build
}

# Function to stop the development environment
stop_dev() {
    echo "Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
}

# Function to rebuild a specific service
rebuild_service() {
    if [ -z "$1" ]; then
        echo "Please specify a service to rebuild (backend, ui, or db)"
        exit 1
    fi
    echo "Rebuilding $1..."
    docker-compose -f docker-compose.dev.yml up -d --build $1
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose -f docker-compose.dev.yml logs -f $1
    fi
}

# Main menu
case "$1" in
    "start")
        start_dev
        ;;
    "stop")
        stop_dev
        ;;
    "rebuild")
        rebuild_service $2
        ;;
    "logs")
        show_logs $2
        ;;
    *)
        echo "Usage: $0 {start|stop|rebuild|logs}"
        echo "  start   - Start the development environment"
        echo "  stop    - Stop the development environment"
        echo "  rebuild - Rebuild a specific service (backend|ui|db)"
        echo "  logs    - Show logs (optional: specify service)"
        exit 1
        ;;
esac 