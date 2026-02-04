"""
LLM Validator - AI Output Testing & Validation Framework

A production-ready framework for validating AI/LLM outputs 
against user-defined assertions, confidence scoring, and edge case testing.
"""

__version__ = "1.0.0"
__author__ = "Claw"

from .core import LLMValidator, ValidationResult
from .assertions import Assertion, AssertionType
from .models import ValidationConfig, AssertionConfig

__all__ = [
    "LLMValidator",
    "ValidationResult", 
    "Assertion",
    "AssertionType",
    "ValidationConfig",
    "AssertionConfig",
]
