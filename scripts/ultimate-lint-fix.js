#!/usr/bin/env node

/**
 * Ultimate Lint Fix for Final Issues
 * 
 * This script handles the final 4 linting issues:
 * - MD042: No empty links (3 cases)
 * - MD026: Trailing punctuation in heading (1 case)
 */

const fs = require('fs');
const path = require('path');

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

function fixFinalIssues(content) {
  let fixedContent = content;
  
  // MD042: Remove empty links - convert to plain text
  fixedContent = fixedContent.replace(/\[([^\]]*)\]\(\)/g, '$1');
  
  // MD026: Remove trailing punctuation from headings
  fixedContent = fixedContent.replace(/^(#{1,6}\s.*)[.:!?]+$/gm, '$1');
  
  return fixedContent;
}

function fixMarkdownFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const fixedContent = fixFinalIssues(content);
  
  if (fixedContent !== content) {
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    return true;
  }
  
  return false;
}

function main() {
  log('🔧 Ultimate lint fix for final 4 issues...', 'cyan');
  
  // The file with final issues
  const fileToFix = 'apps/hetzner-m365-rag/README.md';
  const fullPath = path.join(PROJECT_ROOT, fileToFix);
  
  if (!fs.existsSync(fullPath)) {
    log(`⚠️  File not found: ${fileToFix}`, 'yellow');
    return;
  }
  
  try {
    const wasFixed = fixMarkdownFile(fullPath);
    
    if (wasFixed) {
      log(`✅ Fixed: ${fileToFix}`, 'green');
    } else {
      log(`⚪ No issues: ${fileToFix}`, 'yellow');
    }
  } catch (error) {
    log(`❌ Error fixing ${fileToFix}: ${error.message}`, 'red');
  }
  
  log(`\n🎉 Ultimate lint fix completed!`, 'green');
}

if (require.main === module) {
  main();
}

module.exports = { fixMarkdownFile };
