# Markdownlint Configuration Guide

## Overview

This project uses [vscode-markdownlint](https://github.com/DavidAnson/vscode-markdownlint#configure) for markdown linting and style checking. Configuration is managed through `.markdownlint.json` files.

## Configuration Hierarchy

Markdownlint uses the following configuration priority (highest to lowest):

1. **Inline comments** in markdown files (`<!-- markdownlint-disable -->`)
2. **Project-local configuration** (`.markdownlint.json` in project root)
3. **Workspace settings** (`markdownlint.config` in VS Code settings)
4. **User settings** (global VS Code user settings)
5. **Default configuration** (built-in rules)

## Project Configuration

The project root contains `.markdownlint.json` with these customizations:

### Relaxed Rules

- **MD013**: Line length increased to 120 characters (from 80)
  - Code blocks and tables exempt from line length rules
  - Headings exempt from line length rules

- **MD034**: Bare URLs allowed (useful for documentation)

- **MD040**: Code blocks without language specification allowed

- **MD041**: First line doesn't need to be top-level heading

### Strict Rules Maintained

- **MD022**: Headings must have blank lines above and below
- **MD032**: Lists must be surrounded by blank lines
- **MD031**: Fenced code blocks must be surrounded by blank lines

### HTML Elements

Limited HTML is allowed for enhanced documentation:

- `<br>` - Line breaks
- `<details>` / `<summary>` - Collapsible sections
- `<img>` - Images with attributes
- `<a>` - Links with attributes

## Per-File Configuration

### Disable Rules for Specific Sections

```markdown

<!-- markdownlint-disable MD013 MD033 -->
This section can have long lines and HTML elements.
<!-- markdownlint-enable MD013 MD033 -->

```

### Disable Rules for Single Line

```markdown

<!-- markdownlint-disable-next-line MD013 -->
This is an exceptionally long line that exceeds the normal character limit but is necessary for documentation purposes.

```

### Disable Rules for Entire File

```markdown

<!-- markdownlint-disable-file MD013 -->

# Document Title

All content in this file can have long lines.

```

## VS Code Workspace Settings

For project-specific VS Code settings, add to `.vscode/settings.json`:

```json

{
  "markdownlint.config": {
    "MD003": { "style": "atx_closed" },
    "MD007": { "indent": 4 }
  },
  "markdownlint.focusMode": false,
  "markdownlint.run": "onType"
}

```

## Common Rule Reference

| Rule | Name | Description | Project Setting |
|------|------|-------------|-----------------|
| MD001 | heading-increment | Heading levels increment by one | ✅ Enabled |
| MD003 | heading-style | Heading style (atx, setext) | ✅ Enabled |
| MD007 | ul-indent | Unordered list indentation | ✅ Enabled |
| MD009 | no-trailing-spaces | No trailing spaces | ✅ Enabled |
| MD010 | no-hard-tabs | No hard tabs | ✅ Enabled |
| MD012 | no-multiple-blanks | No multiple blank lines | ✅ Enabled |
| MD013 | line-length | Line length limit | ⚙️ 120 chars |
| MD022 | blanks-around-headings | Headings need blank lines | ✅ Enabled |
| MD023 | heading-start-left | Headings start at beginning | ✅ Enabled |
| MD024 | no-duplicate-heading | No duplicate headings | ⚙️ Siblings only |
| MD025 | single-title | Single top-level heading | ❌ Disabled |
| MD031 | blanks-around-fences | Blank lines around fences | ✅ Enabled |
| MD032 | blanks-around-lists | Blank lines around lists | ✅ Enabled |
| MD033 | no-inline-html | No inline HTML | ⚙️ Some allowed |
| MD034 | no-bare-urls | Bare URLs not allowed | ❌ Disabled |
| MD040 | fenced-code-language | Code blocks need language | ❌ Disabled |
| MD041 | first-line-heading | First line top-level heading | ❌ Disabled |
| MD046 | code-block-style | Code block style | ⚙️ Fenced only |
| MD047 | single-trailing-newline | Single trailing newline | ✅ Enabled |

## Focus Mode

Focus mode reduces distractions by hiding linting issues near the cursor:

```json

{
  "markdownlint.focusMode": true  // Hide issues on current line
}

```

Or ignore N lines above and below:

```json

{
  "markdownlint.focusMode": 2  // Ignore 2 lines above and below cursor
}

```

## Run Mode

Control when linting occurs:

```json

{
  "markdownlint.run": "onType"   // Default: lint as you type
}

```

Or lint only on save:

```json

{
  "markdownlint.run": "onSave"   // Lint only when saving
}

```

## Custom Configuration Files

### markdownlint-cli2 Support

The extension also supports `.markdownlint-cli2.jsonc` for advanced configuration:

```jsonc

{
  "config": {
    "MD013": {
      "line_length": 120
    }
  },
  "globs": [
    "**/*.md",
    "!**/node_modules/**",
    "!**/vendor/**"
  ],
  "ignores": [
    "**/CHANGELOG.md"
  ]
}

```

### Configuration File Priority

1. `.markdownlint-cli2.jsonc`
2. `.markdownlint-cli2.yaml`
3. `.markdownlint-cli2.cjs`
4. `.markdownlint.jsonc`
5. `.markdownlint.json`
6. `.markdownlint.yaml`
7. `.markdownlint.yml`
8. `.markdownlint.cjs`

## Snippets

Use these snippets in markdown files (press `Ctrl+Space` for IntelliSense):

| Snippet | Description |
|---------|-------------|
| `markdownlint-disable` | Disable rules for a section |
| `markdownlint-enable` | Re-enable rules |
| `markdownlint-disable-line` | Disable for current line |
| `markdownlint-disable-next-line` | Disable for next line |
| `markdownlint-capture` | Capture current configuration |
| `markdownlint-restore` | Restore captured configuration |
| `markdownlint-disable-file` | Disable for entire file |
| `markdownlint-enable-file` | Enable for entire file |
| `markdownlint-configure-file` | Configure specific rules |

## Fixing Common Issues

### MD022: Headings should be surrounded by blank lines

## Problem:

```markdown

## Section Title

Content immediately after heading.

```

## Fix:

```markdown

## Section Title (2)

Content with blank line after heading.

```

### MD032: Lists should be surrounded by blank lines

## Problem: (2)

```markdown

Some text.

- List item 1
- List item 2

More text.

```

## Fix: (2)

```markdown

Some text.

- List item 1
- List item 2

More text.

```

### MD040: Fenced code blocks should have a language specified

## Problem: (3)

```markdown

\`\`\`
code here
\`\`\`

```

## Fix: (3)

```markdown

\`\`\`javascript
code here
\`\`\`

```

Or disable the rule in `.markdownlint.json`.

### MD047: Files should end with a single newline

**Problem:** File doesn't end with newline or has multiple trailing newlines.

**Fix:** Ensure file ends with exactly one blank line.

## Auto-Fix on Save

Enable auto-fix in VS Code settings:

```json

{
  "editor.codeActionsOnSave": {
    "source.fixAll.markdownlint": "explicit"
  }
}

```

## Workspace-Specific Configuration

For the ZepCloud project, we use:

- **120 character line length** for better readability
- **Bare URLs allowed** for documentation references
- **Code blocks without language** allowed for generic examples
- **Multiple H1 headings** allowed for complex documents

## Ignoring Files

Create `.markdownlintignore` to exclude files:

```

node_modules/
vendor/
**/CHANGELOG.md
**/.git/

```

## Command Palette Commands

| Command | Description |
|---------|-------------|
| `markdownlint.openConfigFile` | Open/create config file |
| `markdownlint.fixAll` | Fix all auto-fixable issues |
| `markdownlint.toggleLinting` | Enable/disable linting |
| `markdownlint.lintWorkspace` | Lint all markdown files |

## Troubleshooting

### Rules Not Applied

1. Check configuration file syntax (valid JSON)
2. Restart VS Code after changing `.cjs` files
3. Check file is recognized as markdown (bottom-right status bar)
4. Verify extension is installed and enabled

### Configuration Not Found

- Run `markdownlint.openConfigFile` command
- Creates default config if none exists
- Saves to workspace root

### Performance Issues

If linting is slow:

```json

{
  "markdownlint.run": "onSave",
  "markdownlint.focusMode": true
}

```

## Best Practices

1. **Project config over user config**: Use `.markdownlint.json` for team consistency
2. **Disable sparingly**: Only disable rules when truly necessary
3. **Inline comments**: Use for rare exceptions, not widespread issues
4. **Document exceptions**: Comment why rules are disabled
5. **Auto-fix**: Enable auto-fix on save for automatic corrections

## References

- [vscode-markdownlint GitHub](https://github.com/DavidAnson/vscode-markdownlint#configure)
- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)

---

**Last Updated**: October 19, 2025
**Configuration Version**: 1.0
