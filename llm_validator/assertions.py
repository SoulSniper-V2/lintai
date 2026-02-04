"""
Assertion types and configurations for LLM Validator.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


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
    
    @classmethod
    def max_length(cls, name: str, max_tokens: int = 1000, max_chars: int = 10000, weight: float = 1.0) -> "Assertion":
        """Create a MAX_LENGTH assertion."""
        return cls(
            name=name,
            type=AssertionType.MAX_LENGTH,
            params={"max_tokens": max_tokens, "max_chars": max_chars},
            weight=weight
        )
    
    @classmethod
    def min_length(cls, name: str, min_tokens: int = 10, min_words: int = 10, weight: float = 1.0) -> "Assertion":
        """Create a MIN_LENGTH assertion."""
        return cls(
            name=name,
            type=AssertionType.MIN_LENGTH,
            params={"min_tokens": min_tokens, "min_words": min_words},
            weight=weight
        )
    
    @classmethod
    def contains_text(cls, name: str, text: str, count: int = 1, case_sensitive: bool = False, weight: float = 1.0) -> "Assertion":
        """Create a CONTAINS_TEXT assertion."""
        return cls(
            name=name,
            type=AssertionType.CONTAINS_TEXT,
            params={"text": text, "count": count, "case_sensitive": case_sensitive},
            weight=weight
        )
    
    @classmethod
    def no_pattern(cls, name: str, pattern: str, weight: float = 1.0) -> "Assertion":
        """Create a NO_PATTERN assertion."""
        return cls(
            name=name,
            type=AssertionType.NO_PATTERN,
            params={"pattern": pattern},
            weight=weight
        )
    
    @classmethod
    def regex_match(cls, name: str, pattern: str, weight: float = 1.0) -> "Assertion":
        """Create a REGEX_MATCH assertion."""
        return cls(
            name=name,
            type=AssertionType.REGEX_MATCH,
            params={"pattern": pattern},
            weight=weight
        )
    
    @classmethod
    def keyword_count(cls, name: str, keywords: List[str], min_count: int = 1, all_required: bool = False, weight: float = 1.0) -> "Assertion":
        """Create a KEYWORD_COUNT assertion."""
        return cls(
            name=name,
            type=AssertionType.KEYWORD_COUNT,
            params={"keywords": keywords, "min_count": min_count, "all_required": all_required},
            weight=weight
        )
    
    @classmethod
    def json_valid(cls, name: str, schema: str = None, weight: float = 1.0) -> "Assertion":
        """Create a JSON_VALID assertion."""
        params = {}
        if schema:
            params["schema"] = schema
        return cls(
            name=name,
            type=AssertionType.JSON_VALID,
            params=params,
            weight=weight
        )


@dataclass
class ValidationConfig:
    """Configuration for a validation run."""
    name: str
    model: str
    assertions: List[Assertion]
    threshold: float = 70.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "threshold": self.threshold,
            "assertions": [
                {
                    "name": a.name,
                    "type": a.type.value,
                    "params": a.params,
                    "weight": a.weight,
                    "enabled": a.enabled
                }
                for a in self.assertions
            ]
        }
    
    def save(self, path: str):
        """Save config to JSON file."""
        import json
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "ValidationConfig":
        """Load config from JSON file."""
        import json
        with open(path) as f:
            data = json.load(f)
        
        assertions = []
        for ac in data.get("assertions", []):
            assertions.append(Assertion(
                name=ac["name"],
                type=ac["type"],
                params=ac.get("params", {}),
                weight=ac.get("weight", 1.0),
                enabled=ac.get("enabled", True)
            ))
        
        return cls(
            name=data["name"],
            model=data["model"],
            assertions=assertions,
            threshold=data.get("threshold", 70.0)
        )
