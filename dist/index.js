const core = require('@actions/core');
const exec = require('@actions/exec');
const fs = require('fs');
const path = require('path');

async function run() {
  try {
    // Get inputs
    const prompt = core.getInput('prompt', { required: true });
    const output = core.getInput('output', { required: true });
    const configPath = core.getInput('assertions-config', { required: true });
    const threshold = parseFloat(core.getInput('pass-threshold')) || 70;
    const failOnWarning = core.getInput('fail-on-warning') === 'true';

    // Read assertions config
    let config;
    if (fs.existsSync(configPath)) {
      const content = fs.readFileSync(configPath, 'utf8');
      config = JSON.parse(content);
    } else {
      core.setFailed(`Assertions config file not found: ${configPath}`);
      return;
    }

    // Run validation via Python
    let score = 0;
    let passed = false;
    let failedCount = 0;
    let warningsCount = 0;
    const results = [];

    // Simple validation (in production, call the actual validator)
    const assertions = config.assertions || [];
    for (const assertion of assertions) {
      const weight = assertion.weight || 1.0;
      let assertionPassed = true;
      let message = 'Passed';

      // Simple checks
      if (assertion.type === 'MAX_LENGTH' && output.length > (assertion.params?.max_chars || 1000)) {
        assertionPassed = false;
        message = `Output too long: ${output.length} chars`;
      } else if (assertion.type === 'CONTAINS_TEXT') {
        const required = assertion.params?.text;
        if (required && !output.includes(required)) {
          assertionPassed = false;
          message = `Missing required text: "${required}"`;
        }
      } else if (assertion.type === 'NO_PATTERN') {
        const pattern = assertion.params?.pattern;
        if (pattern && new RegExp(pattern, 'i').test(output)) {
          assertionPassed = false;
          message = `Output contains forbidden pattern`;
        }
      }

      results.push({
        name: assertion.name,
        passed: assertionPassed,
        message,
        weight
      });

      if (!assertionPassed) failedCount++;
      score += assertionPassed ? weight : 0;
    }

    // Calculate percentage
    const totalWeight = assertions.reduce((sum, a) => sum + (a.weight || 1.0), 0);
    score = totalWeight > 0 ? Math.round((score / totalWeight) * 100) : 0;
    passed = score >= threshold && failedCount === 0;

    // Set outputs
    core.setOutput('passed', passed.toString());
    core.setOutput('score', score.toString());
    core.setOutput('failed-assertions', failedCount.toString());
    core.setOutput('warnings-count', warningsCount.toString());

    // Print results
    console.log('\n=== LintAI Validation Results ===');
    console.log(`Score: ${score}%`);
    console.log(`Passed: ${passed ? '✓' : '✗'}`);
    console.log(`Failed: ${failedCount}`);
    console.log('================================\n');

    // Set result
    if (passed) {
      console.log(`✓ Validation passed with score ${score}%`);
    } else {
      core.setFailed(`Validation failed! Score: ${score}%, Threshold: ${threshold}%`);
    }
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
