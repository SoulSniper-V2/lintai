"""
Data models for LLM Validator.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json


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
class AssertionConfig:
    """Configuration for a single assertion."""
    name: str
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    enabled: bool = True
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "params": self.params,
            "weight": self.weight,
            "enabled": self.enabled,
            "message": self.message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssertionConfig":
        return cls(
            name=data["name"],
            type=data["type"],
            params=data.get("params", {}),
            weight=data.get("weight", 1.0),
            enabled=data.get("enabled", True),
            message=data.get("message", "")
        )


@dataclass
class ValidationConfig:
    """Configuration for a validation run."""
    name: str
    model: str
    assertions: List[AssertionConfig]
    threshold: float = 70.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "threshold": self.threshold,
            "metadata": self.metadata,
            "assertions": [a.to_dict() for a in self.assertions]
        }
    
    def save(self, path: str):
        """Save config to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> "ValidationConfig":
        """Load config from JSON file."""
        with open(path) as f:
            data = json.load(f)
        
        assertions = [AssertionConfig.from_dict(a) for a in data.get("assertions", [])]
        
        return cls(
            name=data["name"],
            model=data["model"],
            assertions=assertions,
            threshold=data.get("threshold", 70.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class AssertionResult:
    """Result of checking a single assertion."""
    name: str
    type: str
    passed: bool
    message: str
    score: float
    weight: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "passed": self.passed,
            "message": self.message,
            "score": self.score,
            "weight": self.weight
        }


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
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "output": self.output,
            "score": self.score,
            "passed": self.passed,
            "assertion_results": self.assertion_results,
            "failed_assertions": self.failed_assertions,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        
        lines = [
            f"# Validation Result: {status}",
            f"",
            f"**Score:** {self.score:.1f}/100",
            f"**Threshold:** 70.0",
            f"**Timestamp:** {self.timestamp}",
            f"",
            f"## Failed Assertions",
        ]
        
        if self.failed_assertions:
            for name in self.failed_assertions:
                lines.append(f"- ❌ {name}")
        else:
            lines.append("None - all assertions passed!")
        
        lines.extend([
            "",
            f"## All Assertions",
            "",
            "| Name | Type | Passed | Score | Message |",
            "|------|------|--------|-------|---------|",
        ])
        
        for ar in self.assertion_results:
            icon = "✅" if ar["passed"] else "❌"
            lines.append(f"| {ar['name']} | {ar['type']} | {icon} | {ar['score']:.2f} | {ar['message']} |")
        
        if self.warnings:
            lines.extend(["", "## Warnings"])
            for w in self.warnings:
                lines.append(f"- ⚠️ {w}")
        
        return "\n".join(lines)
