#!/usr/bin/env python3
"""
LintAI GitHub Action Entry Point

This script runs LintAI validation on LLM outputs and reports results
back to GitHub Actions.
"""

import json
import os
import sys
from pathlib import Path

# Add the local lintai module to the path
sys.path.insert(0, str(Path(__file__).parent))

from llm_validator.core import LLMValidator, Assertion, AssertionType, ValidationResult


def load_assertions_from_config(config_path: str) -> list:
    """
    Load assertions from a JSON configuration file.
    
    Args:
        config_path: Path to the JSON config file
        
    Returns:
        List of Assertion objects
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    assertions = []
    for ac in config.get('assertions', []):
        assertion = Assertion(
            name=ac['name'],
            type=ac['type'],
            params=ac.get('params', {}),
            weight=ac.get('weight', 1.0),
            enabled=ac.get('enabled', True)
        )
        assertions.append(assertion)
    
    return assertions


def format_assertion_results(results: list) -> str:
    """Format assertion results as a JSON string for GitHub output."""
    return json.dumps(results)


def main():
    """
    Main entry point for the GitHub Action.
    """
    # Get inputs from environment variables
    prompt = os.environ.get('INPUT_PROMPT', '')
    output = os.environ.get('INPUT_OUTPUT', '')
    assertions_config = os.environ.get('INPUT_ASSERTIONS-CONFIG', '')
    pass_threshold = float(os.environ.get('INPUT_PASS-THRESHOLD', '70'))
    fail_on_warning = os.environ.get('INPUT_FAIL-ON-WARNING', 'false').lower() == 'true'
    
    # Validate required inputs
    if not prompt:
        print("::error::Input 'prompt' is required")
        sys.exit(1)
    
    if not output:
        print("::error::Input 'output' is required")
        sys.exit(1)
    
    if not assertions_config:
        print("::error::Input 'assertions-config' is required")
        sys.exit(1)
    
    if not os.path.exists(assertions_config):
        print(f"::error::Assertions config file not found: {assertions_config}")
        sys.exit(1)
    
    try:
        # Load assertions from config
        assertions = load_assertions_from_config(assertions_config)
        
        if not assertions:
            print("::warning::No assertions found in config file")
        
        # Run validation
        validator = LLMValidator()
        result = validator.validate(
            prompt=prompt,
            output=output,
            assertions=assertions,
            metadata={'source': 'github-action'}
        )
        
        # Format assertion results for output
        assertion_results_json = format_assertion_results(result.assertion_results)
        failed_assertions_json = json.dumps(result.failed_assertions)
        
        # Set output variables using GITHUB_OUTPUT
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write(f"passed={str(result.passed).lower()}\n")
                f.write(f"score={result.score}\n")
                f.write(f"failed-assertions={failed_assertions_json}\n")
                f.write(f"assertion-results={assertion_results_json}\n")
        else:
            # Fallback for local testing
            print(f"::set-output name=passed::{str(result.passed).lower()}")
            print(f"::set-output name=score::{result.score}")
            print(f"::set-output name=failed-assertions::{failed_assertions_json}")
            print(f"::set-output name=assertion-results::{assertion_results_json}")
        
        # Print summary
        print("\n" + "="*60)
        print("LintAI Validation Results")
        print("="*60)
        print(f"Passed: {'✓' if result.passed else '✗'}")
        print(f"Score: {result.score:.1f}%")
        print(f"Threshold: {pass_threshold}%")
        print(f"Assertions Checked: {len(result.assertion_results)}")
        print(f"Failed: {len(result.failed_assertions)}")
        
        if result.warnings:
            print(f"Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("\nAssertion Details:")
        for ar in result.assertion_results:
            status = "✓" if ar['passed'] else "✗"
            print(f"  [{status}] {ar['name']}: {ar['message']}")
        
        print("="*60 + "\n")
        
        # Check if validation passed
        validation_passed = result.score >= pass_threshold
        
        # Fail if below threshold
        if not validation_passed:
            print(f"::error::Validation failed! Score ({result.score:.1f}%) below threshold ({pass_threshold}%)")
            sys.exit(1)
        
        # Fail if there are failed assertions and fail_on_warning is true
        if fail_on_warning and result.failed_assertions:
            print(f"::error::Validation failed due to failed assertions with fail-on-warning enabled")
            sys.exit(1)
        
        # Exit with success
        print(f"✓ Validation passed with score {result.score:.1f}%")
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON in assertions config: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"::error::Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
