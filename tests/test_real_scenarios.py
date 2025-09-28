#!/usr/bin/env python3
"""
Unit tests for real scenario files in AssetOpsBench.

This module tests the actual scenario files from the scenarios/ directory
using the scenario validation code.
"""

import unittest
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from assetopsbench.core.validator import validate_file, validate_scenario
from assetopsbench.core.scenarios import Scenario


class TestRealScenarioFiles(unittest.TestCase):
    """Test cases for real scenario files in the repository."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scenarios_dir = Path(__file__).parent.parent / "scenarios"
        self.single_agent_dir = self.scenarios_dir / "single_agent"
        self.multi_agent_dir = self.scenarios_dir / "multi_agent"
        
        # Expected scenario files
        self.expected_files = [
            "iot_utterance_meta.json",
            "fmsr_utterance.json", 
            "tsfm_utterance.json",
            "wo_utterance.json",
            "end2end_utterance.json"
        ]

    def test_scenario_files_exist(self):
        """Test that expected scenario files exist."""
        for filename in self.expected_files:
            if filename == "end2end_utterance.json":
                file_path = self.multi_agent_dir / filename
            else:
                file_path = self.single_agent_dir / filename
            
            self.assertTrue(file_path.exists(), f"Scenario file {filename} should exist")

    def test_iot_scenarios_validation(self):
        """Test validation of IoT scenarios."""
        iot_file = self.single_agent_dir / "iot_utterance_meta.json"
        if iot_file.exists():
            errors = validate_file(iot_file)
            self.assertEqual(len(errors), 0, f"IoT scenarios should be valid: {errors}")
            
            # Load and test a few scenarios
            with open(iot_file, 'r') as f:
                scenarios = json.load(f)
            
            # Test first scenario
            if scenarios:
                errors = validate_scenario(scenarios[0])
                self.assertEqual(len(errors), 0, f"First IoT scenario should be valid: {errors}")
                
                scenario = Scenario(**scenarios[0])
                self.assertEqual(scenario.type, "IoT")

    def test_fmsr_scenarios_validation(self):
        """Test validation of FMSR scenarios."""
        fmsr_file = self.single_agent_dir / "fmsr_utterance.json"
        if fmsr_file.exists():
            errors = validate_file(fmsr_file)
            self.assertEqual(len(errors), 0, f"FMSR scenarios should be valid: {errors}")
            
            # Load and test scenario 113 specifically
            with open(fmsr_file, 'r') as f:
                scenarios = json.load(f)
            
        # Find scenario 113
        scenario_113 = next((s for s in scenarios if s.get('id') == 113), None)
        if scenario_113:
            errors = validate_scenario(scenario_113)
            self.assertEqual(len(errors), 0, f"FMSR scenario 113 should be valid: {errors}")
            
            scenario = Scenario(**scenario_113)
            self.assertEqual(scenario.id, "113")
            # Note: scenario_113 might not have a 'type' field, so we check if it exists
            if 'type' in scenario_113:
                self.assertEqual(scenario.type, "FMSR")
            self.assertIn("Evaporator Water side fouling", scenario.text)

    def test_tsfm_scenarios_validation(self):
        """Test validation of TSFM scenarios."""
        tsfm_file = self.single_agent_dir / "tsfm_utterance.json"
        if tsfm_file.exists():
            errors = validate_file(tsfm_file)
            self.assertEqual(len(errors), 0, f"TSFM scenarios should be valid: {errors}")
            
            # Load and test scenario 217 specifically
            with open(tsfm_file, 'r') as f:
                scenarios = json.load(f)
            
            # Find scenario 217
            scenario_217 = next((s for s in scenarios if s.get('id') == 217), None)
            if scenario_217:
                errors = validate_scenario(scenario_217)
                self.assertEqual(len(errors), 0, f"TSFM scenario 217 should be valid: {errors}")
                
                scenario = Scenario(**scenario_217)
                self.assertEqual(scenario.id, "217")
                self.assertEqual(scenario.type, "TSFM")
                self.assertIn("Forecast", scenario.text)
                self.assertIn("chiller9_annotated_small_test.csv", scenario.text)

    def test_workorder_scenarios_validation(self):
        """Test validation of WorkOrder scenarios."""
        wo_file = self.single_agent_dir / "wo_utterance.json"
        if wo_file.exists():
            errors = validate_file(wo_file)
            self.assertEqual(len(errors), 0, f"WorkOrder scenarios should be valid: {errors}")
            
            # Load and test a few scenarios
            with open(wo_file, 'r') as f:
                scenarios = json.load(f)
            
            # Test first scenario
            if scenarios:
                errors = validate_scenario(scenarios[0])
                self.assertEqual(len(errors), 0, f"First WorkOrder scenario should be valid: {errors}")
                
                scenario = Scenario(**scenarios[0])
                self.assertIn(scenario.type, ["WorkOrder", "Workorder"])  # Accept both variants

    def test_end2end_scenarios_validation(self):
        """Test validation of end-to-end scenarios."""
        end2end_file = self.multi_agent_dir / "end2end_utterance.json"
        if end2end_file.exists():
            errors = validate_file(end2end_file)
            self.assertEqual(len(errors), 0, f"End-to-end scenarios should be valid: {errors}")
            
            # Load and test a few scenarios
            with open(end2end_file, 'r') as f:
                scenarios = json.load(f)
            
            # Test first scenario
            if scenarios:
                errors = validate_scenario(scenarios[0])
                self.assertEqual(len(errors), 0, f"First end-to-end scenario should be valid: {errors}")

    def test_all_utterances_jsonl_validation(self):
        """Test validation of all_utterance.jsonl file."""
        all_utterances_file = self.scenarios_dir / "all_utterance.jsonl"
        if all_utterances_file.exists():
            errors = validate_file(all_utterances_file)
            self.assertEqual(len(errors), 0, f"All utterances JSONL should be valid: {errors}")
            
            # Test a few scenarios from the file
            with open(all_utterances_file, 'r') as f:
                lines = f.readlines()
            
            # Test first few scenarios
            for i, line in enumerate(lines[:5]):  # Test first 5 scenarios
                if line.strip():
                    scenario_data = json.loads(line)
                    errors = validate_scenario(scenario_data)
                    self.assertEqual(len(errors), 0, f"Scenario {i+1} in all_utterance.jsonl should be valid: {errors}")

    def test_scenario_types_and_categories(self):
        """Test that scenarios have valid types and categories."""
        scenario_files = [
            self.single_agent_dir / "iot_utterance_meta.json",
            self.single_agent_dir / "fmsr_utterance.json",
            self.single_agent_dir / "tsfm_utterance.json",
            self.single_agent_dir / "wo_utterance.json",
            self.multi_agent_dir / "end2end_utterance.json"
        ]
        
        expected_types = {"IoT", "FMSR", "TSFM", "WorkOrder", "Workorder", ""}  # Include empty string
        
        for file_path in scenario_files:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    scenarios = json.load(f)
                
                for scenario_data in scenarios:
                    if 'type' in scenario_data:
                        self.assertIn(scenario_data['type'], expected_types, 
                                    f"Unknown scenario type: '{scenario_data['type']}'")
                    
                    # Test scenario creation
                    errors = validate_scenario(scenario_data)
                    self.assertEqual(len(errors), 0, 
                                   f"Scenario {scenario_data.get('id', 'unknown')} should be valid: {errors}")

    def test_scenario_characteristic_forms(self):
        """Test that scenarios have meaningful characteristic_forms."""
        scenario_files = [
            self.single_agent_dir / "iot_utterance_meta.json",
            self.single_agent_dir / "fmsr_utterance.json",
            self.single_agent_dir / "tsfm_utterance.json"
        ]
        
        for file_path in scenario_files:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    scenarios = json.load(f)
                
                for scenario_data in scenarios:
                    if 'characteristic_form' in scenario_data:
                        char_form = scenario_data['characteristic_form']
                        self.assertIsInstance(char_form, str, "characteristic_form should be a string")
                        self.assertGreater(len(char_form), 10, "characteristic_form should be meaningful")


if __name__ == '__main__':
    unittest.main(verbosity=2)
