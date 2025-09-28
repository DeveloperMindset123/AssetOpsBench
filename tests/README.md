# AssetOpsBench Tests

This directory contains comprehensive unit tests for the AssetOpsBench scenario validation system, as requested in [GitHub issue #30](https://github.com/IBM/AssetOpsBench/issues/30).

## Test Structure

- `test_scenario_validation.py` - Core scenario validation tests
- `test_real_scenarios.py` - Tests for actual scenario files
- `run_tests.py` - Basic test runner
- `run_all_tests.py` - Comprehensive test runner

## Running Tests

### Local Execution

#### Option 1: Using Conda (Recommended for macOS)

1. **Install Conda via Homebrew:**

   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Install conda via Homebrew
   brew install --cask miniconda

   # Add conda to your PATH (add to ~/.zshrc or ~/.bash_profile)
   echo 'export PATH="/opt/homebrew/Caskroom/miniconda/base/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc

   # Initialize conda
   conda init zsh  # or bash if using bash
   ```

2. **Create Conda Environment:**

   ```bash
   # Ensure you're in the AssetOpsBench root directory
   cd /path/to/AssetOpsBench

   # Create conda environment with Python 3.12
   conda create -n assetopsbench python=3.12 -y
   conda activate assetopsbench

   # Install dependencies
   pip install -r benchmark/basic_requirements.txt
   ```

3. **Run Tests:**

   ```bash
   # Activate environment (if not already active)
   conda activate assetopsbench

   # Run all tests
   python tests/run_all_tests.py

   # Or run quick test first
   python tests/run_local_tests.py
   ```

#### Option 2: Using Python Virtual Environment

1. **Setup Virtual Environment:**

   ```bash
   # Ensure you're in the AssetOpsBench root directory
   cd /path/to/AssetOpsBench

   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows

   # Install dependencies
   pip install -r benchmark/basic_requirements.txt
   ```

2. **Run Tests:**

   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate

   # Run all tests
   python tests/run_all_tests.py

   # Or run quick test first
   python tests/run_local_tests.py
   ```

#### Running Specific Test Suites

```bash
# Scenario validation tests only
python tests/run_all_tests.py scenario_validation

# Real scenario files tests only
python tests/run_all_tests.py real_scenarios

# Individual test files
python -m unittest tests.test_scenario_validation -v
python -m unittest tests.test_real_scenarios -v

# Using the test runner script
./tests/test_runner.sh scenario_validation
```

### Docker Execution

#### Option 1: Simple Docker Setup (Recommended - Fast & Reliable)

```bash
# Build and run tests in one command
docker-compose -f tests/docker-compose.simple.yml up --build

# Or run specific test suites
docker-compose -f tests/docker-compose.simple.yml run --rm assetopsbench-tests-simple

# Using Docker directly
docker build -f tests/Dockerfile.simple -t assetopsbench-tests-simple .
docker run --rm assetopsbench-tests-simple
```

#### Option 2: Minimal Docker Setup (Fastest - Testing Only)

```bash
# Build with minimal dependencies
docker build -f tests/Dockerfile.minimal -t assetopsbench-tests-minimal .

# Run tests
docker run --rm assetopsbench-tests-minimal

# Or with volume mounting for development
docker run --rm -v $(pwd)/src:/app/src -v $(pwd)/tests:/app/tests assetopsbench-tests-minimal
```

#### Option 3: Full Docker Setup (Complete Environment)

```bash
# Build and run with all dependencies (requires build tools)
docker-compose -f tests/docker-compose.test.yml up --build

# Or run specific test suites
docker-compose -f tests/docker-compose.test.yml run --rm assetopsbench-tests

# Using Docker directly
docker build -f tests/Dockerfile.test -t assetopsbench-tests .
docker run --rm assetopsbench-tests
```

#### Docker Test Runner Script

```bash
# Run all tests in Docker
./tests/test_runner.sh --docker

# Run specific test suite in Docker
./tests/test_runner.sh --docker scenario_validation

# Run real scenarios tests in Docker
./tests/test_runner.sh --docker real_scenarios
```

## Test Coverage

The tests cover:

- ✅ Scenario validation functionality
- ✅ FMSR scenario 113 (Evaporator Water side fouling)
- ✅ TSFM scenario 217 (Chiller 9 forecasting)
- ✅ Real scenario files validation
- ✅ Edge cases and error handling
- ✅ JSON/JSONL file parsing
- ✅ Pydantic model validation

## Expected Output

When tests pass, you should see:

```
🧪 Running All AssetOpsBench Tests...
============================================================
test_valid_fmsr_scenario (tests.test_scenario_validation.TestScenarioValidation) ... ok
test_valid_tsfm_scenario (tests.test_scenario_validation.TestScenarioValidation) ... ok
...
✅ All tests passed! Scenario validation is working correctly.
```

## Troubleshooting

### Local Environment Issues

1. **Import Errors:**

   ```bash
   # Ensure you're in the AssetOpsBench root directory
   cd /path/to/AssetOpsBench

   # For conda users
   conda activate assetopsbench

   # For virtual environment users
   source venv/bin/activate
   ```

2. **Missing Dependencies:**

   ```bash
   # Install required packages
   pip install -r benchmark/basic_requirements.txt

   # Or for minimal testing only
   pip install pydantic pathlib
   ```

3. **Permission Errors (macOS):**

   ```bash
   # Make test scripts executable
   chmod +x tests/test_runner.sh
   chmod +x tests/run_tests.py
   chmod +x tests/run_all_tests.py
   ```

4. **Python Path Issues:**

   ```bash
   # Add src to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

   # Or run with explicit path
   PYTHONPATH=$(pwd)/src python tests/run_all_tests.py
   ```

### Docker Issues

1. **Docker Build Failures:**

   ```bash
   # Use the simple Docker setup instead
   docker-compose -f tests/docker-compose.simple.yml up --build

   # Or use minimal setup
   docker build -f tests/Dockerfile.minimal -t assetopsbench-minimal .
   ```

2. **Permission Denied Errors:**

   ```bash
   # Make sure Docker is running
   docker --version

   # Check Docker daemon status
   docker info
   ```

3. **Volume Mount Issues:**
   ```bash
   # Use absolute paths for volume mounting
   docker run --rm -v /absolute/path/to/AssetOpsBench/src:/app/src assetopsbench-minimal
   ```

### Environment-Specific Issues

1. **macOS with Apple Silicon (M1/M2):**

   ```bash
   # Use conda for better compatibility
   brew install --cask miniconda
   conda create -n assetopsbench python=3.12 -y
   ```

2. **Linux/WSL:**

   ```bash
   # Use virtual environment
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Windows:**
   ```bash
   # Use conda or PowerShell
   conda create -n assetopsbench python=3.12 -y
   conda activate assetopsbench
   ```

### Quick Verification

```bash
# Test if everything is set up correctly
python tests/run_local_tests.py

# Expected output:
# ✅ Dependencies available
# ✅ Scenario 113 validation passed
# ✅ Scenario 217 validation passed
# 🎉 Quick test completed successfully!
```
