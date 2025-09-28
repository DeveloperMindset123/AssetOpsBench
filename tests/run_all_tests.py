#!/usr/bin/env python3
"""
Comprehensive test runner for all AssetOpsBench tests.

This script runs all unittest tests including scenario validation tests
as requested in GitHub issue #30:
https://github.com/IBM/AssetOpsBench/issues/30
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_all_tests():
    """Run all available tests."""
    print("🧪 Running All AssetOpsBench Tests...")
    print("=" * 60)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"  {i}. {test}")
            print(f"     {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"  {i}. {test}")
            print(f"     {traceback.split('Error:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Scenario validation is working correctly.")
        print("\n📋 Test Coverage:")
        print("  ✅ Scenario validation functionality")
        print("  ✅ FMSR scenario 113 (Evaporator Water side fouling)")
        print("  ✅ TSFM scenario 217 (Chiller 9 forecasting)")
        print("  ✅ Real scenario files validation")
        print("  ✅ Edge cases and error handling")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test(s) failed")
        print("\n🔧 Next Steps:")
        print("  1. Review the failed tests above")
        print("  2. Check the scenario validation code")
        print("  3. Ensure all scenario files are properly formatted")
        return False


def run_specific_test_suite(test_name):
    """Run a specific test suite."""
    print(f"🧪 Running {test_name} Tests...")
    print("=" * 60)
    
    # Import and run specific test
    if test_name == "scenario_validation":
        from test_scenario_validation import TestScenarioValidation, TestScenarioExamples
        suite = unittest.TestLoader().loadTestsFromTestCase(TestScenarioValidation)
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestScenarioExamples))
    elif test_name == "real_scenarios":
        from test_real_scenarios import TestRealScenarioFiles
        suite = unittest.TestLoader().loadTestsFromTestCase(TestRealScenarioFiles)
    else:
        print(f"Unknown test suite: {test_name}")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{'✅' if result.wasSuccessful() else '❌'} {test_name} tests completed")
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test suite
        test_suite = sys.argv[1]
        success = run_specific_test_suite(test_suite)
    else:
        # Run all tests
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
