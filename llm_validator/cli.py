#!/usr/bin/env python3
"""
CLI for LLM Validator.
"""

import json
import click
from pathlib import Path
from llm_validator import LLMValidator, Assertion, AssertionType, ValidationResult


@click.group()
def cli():
    """LLM Validator - AI Output Testing & Validation Framework"""
    pass


@cli.command()
@click.option("--prompt", "-p", help="Input prompt")
@click.option("--output", "-o", help="LLM output to validate")
@click.option("--config", "-c", help="Path to validation config YAML/JSON")
@click.option("--rules", "-r", help="Inline rules (key:value,key:value)")
@click.option("--output-file", "-f", help="Save results to file")
@click.option("--format", "fmt", type=click.Choice(["json", "markdown", "text"]), default="text")
def validate(prompt, output, config, rules, output_file, fmt):
    """Validate an LLM output."""
    
    validator = LLMValidator()
    
    if config:
        result = validator.validate_from_config(prompt or "", output or "", config)
    elif rules:
        assertions = []
        for rule in rules.split(","):
            if ":" in rule:
                key, value = rule.split(":", 1)
                if key == "max_tokens":
                    assertions.append(Assertion.max_length("max_tokens", max_tokens=int(value)))
                elif key == "max_length":
                    assertions.append(Assertion.max_length("max_length", max_chars=int(value)))
                elif key == "min_words":
                    assertions.append(Assertion.min_length("min_words", min_words=int(value)))
        result = validator.validate(prompt or "", output or "", assertions)
    else:
        click.echo("Error: Must provide --config or --rules")
        return
    
    if output_file:
        with open(output_file, "w") as wf:
            if fmt == "json":
                wf.write(result.to_json())
            elif fmt == "markdown":
                wf.write(result.to_markdown())
        click.echo(f"Results saved to {output_file}")
    
    if fmt == "json":
        click.echo(result.to_json())
    elif fmt == "markdown":
        click.echo(result.to_markdown())
    else:
        # Text format
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        click.echo(f"\n{'='*50}")
        click.echo(f"Validation: {status}")
        click.echo(f"Score: {result.score:.1f}/100")
        click.echo(f"{'='*50}")
        
        if result.failed_assertions:
            click.echo(f"\n❌ Failed Assertions ({len(result.failed_assertions)}):")
            for name in result.failed_assertions:
                click.echo(f"  - {name}")
        
        click.echo(f"\n📊 All Assertions:")
        for ar in result.assertion_results:
            icon = "✅" if ar["passed"] else "❌"
            click.echo(f"  {icon} {ar['name']}: {ar['message']}")


@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), help="Input JSONL file")
@click.option("--output", "-o", type=click.Path(), help="Output JSONL file")
@click.option("--config", "-c", type=click.Path(exists=True), required=True, help="Validation config file")
def batch(input, output, config):
    """Run batch validation from JSONL file."""
    from datetime import datetime
    
    validator = LLMValidator()
    
    results = []
    count = 0
    
    with open(input) as infile:
        for line in infile:
            data = json.loads(line.strip())
            result = validator.validate_from_config(
                data.get("prompt", ""),
                data.get("output", ""),
                config,
                metadata=data.get("metadata", {})
            )
            results.append(result.to_dict())
            count += 1
    
    with open(output, "w") as outfile:
        for r in results:
            outfile.write(json.dumps(r) + "\n")
    
    click.echo(f"Processed {count} items")
    click.echo(f"Results saved to {output}")


@cli.command()
@click.argument("name")
@click.option("--model", default="gpt-4", help="Model name")
@click.option("--output", "-o", type=click.Path(), help="Save config to file")
def init_config(name, model, output):
    """Generate a sample validation config."""
    
    config = {
        "name": name,
        "model": model,
        "threshold": 70.0,
        "assertions": [
            {
                "name": "max_length",
                "type": "max_length",
                "params": {"max_tokens": 1000, "max_chars": 10000},
                "weight": 0.2
            },
            {
                "name": "min_length", 
                "type": "min_length",
                "params": {"min_words": 20},
                "weight": 0.1
            },
            {
                "name": "has_action_plan",
                "type": "contains_text",
                "params": {"text": "step", "count": 2},
                "weight": 0.3
            },
            {
                "name": "no_errors",
                "type": "no_pattern",
                "params": {"pattern": "error|fail|exception"},
                "weight": 0.4
            }
        ]
    }
    
    click.echo(json.dumps(config, indent=2))
    
    if output:
        with open(output, "w") as f:
            json.dump(config, f, indent=2)
        click.echo(f"\nConfig saved to {output}")


if __name__ == "__main__":
    cli()
