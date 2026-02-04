"""
Core validation logic for LLM Validator.
"""

import re
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
from abc import ABC, abstractmethod


class AssertionType(Enum):
    """Types of assertions available for validation."""
    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"
    CONTAINS_TEXT = "contains_text"
    NO_PATTERN = "no_pattern"
    REGEX_MATCH = "regex_match"
    SENTIMENT = "sentiment"
    JSON_VALID = "json_valid"
    KEYWORD_COUNT = "keyword_count"
    CUSTOM = "custom"


@dataclass
class Assertion:
    """A single validation assertion."""
    name: str
    type: AssertionType
    params: Dict[str, Any]
    weight: float = 1.0
    enabled: bool = True
    message: str = ""
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = AssertionType(self.type)


@dataclass
class ValidationResult:
    """Result of running validation on an LLM output."""
    prompt: str
    output: str
    score: float
    passed: bool
    assertion_results: List[Dict[str, Any]]
    failed_assertions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "output": self.output,
            "score": self.score,
            "passed": self.passed,
            "assertion_results": self.assertion_results,
            "failed_assertions": self.failed_assertions,
            "warnings": self.warnings,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class BaseAssertionHandler(ABC):
    """Base class for assertion handlers."""
    
    @abstractmethod
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if assertion passes. Returns dict with passed, message, score."""
        pass


class MaxLengthHandler(BaseAssertionHandler):
    """Handler for MAX_LENGTH assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        max_tokens = params.get("max_tokens", 1000)
        max_chars = params.get("max_chars", 10000)
        
        # Estimate tokens (rough approximation)
        token_count = len(output.split()) * 1.33  # ~1.33 tokens per word
        
        if token_count <= max_tokens and len(output) <= max_chars:
            return {
                "passed": True,
                "message": f"Output within limits ({int(token_count)} tokens)",
                "score": 1.0
            }
        else:
            return {
                "passed": False,
                "message": f"Output exceeds limits ({int(token_count)} tokens, {len(output)} chars)",
                "score": 0.0
            }


class MinLengthHandler(BaseAssertionHandler):
    """Handler for MIN_LENGTH assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        min_tokens = params.get("min_tokens", 10)
        min_words = params.get("min_words", 10)
        
        word_count = len(output.split())
        
        if word_count >= min_words and (word_count * 1.33) >= min_tokens:
            return {
                "passed": True,
                "message": f"Output meets minimum length ({word_count} words)",
                "score": 1.0
            }
        else:
            return {
                "passed": False,
                "message": f"Output below minimum ({word_count} words)",
                "score": 0.0
            }


class ContainsTextHandler(BaseAssertionHandler):
    """Handler for CONTAINS_TEXT assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        required_text = params.get("text", "")
        count = params.get("count", 1)
        case_sensitive = params.get("case_sensitive", False)
        
        if case_sensitive:
            occurrences = output.count(required_text)
        else:
            occurrences = output.lower().count(required_text.lower())
        
        if occurrences >= count:
            return {
                "passed": True,
                "message": f"Contains '{required_text}' ({occurrences} times)",
                "score": min(1.0, occurrences / count)
            }
        else:
            return {
                "passed": False,
                "message": f"Missing '{required_text}' (found {occurrences}, need {count})",
                "score": 0.0
            }


class NoPatternHandler(BaseAssertionHandler):
    """Handler for NO_PATTERN assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pattern = params.get("pattern", "")
        
        try:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                return {
                    "passed": False,
                    "message": f"Found prohibited pattern: {matches[0]}",
                    "score": 0.0
                }
            else:
                return {
                    "passed": True,
                    "message": "No prohibited patterns found",
                    "score": 1.0
                }
        except re.error as e:
            return {
                "passed": False,
                "message": f"Invalid regex pattern: {e}",
                "score": 0.0
            }


class RegexMatchHandler(BaseAssertionHandler):
    """Handler for REGEX_MATCH assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pattern = params.get("pattern", "")
        
        try:
            if re.search(pattern, output):
                return {
                    "passed": True,
                    "message": f"Pattern '{pattern}' matched",
                    "score": 1.0
                }
            else:
                return {
                    "passed": False,
                    "message": f"Pattern '{pattern}' not found",
                    "score": 0.0
                }
        except re.error as e:
            return {
                "passed": False,
                "message": f"Invalid regex pattern: {e}",
                "score": 0.0
            }


class JSONValidHandler(BaseAssertionHandler):
    """Handler for JSON_VALID assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data = json.loads(output)
            
            # Validate against schema if provided
            schema_path = params.get("schema")
            if schema_path:
                with open(schema_path) as f:
                    schema = json.load(f)
                # Basic schema validation (simplified)
                # In production, use jsonschema library
            
            return {
                "passed": True,
                "message": "Valid JSON",
                "score": 1.0
            }
        except json.JSONDecodeError as e:
            return {
                "passed": False,
                "message": f"Invalid JSON: {e}",
                "score": 0.0
            }
        except FileNotFoundError:
            return {
                "passed": False,
                "message": f"Schema file not found: {schema_path}",
                "score": 0.0
            }


class KeywordCountHandler(BaseAssertionHandler):
    """Handler for KEYWORD_COUNT assertion."""
    
    def check(self, output: str, params: Dict[str, Any]) -> Dict[str, Any]:
        keywords = params.get("keywords", [])
        min_count = params.get("min_count", 1)
        all_required = params.get("all_required", False)
        
        output_lower = output.lower()
        found_keywords = []
        
        for kw in keywords:
            if kw.lower() in output_lower:
                found_keywords.append(kw)
        
        if all_required:
            passed = len(found_keywords) == len(keywords)
            score = len(found_keywords) / len(keywords) if keywords else 1.0
        else:
            passed = len(found_keywords) >= min_count
            score = min(1.0, len(found_keywords) / max(min_count, len(keywords)))
        
        return {
            "passed": passed,
            "message": f"Found {len(found_keywords)}/{len(keywords)} keywords: {found_keywords}",
            "score": score
        }


# Handler registry
ASSERTION_HANDLERS = {
    AssertionType.MAX_LENGTH: MaxLengthHandler(),
    AssertionType.MIN_LENGTH: MinLengthHandler(),
    AssertionType.CONTAINS_TEXT: ContainsTextHandler(),
    AssertionType.NO_PATTERN: NoPatternHandler(),
    AssertionType.REGEX_MATCH: RegexMatchHandler(),
    AssertionType.JSON_VALID: JSONValidHandler(),
    AssertionType.KEYWORD_COUNT: KeywordCountHandler(),
}


class LLMValidator:
    """
    Main validator class for testing LLM outputs.
    """
    
    def __init__(self, model: str = "gpt-4", provider: str = "openai"):
        """
        Initialize the validator.
        
        Args:
            model: LLM model to use (for reference)
            provider: LLM provider (openai, anthropic, etc.)
        """
        self.model = model
        self.provider = provider
        self.assertion_handlers = ASSERTION_HANDLERS.copy()
        
    def add_assertion_handler(self, assertion_type: AssertionType, handler: BaseAssertionHandler):
        """Add a custom assertion handler."""
        self.assertion_handlers[assertion_type] = handler
    
    def validate(
        self,
        prompt: str,
        output: str,
        assertions: List[Assertion],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate an LLM output against assertions.
        
        Args:
            prompt: The original prompt sent to the LLM
            output: The LLM's output to validate
            assertions: List of assertions to check
            metadata: Optional metadata to include in results
            
        Returns:
            ValidationResult with score and details
        """
        assertion_results = []
        total_weight = 0.0
        passed_weight = 0.0
        failed_assertions = []
        warnings = []
        
        for assertion in assertions:
            if not assertion.enabled:
                continue
                
            total_weight += assertion.weight
            
            handler = self.assertion_handlers.get(assertion.type)
            
            if handler is None:
                warnings.append(f"No handler for assertion type: {assertion.type}")
                continue
            
            result = handler.check(output, assertion.params)
            
            assertion_result = {
                "name": assertion.name,
                "type": assertion.type.value,
                "passed": result["passed"],
                "message": result["message"],
                "score": result["score"],
                "weight": assertion.weight
            }
            assertion_results.append(assertion_result)
            
            if result["passed"]:
                passed_weight += assertion.weight * result["score"]
            else:
                failed_assertions.append(assertion.name)
        
        # Calculate overall score
        score = (passed_weight / total_weight * 100) if total_weight > 0 else 100.0
        
        return ValidationResult(
            prompt=prompt,
            output=output,
            score=score,
            passed=score >= 70.0,  # 70% threshold for passing
            assertion_results=assertion_results,
            failed_assertions=failed_assertions,
            warnings=warnings,
            metadata=metadata or {}
        )
    
    def validate_from_config(
        self,
        prompt: str,
        output: str,
        config_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate using a YAML/JSON config file.
        
        Args:
            prompt: The original prompt
            output: The LLM's output
            config_path: Path to validation config file
            metadata: Optional metadata
            
        Returns:
            ValidationResult
        """
        with open(config_path) as f:
            config = json.load(f) if config_path.endswith(".json") else json.load(f)
        
        assertions = []
        for ac in config.get("assertions", []):
            assertions.append(Assertion(
                name=ac["name"],
                type=ac["type"],
                params=ac.get("params", {}),
                weight=ac.get("weight", 1.0)
            ))
        
        return self.validate(prompt, output, assertions, metadata)
