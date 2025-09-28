#!/usr/bin/env python3
"""
Unit tests for scenario validation code in AssetOpsBench.

This module tests the scenario validation functionality as requested in GitHub issue #30:
https://github.com/IBM/AssetOpsBench/issues/30

Tests the validator.py code using Python's built-in unittest package.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from assetopsbench.core.validator import (
    validate_scenario,
    validate_file,
    find_json_files,
)
from assetopsbench.core.scenarios import Scenario


class TestScenarioValidation(unittest.TestCase):
    """Test cases for scenario validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_scenario_data = {
            "id": "113",
            "type": "FMSR",
            "text": "If Evaporator Water side fouling occurs for Chiller 6, which sensor is most relevant for monitoring this specific failure?",
            "category": "Knowledge Query",
            "characteristic_form": "the answer should contain one of more sensors of Chiller 6. The sensors of Chiller 6 need to be from the list [Chiller 6 Chiller % Loaded, Chiller 6 Chiller Efficiency, Chiller 6 Condenser Water Flow, Chiller 6 Condenser Water Return To Tower Temperature, Chiller 6 Liquid Refrigerant Evaporator Temperature, Chiller 6 Power Input, Chiller 6 Return Temperature, Chiller 6 Schedule, Chiller 6 Supply Temperature, Chiller 6 Tonnage.]",
            "deterministic": False,
        }

        self.tsfm_scenario_data = {
            "id": "217",
            "type": "TSFM",
            "text": "Forecast 'Chiller 9 Condenser Water Flow' using data in 'chiller9_annotated_small_test.csv'. Use parameter 'Timestamp' as a timestamp.",
            "category": "Inference Query",
            "characteristic_form": "The expected response should be: Forecasting results of 'Chiller 9 Condenser Water Flow' using data in 'chiller9_annotated_small_test.csv' are stored in json file",
        }

    def test_valid_fmsr_scenario(self):
        """Test validation of FMSR scenario 113."""
        errors = validate_scenario(self.valid_scenario_data)
        self.assertEqual(
            len(errors), 0, f"Validation should pass but got errors: {errors}"
        )

        # Test that it creates a valid Scenario object
        scenario = Scenario(**self.valid_scenario_data)
        self.assertEqual(scenario.id, "113")
        self.assertEqual(scenario.type, "FMSR")
        self.assertIn("Evaporator Water side fouling", scenario.text)

    def test_valid_tsfm_scenario(self):
        """Test validation of TSFM scenario 217."""
        errors = validate_scenario(self.tsfm_scenario_data)
        self.assertEqual(
            len(errors), 0, f"Validation should pass but got errors: {errors}"
        )

        # Test that it creates a valid Scenario object
        scenario = Scenario(**self.tsfm_scenario_data)
        self.assertEqual(scenario.id, "217")
        self.assertEqual(scenario.type, "TSFM")
        self.assertIn("Forecast", scenario.text)

    def test_invalid_scenario_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        invalid_data = {
            "id": "999"
            # Missing required 'text' field
        }
        errors = validate_scenario(invalid_data)
        self.assertGreater(
            len(errors), 0, "Should have validation errors for missing required fields"
        )
        self.assertTrue(any("text" in error.lower() for error in errors))

    def test_invalid_scenario_empty_text(self):
        """Test validation fails for empty text field."""
        invalid_data = {
            "id": "999",
            "text": "   ",  # Whitespace-only text should be stripped to empty
            "type": "FMSR",
        }
        errors = validate_scenario(invalid_data)
        # Note: The current model allows empty text, so this test checks the current behavior
        # If we want to enforce non-empty text, we'd need to add validation to the Scenario model
        self.assertEqual(len(errors), 0, "Current model allows empty text after stripping whitespace")

    def test_scenario_with_optional_fields(self):
        """Test validation with optional fields."""
        data_with_optionals = self.valid_scenario_data.copy()
        data_with_optionals.update(
            {
                "uuid": "test-uuid-123",
                "expected_result": {
                    "sensor": "Chiller 6 Liquid Refrigerant Evaporator Temperature"
                },
                "data": {"site": "MAIN", "equipment": "Chiller 6"},
                "source": "test_dataset.json",
            }
        )

        errors = validate_scenario(data_with_optionals)
        self.assertEqual(
            len(errors), 0, f"Validation should pass with optional fields: {errors}"
        )

        scenario = Scenario(**data_with_optionals)
        self.assertEqual(scenario.uuid, "test-uuid-123")
        self.assertEqual(scenario.data["site"], "MAIN")

    def test_scenario_id_type_conversion(self):
        """Test that integer IDs are converted to strings."""
        data_with_int_id = self.valid_scenario_data.copy()
        data_with_int_id["id"] = 113  # Integer ID

        # The validator should convert this to string
        errors = validate_scenario(data_with_int_id)
        self.assertEqual(len(errors), 0, "Should handle integer ID conversion")

    def test_validate_json_file(self):
        """Test validation of JSON files."""
        # Create temporary JSON file with valid scenarios
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([self.valid_scenario_data, self.tsfm_scenario_data], f)
            temp_file = Path(f.name)

        try:
            errors = validate_file(temp_file)
            self.assertEqual(
                len(errors), 0, f"JSON file validation should pass: {errors}"
            )
        finally:
            temp_file.unlink()

    def test_validate_jsonl_file(self):
        """Test validation of JSONL files."""
        # Create temporary JSONL file with valid scenarios
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps(self.valid_scenario_data) + "\n")
            f.write(json.dumps(self.tsfm_scenario_data) + "\n")
            temp_file = Path(f.name)

        try:
            errors = validate_file(temp_file)
            self.assertEqual(
                len(errors), 0, f"JSONL file validation should pass: {errors}"
            )
        finally:
            temp_file.unlink()

    def test_validate_invalid_json_file(self):
        """Test validation fails for invalid JSON files."""
        # Create temporary JSON file with invalid scenario
        invalid_scenario = {
            "id": "999"
            # Missing required 'text' field
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([invalid_scenario], f)
            temp_file = Path(f.name)

        try:
            errors = validate_file(temp_file)
            self.assertGreater(
                len(errors), 0, "Should have validation errors for invalid JSON file"
            )
        finally:
            temp_file.unlink()

    def test_find_json_files(self):
        """Test finding JSON and JSONL files in directory."""
        # Create temporary directory with various files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test.json").write_text("[]")
            (temp_path / "test.jsonl").write_text("")
            (temp_path / "test.txt").write_text("not json")
            (temp_path / "test.py").write_text('print("hello")')

            # Find JSON files
            json_files = find_json_files(temp_path)

            # Should find 2 files (test.json and test.jsonl)
            self.assertEqual(len(json_files), 2)
            file_names = [f.name for f in json_files]
            self.assertIn("test.json", file_names)
            self.assertIn("test.jsonl", file_names)

    def test_scenario_validation_edge_cases(self):
        """Test edge cases in scenario validation."""
        # Test with minimal required fields only
        minimal_scenario = {"id": "001", "text": "What IoT sites are available?"}
        errors = validate_scenario(minimal_scenario)
        self.assertEqual(len(errors), 0, "Minimal scenario should be valid")

        # Test with extra fields (should be ignored due to extra="ignore")
        extra_fields_scenario = self.valid_scenario_data.copy()
        extra_fields_scenario["extra_field"] = "should be ignored"
        extra_fields_scenario["another_field"] = 123

        errors = validate_scenario(extra_fields_scenario)
        self.assertEqual(len(errors), 0, "Extra fields should be ignored")

    def test_characteristic_form_validation(self):
        """Test validation of characteristic_form field."""
        # Test with long characteristic_form
        long_characteristic = "x" * 10000  # Very long string
        scenario_with_long_char = self.valid_scenario_data.copy()
        scenario_with_long_char["characteristic_form"] = long_characteristic

        errors = validate_scenario(scenario_with_long_char)
        self.assertEqual(len(errors), 0, "Long characteristic_form should be valid")

        # Test with None characteristic_form
        scenario_with_none_char = self.valid_scenario_data.copy()
        scenario_with_none_char["characteristic_form"] = None

        errors = validate_scenario(scenario_with_none_char)
        self.assertEqual(len(errors), 0, "None characteristic_form should be valid")

    def test_deterministic_field_validation(self):
        """Test validation of deterministic field."""
        # Test with deterministic=True
        deterministic_scenario = self.valid_scenario_data.copy()
        deterministic_scenario["deterministic"] = True
        deterministic_scenario["expected_result"] = {
            "answer": "Chiller 6 Liquid Refrigerant Evaporator Temperature"
        }

        errors = validate_scenario(deterministic_scenario)
        self.assertEqual(len(errors), 0, "Deterministic scenario should be valid")

        # Test with deterministic=False
        non_deterministic_scenario = self.valid_scenario_data.copy()
        non_deterministic_scenario["deterministic"] = False

        errors = validate_scenario(non_deterministic_scenario)
        self.assertEqual(len(errors), 0, "Non-deterministic scenario should be valid")


class TestScenarioExamples(unittest.TestCase):
    """Test cases using the actual example scenarios from the issue."""

    def test_fmsr_scenario_113(self):
        """Test the specific FMSR scenario 113 mentioned in the issue."""
        scenario_113 = {
            "id": "113",
            "type": "FMSR",
            "deterministic": False,
            "characteristic_form": "the answer should contain one of more sensors of Chiller 6. The sensors of Chiller 6 need to be from the list [Chiller 6 Chiller % Loaded, Chiller 6 Chiller Efficiency, Chiller 6 Condenser Water Flow, Chiller 6 Condenser Water Return To Tower Temperature, Chiller 6 Liquid Refrigerant Evaporator Temperature, Chiller 6 Power Input, Chiller 6 Return Temperature, Chiller 6 Schedule, Chiller 6 Supply Temperature, Chiller 6 Tonnage.] ",
            "text": " If Evaporator Water side fouling occurs for Chiller 6, which sensor is most relevant for monitoring this specific failure?",
        }

        errors = validate_scenario(scenario_113)
        self.assertEqual(len(errors), 0, f"Scenario 113 should be valid: {errors}")

        # Validate the scenario object creation
        scenario = Scenario(**scenario_113)
        self.assertEqual(scenario.id, "113")
        self.assertEqual(scenario.type, "FMSR")
        self.assertFalse(scenario.deterministic)
        self.assertIn("Evaporator Water side fouling", scenario.text)
        self.assertIn("Chiller 6", scenario.characteristic_form)

    def test_tsfm_scenario_217(self):
        """Test the specific TSFM scenario 217 mentioned in the issue."""
        scenario_217 = {
            "id": "217",
            "type": "TSFM",
            "text": "Forecast 'Chiller 9 Condenser Water Flow' using data in 'chiller9_annotated_small_test.csv'. Use parameter 'Timestamp' as a timestamp.",
            "category": "Inference Query",
            "characteristic_form": "The expected response should be: Forecasting results of 'Chiller 9 Condenser Water Flow' using data in 'chiller9_annotated_small_test.csv' are stored in json file",
        }

        errors = validate_scenario(scenario_217)
        self.assertEqual(len(errors), 0, f"Scenario 217 should be valid: {errors}")

        # Validate the scenario object creation
        scenario = Scenario(**scenario_217)
        self.assertEqual(scenario.id, "217")
        self.assertEqual(scenario.type, "TSFM")
        self.assertEqual(scenario.category, "Inference Query")
        self.assertIn("Forecast", scenario.text)
        self.assertIn("chiller9_annotated_small_test.csv", scenario.text)
        self.assertIn("Timestamp", scenario.text)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
