#!/usr/bin/env node

/**
 * Auto-fix Markdown Linting Issues
 * 
 * This script automatically fixes common markdownlint issues:
 * - MD013: Line length (wraps long lines)
 * - MD022: Blanks around headings
 * - MD031: Blanks around fenced code blocks
 * - MD032: Blanks around lists
 * - MD009: Trailing spaces
 * - MD012: Multiple consecutive blank lines
 * - MD026: Trailing punctuation in headings
 * - MD047: Single trailing newline
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

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

function findMarkdownFiles(dir) {
  const files = [];
  
  function traverse(currentDir) {
    const items = fs.readdirSync(currentDir);
    
    for (const item of items) {
      const fullPath = path.join(currentDir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        // Skip node_modules, .git, and other common directories
        if (!['node_modules', '.git', '.cursor', '.taskmaster', '.kilo', '.kilocode'].includes(item)) {
          traverse(fullPath);
        }
      } else if (item.endsWith('.md')) {
        files.push(fullPath);
      }
    }
  }
  
  traverse(dir);
  return files;
}

function wrapLongLine(line, maxLength) {
  if (line.length <= maxLength) {
    return line;
  }
  
  // Don't wrap code blocks, tables, or URLs
  if (line.startsWith('```') || line.startsWith('|') || line.includes('http')) {
    return line;
  }
  
  // Don't wrap lines that are mostly URLs or code
  if (line.includes('://') && line.length < maxLength * 1.5) {
    return line;
  }
  
  // Find a good break point
  let breakPoint = maxLength;
  const lastSpace = line.lastIndexOf(' ', maxLength);
  const lastHyphen = line.lastIndexOf('-', maxLength);
  const lastComma = line.lastIndexOf(',', maxLength);
  
  // Prefer breaking at spaces, then hyphens, then commas
  if (lastSpace > maxLength * 0.8) {
    breakPoint = lastSpace;
  } else if (lastHyphen > maxLength * 0.8) {
    breakPoint = lastHyphen;
  } else if (lastComma > maxLength * 0.8) {
    breakPoint = lastComma;
  }
  
  const firstPart = line.substring(0, breakPoint).trim();
  const secondPart = line.substring(breakPoint).trim();
  
  // Add proper indentation for continuation
  const indent = firstPart.match(/^(\s*)/)[1];
  const continuationIndent = indent + '  ';
  
  return `${firstPart}\n${continuationIndent}${secondPart}`;
}

function fixMarkdownFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const originalLine = line;
    
    // MD009: Remove trailing spaces
    if (line !== line.trimEnd()) {
      line = line.trimEnd();
      modified = true;
    }
    
    // MD013: Wrap long lines (but be smart about it)
    if (line.length > MAX_LINE_LENGTH) {
      const wrapped = wrapLongLine(line, MAX_LINE_LENGTH);
      if (wrapped !== line) {
        line = wrapped;
        modified = true;
      }
    }
    
    // MD022: Add blank lines around headings
    if (line.match(/^#{1,6}\s/)) {
      // Check if there's a blank line before
      if (i > 0 && fixedLines[fixedLines.length - 1].trim() !== '') {
        fixedLines.push('');
        modified = true;
      }
      
      fixedLines.push(line);
      
      // Check if there's a blank line after
      if (i < lines.length - 1 && lines[i + 1].trim() !== '') {
        fixedLines.push('');
        modified = true;
      }
      continue;
    }
    
    // MD031: Add blank lines around fenced code blocks
    if (line.startsWith('```')) {
      // Check if there's a blank line before
      if (i > 0 && fixedLines[fixedLines.length - 1].trim() !== '') {
        fixedLines.push('');
        modified = true;
      }
      
      fixedLines.push(line);
      
      // Check if there's a blank line after
      if (i < lines.length - 1 && lines[i + 1].trim() !== '') {
        fixedLines.push('');
        modified = true;
      }
      continue;
    }
    
    // MD032: Add blank lines around lists
    if (line.match(/^\s*[-*+]\s/) || line.match(/^\s*\d+\.\s/)) {
      // Check if there's a blank line before
      if (i > 0 && fixedLines[fixedLines.length - 1].trim() !== '' && 
          !fixedLines[fixedLines.length - 1].match(/^\s*[-*+]\s/) &&
          !fixedLines[fixedLines.length - 1].match(/^\s*\d+\.\s/)) {
        fixedLines.push('');
        modified = true;
      }
      
      fixedLines.push(line);
      
      // Check if there's a blank line after
      if (i < lines.length - 1 && lines[i + 1].trim() !== '' &&
          !lines[i + 1].match(/^\s*[-*+]\s/) &&
          !lines[i + 1].match(/^\s*\d+\.\s/)) {
        fixedLines.push('');
        modified = true;
      }
      continue;
    }
    
    // MD012: Remove multiple consecutive blank lines
    if (line.trim() === '') {
      if (fixedLines.length > 0 && fixedLines[fixedLines.length - 1].trim() === '') {
        // Skip this blank line
        continue;
      }
    }
    
    // MD026: Remove trailing punctuation from headings
    if (line.match(/^#{1,6}\s.*[.:!?]$/)) {
      line = line.replace(/[.:!?]+$/, '');
      modified = true;
    }
    
    fixedLines.push(line);
  }
  
  // MD047: Ensure single trailing newline
  let result = fixedLines.join('\n');
  if (!result.endsWith('\n')) {
    result += '\n';
    modified = true;
  }
  
  if (modified) {
    fs.writeFileSync(filePath, result, 'utf8');
    return true;
  }
  
  return false;
}

function main() {
  log('🔧 Auto-fixing Markdown linting issues...', 'cyan');
  log(`📁 Scanning directory: ${PROJECT_ROOT}`, 'blue');
  
  const markdownFiles = findMarkdownFiles(PROJECT_ROOT);
  log(`📄 Found ${markdownFiles.length} Markdown files`, 'blue');
  
  let fixedCount = 0;
  let totalIssues = 0;
  
  for (const file of markdownFiles) {
    const relativePath = path.relative(PROJECT_ROOT, file);
    
    try {
      const wasFixed = fixMarkdownFile(file);
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
  log(`   Files processed: ${markdownFiles.length}`, 'blue');
  log(`   Files fixed: ${fixedCount}`, 'green');
  log(`   Files unchanged: ${markdownFiles.length - fixedCount}`, 'yellow');
  
  if (fixedCount > 0) {
    log(`\n🎉 Auto-fix completed! Run 'npm run lint:markdown' to verify.`, 'green');
  } else {
    log(`\n✨ No issues found to auto-fix!`, 'green');
  }
}

if (require.main === module) {
  main();
}

module.exports = { fixMarkdownFile, findMarkdownFiles };
