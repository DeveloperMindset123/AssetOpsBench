#!/usr/bin/env python3
"""
Quick local test runner for AssetOpsBench scenario validation.

This script is designed for quick local testing without Docker.
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for running tests."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src"
    
    # Add src to Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Change to project root directory
    os.chdir(project_root)
    
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path includes: {src_path}")

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        from assetopsbench.core.validator import validate_scenario
        from assetopsbench.core.scenarios import Scenario
        print("✅ Dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Try: pip install -r benchmark/basic_requirements.txt")
        return False

def run_quick_test():
    """Run a quick test to verify everything works."""
    print("\n🧪 Running Quick Test...")
    
    try:
        from assetopsbench.core.validator import validate_scenario
        from assetopsbench.core.scenarios import Scenario
        
        # Test scenario 113
        scenario_113 = {
            "id": "113",
            "type": "FMSR",
            "text": "If Evaporator Water side fouling occurs for Chiller 6, which sensor is most relevant for monitoring this specific failure?",
            "deterministic": False
        }
        
        errors = validate_scenario(scenario_113)
        if len(errors) == 0:
            print("✅ Scenario 113 validation passed")
        else:
            print(f"❌ Scenario 113 validation failed: {errors}")
            return False
        
        # Test scenario 217
        scenario_217 = {
            "id": "217",
            "type": "TSFM",
            "text": "Forecast 'Chiller 9 Condenser Water Flow' using data in 'chiller9_annotated_small_test.csv'. Use parameter 'Timestamp' as a timestamp.",
            "category": "Inference Query"
        }
        
        errors = validate_scenario(scenario_217)
        if len(errors) == 0:
            print("✅ Scenario 217 validation passed")
        else:
            print(f"❌ Scenario 217 validation failed: {errors}")
            return False
        
        print("🎉 Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"💥 Quick test failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 AssetOpsBench Local Test Runner")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run quick test
    if run_quick_test():
        print("\n📋 Next steps:")
        print("  1. Run full tests: python tests/run_all_tests.py")
        print("  2. Run with Docker: docker-compose -f tests/docker-compose.test.yml up")
        print("  3. Run specific tests: python -m unittest tests.test_scenario_validation -v")
        sys.exit(0)
    else:
        print("\n🔧 Troubleshooting:")
        print("  1. Check that you're in the AssetOpsBench root directory")
        print("  2. Ensure src/ directory contains the validation code")
        print("  3. Install dependencies: pip install -r benchmark/basic_requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
