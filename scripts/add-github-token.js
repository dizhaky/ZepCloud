#!/usr/bin/env node

/**
 * Simple script to add GitHub token to MCP configuration
 * Usage: node scripts/add-github-token.js <token>
 */

const fs = require('fs');
const path = require('path');

const token = process.argv[2];

if (!token) {
    console.log('❌ Error: GitHub token required');
    console.log('');
    console.log('Usage: node scripts/add-github-token.js <your-github-token>');
    console.log('');
    console.log('Example:');
    console.log('  node scripts/add-github-token.js ghp_1234567890abcdef');
    console.log('');
    console.log('Get your token from: https://github.com/settings/tokens');
    process.exit(1);
}

if (!token.startsWith('ghp_') && !token.startsWith('github_pat_')) {
    console.log('⚠️  Warning: Token should start with "ghp_" or "github_pat_"');
    console.log('   Make sure you copied the correct token');
    console.log('');
}

const mcpConfigPath = path.join(__dirname, '..', '.cursor', 'mcp.json');

try {
    // Read current configuration
    const mcpConfig = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf8'));
    
    // Update GitHub token
    if (mcpConfig.mcpServers.github) {
        mcpConfig.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = token;
        
        // Write updated configuration
        fs.writeFileSync(mcpConfigPath, JSON.stringify(mcpConfig, null, 2));
        
        console.log('✅ GitHub token added to MCP configuration');
        console.log(`   File: ${mcpConfigPath}`);
        console.log(`   Token: ${token.substring(0, 10)}...${token.substring(token.length - 10)}`);
        console.log('');
        console.log('🔄 Next steps:');
        console.log('1. Restart Cursor to reload MCP configuration');
        console.log('2. Run: npm run mcp:health');
        console.log('3. Verify GitHub MCP is working');
        
    } else {
        console.log('❌ Error: GitHub MCP server not found in configuration');
        console.log('   Make sure .cursor/mcp.json has a "github" section');
        process.exit(1);
    }
    
} catch (error) {
    console.log('❌ Error updating MCP configuration:');
    console.log(`   ${error.message}`);
    process.exit(1);
}
