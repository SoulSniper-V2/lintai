"""
Example validation configurations for LLM Validator.
"""

# Example 1: Code Review Validator
CODE_REVIEW_VALIDATOR = {
    "name": "code_review",
    "model": "gpt-4",
    "threshold": 75.0,
    "assertions": [
        {
            "name": "has_tests",
            "type": "contains_text",
            "params": {"text": "test", "count": 1},
            "weight": 0.15
        },
        {
            "name": "no_hardcoded_secrets",
            "type": "no_pattern",
            "params": {"pattern": r"api_key|password|secret|token"},
            "weight": 0.25
        },
        {
            "name": "reasonable_length",
            "type": "max_length",
            "params": {"max_tokens": 3000},
            "weight": 0.10
        },
        {
            "name": "has_error_handling",
            "type": "regex_match",
            "params": {"pattern": r"except|try|catch|error|Error"},
            "weight": 0.20
        },
        {
            "name": "no_infinite_loops",
            "type": "no_pattern",
            "params": {"pattern": r"while\s+True\s*:|while\s+1\s*:"},
            "weight": 0.15
        },
        {
            "name": "proper_formatting",
            "type": "regex_match",
            "params": {"pattern": r"\n"},
            "weight": 0.15
        }
    ]
}

# Example 2: Customer Email Validator
CUSTOMER_EMAIL_VALIDATOR = {
    "name": "customer_email",
    "model": "claude-3-opus",
    "threshold": 80.0,
    "assertions": [
        {
            "name": "professional_tone",
            "type": "no_pattern",
            "params": {"pattern": r"omg|wtf|idiot|stupid|dumb"},
            "weight": 0.30
        },
        {
            "name": "has_greeting",
            "type": "contains_text",
            "params": {"text": "Dear|Hello|Hi|Good morning|Good afternoon", "count": 1},
            "weight": 0.10
        },
        {
            "name": "has_signature",
            "type": "contains_text",
            "params": {"text": "Sincerely|Best|Thanks|Regards", "count": 1},
            "weight": 0.10
        },
        {
            "name": "no_pii",
            "type": "no_pattern",
            "params": {"pattern": r"\d{3}-\d{2}-\d{4}"},  # SSN pattern
            "weight": 0.25
        },
        {
            "name": "helpful_length",
            "type": "min_length",
            "params": {"min_words": 30},
            "weight": 0.15
        },
        {
            "name": "actionable",
            "type": "contains_text",
            "params": {"text": "can|will|please|help|assist", "count": 1},
            "weight": 0.10
        }
    ]
}

# Example 3: Documentation Validator
DOCUMENTATION_VALIDATOR = {
    "name": "documentation",
    "model": "gpt-4",
    "threshold": 70.0,
    "assertions": [
        {
            "name": "has_headings",
            "type": "regex_match",
            "params": {"pattern": r"^#+"},
            "weight": 0.15
        },
        {
            "name": "has_code_examples",
            "type": "contains_text",
            "params": {"text": "```", "count": 1},
            "weight": 0.20
        },
        {
            "name": "readable_length",
            "type": "min_length",
            "params": {"min_words": 50},
            "weight": 0.10
        },
        {
            "name": "not_too_long",
            "type": "max_length",
            "params": {"max_tokens": 2000},
            "weight": 0.10
        },
        {
            "name": "clear_purpose",
            "type": "contains_text",
            "params": {"text": "purpose|goal|objective|This document"},
            "weight": 0.25
        },
        {
            "name": "no_placeholder_text",
            "type": "no_pattern",
            "params": {"pattern": r"TODO|FIXME|XXX|Lorem ipsum"},
            "weight": 0.20
        }
    ]
}

# Example 4: JSON Output Validator
JSON_OUTPUT_VALIDATOR = {
    "name": "json_output",
    "model": "gpt-4",
    "threshold": 85.0,
    "assertions": [
        {
            "name": "valid_json",
            "type": "json_valid",
            "params": {},
            "weight": 0.40
        },
        {
            "name": "has_required_fields",
            "type": "contains_text",
            "params": {"text": "\"status\"|\"result\"|\"data\"", "count": 1},
            "weight": 0.20
        },
        {
            "name": "reasonable_size",
            "type": "max_length",
            "params": {"max_chars": 5000},
            "weight": 0.20
        },
        {
            "name": "no_error_key",
            "type": "no_pattern",
            "params": {"pattern": r"\"error\""},
            "weight": 0.20
        }
    ]
}
