#!/usr/bin/env node

/**
 * Complete Lint Fix for All Remaining Issues
 * 
 * This script handles all remaining linting issues:
 * - MD036: Emphasis used instead of heading
 * - MD042: No empty links
 * - MD022: Blanks around headings
 * - MD032: Blanks around lists
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

function fixAllMarkdownIssues(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const originalLine = line;
    
    // MD036: Convert emphasis to proper headings
    if (line.match(/^\*\*[^*]+\*\*$/) || line.match(/^__[^_]+__$/)) {
      const text = line.replace(/^\*\*|\*\*$/g, '').replace(/^__|__$/g, '');
      line = `## ${text}`;
    }
    
    // MD042: Remove empty links
    if (line.match(/\[([^\]]*)\]\(\)/)) {
      line = line.replace(/\[([^\]]*)\]\(\)/g, '$1');
    }
    
    // MD022 & MD032: Add blank lines around headings and lists
    if (line.match(/^#{1,6}\s/) || line.match(/^\s*[-*+]\s/) || line.match(/^\s*\d+\.\s/)) {
      // Check if there's a blank line before
      if (i > 0 && fixedLines[fixedLines.length - 1].trim() !== '') {
        fixedLines.push('');
      }
      
      fixedLines.push(line);
      
      // Check if there's a blank line after
      if (i < lines.length - 1 && lines[i + 1].trim() !== '') {
        fixedLines.push('');
      }
      continue;
    }
    
    fixedLines.push(line);
  }
  
  return fixedLines.join('\n');
}

function fixMarkdownFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const fixedContent = fixAllMarkdownIssues(content);
  
  if (fixedContent !== content) {
    fs.writeFileSync(filePath, fixedContent, 'utf8');
    return true;
  }
  
  return false;
}

function main() {
  log('🔧 Complete lint fix for all remaining issues...', 'cyan');
  
  // The file with remaining issues
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
  
  log(`\n🎉 Complete lint fix completed!`, 'green');
}

if (require.main === module) {
  main();
}

module.exports = { fixMarkdownFile };
