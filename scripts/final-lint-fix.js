#!/usr/bin/env node

/**
 * Final Lint Fix for Remaining Issues
 * 
 * This script handles the last 2 remaining linting issues:
 * - MD013: Line length (final 2 cases)
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

function fixFinalLineLength(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (const line of lines) {
    if (line.length > MAX_LINE_LENGTH) {
      // For these final cases, we'll be more aggressive with line breaking
      const wrapped = wrapLineAggressively(line, MAX_LINE_LENGTH);
      fixedLines.push(wrapped);
    } else {
      fixedLines.push(line);
    }
  }
  
  return fixedLines.join('\n');
}

function wrapLineAggressively(line, maxLength) {
  if (line.length <= maxLength) {
    return line;
  }
  
  // Find any reasonable break point
  let bestBreak = maxLength;
  
  // Look for spaces, commas, periods, etc.
  for (let i = maxLength; i >= maxLength * 0.7; i--) {
    const char = line[i];
    if (char === ' ' || char === ',' || char === '.' || char === ';' || char === '-') {
      bestBreak = i;
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
  const fixedContent = fixFinalLineLength(content);
  
  if (fixedContent !== content) {
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    return true;
  }
  
  return false;
}

function main() {
  log('🔧 Final lint fix for remaining 2 issues...', 'cyan');
  
  // The last 2 files with issues
  const filesToFix = [
    'apps/hetzner-m365-rag/docs/SECURITY_ENHANCEMENTS_SUMMARY.md',
    'apps/hetzner-m365-rag/docs/SECURITY_HARDENING_GUIDE.md'
  ];
  
  let fixedCount = 0;
  
  for (const relativePath of filesToFix) {
    const fullPath = path.join(PROJECT_ROOT, relativePath);
    
    if (!fs.existsSync(fullPath)) {
      log(`⚠️  File not found: ${relativePath}`, 'yellow');
      continue;
    }
    
    try {
      const wasFixed = fixMarkdownFile(fullPath);
      
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
  
  log(`\n📊 Final Summary:`, 'bright');
  log(`   Files processed: ${filesToFix.length}`, 'blue');
  log(`   Files fixed: ${fixedCount}`, 'green');
  log(`   Files unchanged: ${filesToFix.length - fixedCount}`, 'yellow');
  
  if (fixedCount > 0) {
    log(`\n🎉 All linting issues should now be resolved!`, 'green');
  } else {
    log(`\n✨ No issues found to fix!`, 'green');
  }
}

if (require.main === module) {
  main();
}

module.exports = { fixMarkdownFile };
