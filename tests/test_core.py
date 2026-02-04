"""
Tests for LLM Validator core functionality.
"""

import pytest
from llm_validator import LLMValidator, Assertion, AssertionType


class TestMaxLengthAssertion:
    """Tests for MAX_LENGTH assertion."""
    
    def test_under_limit(self):
        validator = LLMValidator()
        assertion = Assertion.max_length("max_tokens", max_tokens=100)
        result = validator.validate("prompt", "short output", [assertion])
        
        assert result.passed == True
        assert result.score == 100.0
        assert "max_tokens" not in result.failed_assertions
    
    def test_over_limit(self):
        validator = LLMValidator()
        assertion = Assertion.max_length("max_tokens", max_tokens=5)
        result = validator.validate("prompt", "this is a much longer output that exceeds the token limit", [assertion])
        
        assert result.passed == False
        assert result.score < 70.0  # Below threshold
        assert "max_tokens" in result.failed_assertions


class TestContainsTextAssertion:
    """Tests for CONTAINS_TEXT assertion."""
    
    def test_contains_text(self):
        validator = LLMValidator()
        assertion = Assertion.contains_text("has_step", text="step", count=2)
        result = validator.validate("prompt", "Here is step one and step two of the plan", [assertion])
        
        assert result.passed == True
        assert "has_step" not in result.failed_assertions
    
    def test_missing_text(self):
        validator = LLMValidator()
        assertion = Assertion.contains_text("has_plan", text="plan", count=1)
        result = validator.validate("prompt", "This output has no specific plan", [assertion])
        
        assert result.passed == True  # Contains "plan"
        assert "has_plan" not in result.failed_assertions


class TestNoPatternAssertion:
    """Tests for NO_PATTERN assertion."""
    
    def test_no_prohibited_pattern(self):
        validator = LLMValidator()
        assertion = Assertion.no_pattern("no_secrets", pattern=r"api_key|password|secret")
        result = validator.validate("prompt", "Here is a normal response without secrets", [assertion])
        
        assert result.passed == True
        assert "no_secrets" not in result.failed_assertions
    
    def test_finds_prohibited_pattern(self):
        validator = LLMValidator()
        assertion = Assertion.no_pattern("no_secrets", pattern=r"api_key|password")
        result = validator.validate("prompt", "The API key is sk-12345 and password is hidden", [assertion])
        
        assert result.passed == False
        assert "no_secrets" in result.failed_assertions


class TestRegexMatchAssertion:
    """Tests for REGEX_MATCH assertion."""
    
    def test_matches_regex(self):
        validator = LLMValidator()
        assertion = Assertion.regex_match("numbered_list", pattern=r"^\d+\.")
        result = validator.validate("prompt", "1. First item\n2. Second item", [assertion])
        
        assert result.passed == True
        assert "numbered_list" not in result.failed_assertions
    
    def test_no_regex_match(self):
        validator = LLMValidator()
        assertion = Assertion.regex_match("numbered_list", pattern=r"^\d+\.")
        result = validator.validate("prompt", "Just a regular sentence", [assertion])
        
        assert result.passed == False
        assert "numbered_list" in result.failed_assertions


class TestValidationResult:
    """Tests for ValidationResult."""
    
    def test_to_dict(self):
        result = LLMValidator().validate(
            "prompt",
            "output",
            [Assertion.max_length("test", max_tokens=100)]
        )
        
        data = result.to_dict()
        assert "prompt" in data
        assert "output" in data
        assert "score" in data
        assert "passed" in data
    
    def test_threshold(self):
        validator = LLMValidator()
        
        # High score
        high_result = validator.validate("p", "short", [Assertion.max_length("t", max_tokens=100)])
        assert high_result.passed == True
        
        # Low score  
        low_result = validator.validate("p", "x" * 10000, [Assertion.max_length("t", max_tokens=5)])
        assert low_result.passed == False


class TestWeighting:
    """Tests for assertion weighting."""
    
    def test_weighted_scoring(self):
        validator = LLMValidator()
        
        assertions = [
            Assertion.max_length("passing", max_tokens=100, weight=0.5),
            Assertion.no_pattern("failing", pattern="error", weight=0.5)
        ]
        
        result = validator.validate("prompt", "This has error in it", assertions)
        
        # One passes (0.5 * 1.0 = 0.5), one fails (0.5 * 0 = 0)
        # Score = (0.5 / 1.0) * 100 = 50.0
        assert result.score == 50.0
        assert result.passed == False  # Below 70 threshold


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
