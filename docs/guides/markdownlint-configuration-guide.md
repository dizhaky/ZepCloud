# Comprehensive Markdownlint Configuration Guide

## Overview

This guide demonstrates how to properly set up and customize markdownlint rules within VS Code, including examples of
common rule configurations, explanations of rule severity levels, methods for disabling specific rules either globally
  or inline, and best practices for maintaining consistent markdown formatting across projects. It also covers advanced topics such as creating custom rules, integrating with CI/CD pipelines, and troubleshooting common configuration issues.

## VS Code Extension Setup

To begin using markdownlint in VS Code:

1. Install the markdownlint extension from the VS Code marketplace
2. The extension will automatically lint markdown files when opened
3. Default rules are applied without any additional configuration

## Common Rule Configurations

### Basic Configuration File

Create a `.markdownlint.json` file in your project root to customize rules:

```json

{
  "default": true,
  "MD001": false,
  "MD002": false,
  "MD003": {
    "style": "atx"
  },
  "MD004": {
    "style": "dash"
  },
  "MD007": {
    "indent": 2
  },
  "MD009": {
    "br_spaces": 2
  },
  "MD010": {
    "code_blocks": false
  },
  "MD012": true,
  "MD013": {
    "line_length": 100
  },
  "MD014": false,
  "MD018": true,
  "MD019": true,
  "MD022": true,
  "MD023": true,
  "MD024": false,
  "MD025": {
    "level": 1
  },
  "MD026": {
    "punctuation": ".,;:!"
  },
  "MD027": true,
  "MD028": true,
  "MD029": {
    "style": "ordered"
  },
  "MD030": true,
  "MD031": true,
  "MD032": true,
  "MD033": false,
  "MD034": true,
  "MD035": {
    "style": "---"
  },
  "MD036": false,
  "MD037": true,
  "MD038": true,
  "MD039": true,
  "MD040": true,
  "MD041": false,
  "MD042": true,
  "MD043": false,
  "MD044": false,
  "MD045": true,
  "MD046": {
    "style": "fenced"
  },
  "MD047": true
}

```

### Workspace-Level Configuration

You can also configure markdownlint in your VS Code workspace settings (`settings.json`):

```json

{
  "markdownlint.config": {
    "default": true,
    "MD013": {
      "line_length": 120
    },
    "MD024": false,
    "MD025": {
      "level": 1
    }
  }
}

```

## Rule Severity Levels

Markdownlint rules have two severity levels:

1. **Enabled (true)**: Rule violations will be highlighted as errors
2. **Disabled (false)**: Rule violations will be ignored

Some rules also accept parameters for fine-tuning their behavior:

```json

{
  "MD013": {
    "line_length": 100,
    "heading_line_length": 80,
    "code_block_line_length": 120,
    "code_blocks": true
  }
}

```

## Disabling Rules

### Global Disabling

To disable rules globally, set them to `false` in your configuration file:

```json

{
  "MD001": false,
  "MD024": false
}

```

### Inline Disabling

To disable rules for specific lines, use HTML comments:

```markdown

<!-- markdownlint-disable MD033 -->

## This heading has an inline HTML element: <span>example</span>

<!-- markdownlint-enable MD033 -->

<!-- markdownlint-disable -->
This entire section will ignore all markdownlint rules.
<!-- markdownlint-enable -->

## This heading has trailing punctuation. <!-- markdownlint-disable-line MD026 -->

```

### File-Level Disabling

To disable rules for an entire file, place the comment at the top:

```markdown

<!-- markdownlint-disable MD013 MD024 -->

# This file ignores line length and duplicate heading rules

Content that might violate those rules...

```

## Best Practices

### 1. Consistent Configuration Across Projects

Create a standard `.markdownlint.json` file that can be reused across projects:

```json

{
  "default": true,
  "MD013": {
    "line_length": 100
  },
  "MD007": {
    "indent": 2
  },
  "MD030": {
    "ul_single": 3,
    "ol_single": 2
  }
}

```

### 2. Team Configuration

Share configuration files in your repository to ensure consistent linting across team members:

- Include `.markdownlint.json` in version control
- Document any project-specific rule exceptions
- Use workspace settings for team-wide configurations

### 3. Rule Selection

Enable rules that improve readability and consistency:

```json

{
  "MD022": true,  // Headings should be surrounded by blank lines
  "MD023": true,  // Headings must start at the beginning of the line
  "MD031": true,  // Fenced code blocks should be surrounded by blank lines
  "MD032": true,  // Lists should be surrounded by blank lines
  "MD047": true   // Files should end with a single newline character
}

```

## Advanced Topics

### Custom Rules

You can create custom rules by implementing them in JavaScript and referencing them in your configuration:

```json

{
  "custom-rules": {
    "folder": "./markdownlint-custom-rules"
  }
}

```

### CI/CD Integration

To integrate markdownlint with your CI/CD pipeline, install it as a development dependency:

```bash

npm install markdownlint-cli --save-dev

```

Then create a script in your `package.json`:

```json

{
  "scripts": {
    "lint:md": "markdownlint \"**/*.md\" --ignore node_modules"
  }
}

```

For GitHub Actions, create a workflow file:

```yaml

name: Markdownlint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v2
      - run: npm install markdownlint-cli
      - run: npx markdownlint "**/*.md" --ignore node_modules

```

### Troubleshooting Common Issues

#### 1. Rules Not Being Applied

Check that:

- Your configuration file is named correctly (`.markdownlint.json`)
- The file is in the correct location (project root)
- Rule names are spelled correctly
- VS Code has reloaded the configuration

#### 2. Conflicting Rules

Some rules may conflict with each other. For example:

```json

{
  "MD013": { "line_length": 80 },  // Line length limit
  "MD004": { "style": "sublist" }  // Sublist indentation
}

```

Adjust parameters to resolve conflicts:

```json

{
  "MD013": {
    "line_length": 100,
    "code_blocks": false
  }
}

```

#### 3. Performance Issues

For large projects, you might want to ignore certain directories:

```bash

markdownlint "**/*.md" --ignore node_modules --ignore docs/generated

```

Or in your configuration file:

```json

{
  "ignore": [
    "node_modules/",
    "docs/generated/"
  ]
}

```

## Conclusion

Properly configuring markdownlint in VS Code helps maintain consistent documentation standards across your projects. By
understanding how to customize rules, disable them when needed, and integrate with your development workflow, you can
  ensure your markdown files are clean, readable, and follow best practices.
