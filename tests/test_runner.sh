#!/bin/bash

# AssetOpsBench Test Runner Script
# Supports both local and Docker execution

set -e  # Exit on any error

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

# Function to check if running in Docker
is_docker() {
    [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Get project root
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    cd "$PROJECT_ROOT"
    
    print_status "Project root: $PROJECT_ROOT"
    
    # Check if src directory exists
    if [ ! -d "src" ]; then
        print_error "src directory not found. Are you in the AssetOpsBench root directory?"
        exit 1
    fi
    
    # Check if scenarios directory exists
    if [ ! -d "scenarios" ]; then
        print_warning "scenarios directory not found. Some tests may fail."
    fi
    
    print_success "Environment setup complete"
}

# Function to run local tests
run_local_tests() {
    print_status "Running tests locally..."
    
    # Check Python availability
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    
    # Check if virtual environment should be activated
    if [ -f "venv/bin/activate" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run quick test first
    print_status "Running quick validation test..."
    python3 tests/run_local_tests.py
    
    if [ $? -eq 0 ]; then
        print_success "Quick test passed!"
        
        # Run full test suite
        print_status "Running full test suite..."
        python3 tests/run_all_tests.py
        
        if [ $? -eq 0 ]; then
            print_success "All tests passed!"
        else
            print_error "Some tests failed!"
            exit 1
        fi
    else
        print_error "Quick test failed. Please check your setup."
        exit 1
    fi
}

# Function to run Docker tests
run_docker_tests() {
    print_status "Running tests in Docker..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install docker-compose."
        exit 1
    fi
    
    # Build and run tests
    print_status "Building Docker test image..."
    docker-compose -f tests/docker-compose.test.yml build
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully!"
        
        print_status "Running tests in Docker container..."
        docker-compose -f tests/docker-compose.test.yml run --rm assetopsbench-tests
        
        if [ $? -eq 0 ]; then
            print_success "Docker tests completed successfully!"
        else
            print_error "Docker tests failed!"
            exit 1
        fi
    else
        print_error "Failed to build Docker image!"
        exit 1
    fi
}

# Function to run specific test suite
run_specific_tests() {
    local test_suite="$1"
    print_status "Running specific test suite: $test_suite"
    
    if is_docker; then
        python3 tests/run_all_tests.py "$test_suite"
    else
        # Check if we should use Docker
        if [ "$USE_DOCKER" = "true" ]; then
            docker-compose -f tests/docker-compose.test.yml run --rm assetopsbench-tests python3 tests/run_all_tests.py "$test_suite"
        else
            python3 tests/run_all_tests.py "$test_suite"
        fi
    fi
}

# Function to show help
show_help() {
    echo "AssetOpsBench Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_SUITE]"
    echo ""
    echo "Options:"
    echo "  -d, --docker     Run tests in Docker container"
    echo "  -l, --local      Run tests locally (default)"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Test Suites:"
    echo "  scenario_validation    Run scenario validation tests only"
    echo "  real_scenarios         Run real scenario file tests only"
    echo "  all                    Run all tests (default)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run all tests locally"
    echo "  $0 --docker                 # Run all tests in Docker"
    echo "  $0 scenario_validation      # Run scenario validation tests locally"
    echo "  $0 --docker real_scenarios  # Run real scenarios tests in Docker"
    echo ""
}

# Main function
main() {
    local use_docker=false
    local test_suite="all"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--docker)
                use_docker=true
                shift
                ;;
            -l|--local)
                use_docker=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            scenario_validation|real_scenarios|all)
                test_suite="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Setup environment
    setup_environment
    
    # Run tests based on mode
    if [ "$use_docker" = true ]; then
        export USE_DOCKER=true
        if [ "$test_suite" = "all" ]; then
            run_docker_tests
        else
            run_specific_tests "$test_suite"
        fi
    else
        export USE_DOCKER=false
        if [ "$test_suite" = "all" ]; then
            run_local_tests
        else
            run_specific_tests "$test_suite"
        fi
    fi
}

# Run main function with all arguments
main "$@"
