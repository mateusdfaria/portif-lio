#!/bin/bash

# HospiCast Deployment Script
# This script deploys the HospiCast application using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All prerequisites are met."
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p database/backup
    mkdir -p nginx/logs
    mkdir -p nginx/ssl
    mkdir -p backend/logs
    mkdir -p backend/data
    
    print_success "Directories created."
}

# Function to check environment file
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_warning "Environment file .env not found."
        if [ -f "config.example.env" ]; then
            print_status "Copying example configuration..."
            cp config.example.env .env
            print_warning "Please edit .env file with your actual configuration before proceeding."
            print_warning "Especially update passwords and API keys!"
            read -p "Press Enter to continue after updating .env file..."
        else
            print_error "No environment configuration found. Please create .env file."
            exit 1
        fi
    fi
    
    print_success "Environment configuration checked."
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    docker-compose -f docker-compose.yml build --no-cache
    
    print_success "Images built successfully."
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    docker-compose -f docker-compose.yml up -d
    
    print_success "Services started."
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U hospicast_user -d hospicast; do sleep 2; done'
    
    # Wait for backend
    print_status "Waiting for backend..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/ >/dev/null 2>&1; do sleep 2; done'
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    timeout 60 bash -c 'until curl -f http://localhost:3000/ >/dev/null 2>&1; do sleep 2; done'
    
    print_success "All services are ready."
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Application URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Database: localhost:5432"
    echo "  Redis: localhost:6379"
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    docker-compose logs --tail=50
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose -f docker-compose.yml down
    print_success "Services stopped."
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f docker-compose.yml down -v
    docker system prune -f
    print_success "Cleanup completed."
}

# Function to backup database
backup_database() {
    print_status "Creating database backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    docker-compose exec postgres pg_dump -U hospicast_user -d hospicast > "database/backup/hospicast_${timestamp}.sql"
    print_success "Database backup created: database/backup/hospicast_${timestamp}.sql"
}

# Function to restore database
restore_database() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path as argument."
        exit 1
    fi
    
    print_status "Restoring database from $1..."
    docker-compose exec -T postgres psql -U hospicast_user -d hospicast < "$1"
    print_success "Database restored from $1"
}

# Function to show help
show_help() {
    echo "HospiCast Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the application (default)"
    echo "  start      Start services"
    echo "  stop       Stop services"
    echo "  restart    Restart services"
    echo "  status     Show service status"
    echo "  logs       Show service logs"
    echo "  backup     Backup database"
    echo "  restore    Restore database (requires backup file path)"
    echo "  cleanup    Stop services and clean up volumes"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 backup"
    echo "  $0 restore database/backup/hospicast_20240101_120000.sql"
}

# Main function
main() {
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            create_directories
            check_environment
            build_images
            start_services
            wait_for_services
            show_status
            ;;
        start)
            start_services
            wait_for_services
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services
            wait_for_services
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database "$2"
            ;;
        cleanup)
            cleanup
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
