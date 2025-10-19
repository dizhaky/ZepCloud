#!/usr/bin/env node

/**
 * Auto-fix Remaining Markdown Linting Issues
 * 
 * This script handles the remaining issues that the basic auto-fix couldn't handle:
 * - MD013: Line length (for complex cases)
 * - MD026: Trailing punctuation in headings
 * - MD024: Duplicate headings
 * - PowerShell alias issues
 */

const fs = require('fs');
const path = require('path');

// Configuration
const MAX_LINE_LENGTH = 120;
const PROJECT_ROOT = process.cwd();

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function fixTrailingPunctuationInHeadings(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (const line of lines) {
    if (line.match(/^#{1,6}\s.*[.:!?]$/)) {
      const fixedLine = line.replace(/[.:!?]+$/, '');
      fixedLines.push(fixedLine);
    } else {
      fixedLines.push(line);
    }
  }
  
  return fixedLines.join('\n');
}

function fixDuplicateHeadings(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  const headingCounts = new Map();
  
  for (const line of lines) {
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1];
      const text = headingMatch[2];
      const key = text.toLowerCase().trim();
      
      if (headingCounts.has(key)) {
        const count = headingCounts.get(key) + 1;
        headingCounts.set(key, count);
        // Add a number to make it unique
        const newText = `${text} (${count})`;
        fixedLines.push(`${level} ${newText}`);
      } else {
        headingCounts.set(key, 1);
        fixedLines.push(line);
      }
    } else {
      fixedLines.push(line);
    }
  }
  
  return fixedLines.join('\n');
}

function fixPowerShellAliases(content) {
  // Replace common PowerShell aliases with full commands
  const aliasReplacements = {
    'cd ': 'Set-Location ',
    'ls ': 'Get-ChildItem ',
    'dir ': 'Get-ChildItem ',
    'cat ': 'Get-Content ',
    'cp ': 'Copy-Item ',
    'mv ': 'Move-Item ',
    'rm ': 'Remove-Item ',
    'mkdir ': 'New-Item -ItemType Directory ',
    'rmdir ': 'Remove-Item ',
    'pwd': 'Get-Location',
    'echo ': 'Write-Output ',
    'type ': 'Get-Content '
  };
  
  let fixedContent = content;
  
  for (const [alias, fullCommand] of Object.entries(aliasReplacements)) {
    // Use word boundaries to avoid partial matches
    const regex = new RegExp(`\\b${alias.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'g');
    fixedContent = fixedContent.replace(regex, fullCommand);
  }
  
  return fixedContent;
}

function fixComplexLineLength(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (const line of lines) {
    if (line.length > MAX_LINE_LENGTH) {
      // For very long lines, try to break them more intelligently
      if (line.includes('://') && line.length < MAX_LINE_LENGTH * 1.5) {
        // Keep URLs that are not too long
        fixedLines.push(line);
      } else if (line.startsWith('```') || line.startsWith('|')) {
        // Keep code blocks and tables
        fixedLines.push(line);
      } else {
        // Try to break at natural points
        const wrapped = wrapLongLineIntelligently(line, MAX_LINE_LENGTH);
        fixedLines.push(wrapped);
      }
    } else {
      fixedLines.push(line);
    }
  }
  
  return fixedLines.join('\n');
}

function wrapLongLineIntelligently(line, maxLength) {
  if (line.length <= maxLength) {
    return line;
  }
  
  // Find the best break point
  let bestBreak = maxLength;
  const breakPoints = [
    { char: '.', weight: 0.9 },
    { char: ',', weight: 0.8 },
    { char: ';', weight: 0.7 },
    { char: ' ', weight: 0.6 },
    { char: '-', weight: 0.5 }
  ];
  
  for (const { char, weight } of breakPoints) {
    const lastIndex = line.lastIndexOf(char, maxLength);
    if (lastIndex > maxLength * weight) {
      bestBreak = lastIndex;
      break;
    }
  }
  
  const firstPart = line.substring(0, bestBreak).trim();
  const secondPart = line.substring(bestBreak).trim();
  
  // Add proper indentation
  const indent = firstPart.match(/^(\s*)/)[1];
  const continuationIndent = indent + '  ';
  
  return `${firstPart}\n${continuationIndent}${secondPart}`;
}

function fixMarkdownFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  
  // Fix trailing punctuation in headings
  const contentAfterPunctuation = fixTrailingPunctuationInHeadings(content);
  if (contentAfterPunctuation !== content) {
    content = contentAfterPunctuation;
    modified = true;
  }
  
  // Fix duplicate headings
  const contentAfterDuplicates = fixDuplicateHeadings(content);
  if (contentAfterDuplicates !== content) {
    content = contentAfterDuplicates;
    modified = true;
  }
  
  // Fix complex line length issues
  const contentAfterLineLength = fixComplexLineLength(content);
  if (contentAfterLineLength !== content) {
    content = contentAfterLineLength;
    modified = true;
  }
  
  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    return true;
  }
  
  return false;
}

function fixPowerShellFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const fixedContent = fixPowerShellAliases(content);
  
  if (fixedContent !== content) {
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    return true;
  }
  
  return false;
}

function main() {
  log('🔧 Auto-fixing remaining linting issues...', 'cyan');
  
  // Files with specific issues
  const filesToFix = [
    'apps/hetzner-m365-rag/docs/DISASTER_RECOVERY_AND_BACKUP_SECURITY_PLAN.md',
    'apps/hetzner-m365-rag/docs/SECURITY_ENHANCEMENTS_SUMMARY.md',
    'apps/azure-rag-setup/docs/security/SECURITY_HARDENING_GUIDE.md',
    'apps/azure-rag-setup/docs/MONITORING_AND_ALERTING.md',
    'apps/azure-rag-setup/docs/DISASTER_RECOVERY_AND_BACKUP_SECURITY.md',
    'apps/hetzner-m365-rag/CLI_DEPLOYMENT_GUIDE.md',
    'apps/hetzner-m365-rag/docs/SECURITY_HARDENING_GUIDE.md',
    'apps/hetzner-m365-rag/docs/ROBUST_DEPLOYMENT.md',
    'apps/hetzner-m365-rag/docs/MONITORING_AND_ALERTING_CONFIGURATION.md',
    'apps/hetzner-m365-rag/DEPLOY_COMPLETE_CLI.ps1'
  ];
  
  let fixedCount = 0;
  
  for (const relativePath of filesToFix) {
    const fullPath = path.join(PROJECT_ROOT, relativePath);
    
    if (!fs.existsSync(fullPath)) {
      log(`⚠️  File not found: ${relativePath}`, 'yellow');
      continue;
    }
    
    try {
      let wasFixed = false;
      
      if (relativePath.endsWith('.ps1')) {
        wasFixed = fixPowerShellFile(fullPath);
      } else {
        wasFixed = fixMarkdownFile(fullPath);
      }
      
      if (wasFixed) {
        log(`✅ Fixed: ${relativePath}`, 'green');
        fixedCount++;
      } else {
        log(`⚪ No issues: ${relativePath}`, 'yellow');
      }
    } catch (error) {
      log(`❌ Error fixing ${relativePath}: ${error.message}`, 'red');
    }
  }
  
  log(`\n📊 Summary:`, 'bright');
  log(`   Files processed: ${filesToFix.length}`, 'blue');
  log(`   Files fixed: ${fixedCount}`, 'green');
  log(`   Files unchanged: ${filesToFix.length - fixedCount}`, 'yellow');
  
  if (fixedCount > 0) {
    log(`\n🎉 Remaining issues auto-fix completed!`, 'green');
  } else {
    log(`\n✨ No remaining issues found to auto-fix!`, 'green');
  }
}

if (require.main === module) {
  main();
}

module.exports = { fixMarkdownFile, fixPowerShellFile };
