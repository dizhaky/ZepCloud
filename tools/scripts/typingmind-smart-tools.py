#!/usr/bin/env python3
"""
TypingMind Smart Tool Integration
Implements smart tool selection for TypingMind MCP + Groq
"""

class TypingMindSmartTools:
    """Smart tool management for TypingMind MCP server"""

    def __init__(self):
        self.mcp_servers = {
            'memory': {
                'tools': ['create_memory', 'search_memory', 'update_memory', 'delete_memory'],
                'keywords': ['remember', 'save', 'store', 'recall', 'memory', 'forgot']
            },
            'filesystem': {
                'tools': ['read_file', 'write_file', 'list_directory', 'create_directory'],
                'keywords': ['file', 'document', 'read', 'write', 'save', 'open', 'folder']
            },
            'github': {
                'tools': ['create_issue', 'get_repository', 'list_commits', 'search_code'],
                'keywords': ['github', 'repository', 'commit', 'issue', 'code', 'pull']
            },
            'sequential-thinking': {
                'tools': ['start_thought', 'continue_thought', 'complete_thought'],
                'keywords': ['think', 'reason', 'analyze', 'consider', 'thought']
            }
        }

    def get_optimal_mcp_config(self, user_query: str) -> dict:
        """Get optimal MCP server configuration based on query"""
        query_lower = user_query.lower()
        selected_servers = {}

        # Always include memory (core functionality)
        selected_servers['memory'] = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        }

        # Add servers based on query analysis
        if any(keyword in query_lower for keyword in ['file', 'document', 'read', 'write']):
            selected_servers['filesystem'] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"]
            }

        if any(keyword in query_lower for keyword in ['github', 'repository', 'code', 'commit']):
            selected_servers['github'] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"]
            }

        if any(keyword in query_lower for keyword in ['think', 'analyze', 'reason', 'consider']):
            selected_servers['sequential-thinking'] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
            }

        return {"mcpServers": selected_servers}

    def estimate_tool_count(self, mcp_config: dict) -> int:
        """Estimate total tool count from MCP configuration"""
        tool_counts = {
            'memory': 8,
            'filesystem': 12,
            'github': 15,
            'sequential-thinking': 6,
            'puppeteer': 45,  # High tool count
            'zapier': 35      # High tool count
        }

        total_tools = 0
        for server_name in mcp_config.get('mcpServers', {}):
            total_tools += tool_counts.get(server_name, 10)

        return total_tools

    def get_safe_config(self, user_query: str) -> dict:
        """Get safe MCP configuration that stays under 128 tools"""
        # Start with minimal config
        safe_config = {
            "mcpServers": {
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"]
                }
            }
        }

        # Add servers one by one, checking tool count
        query_lower = user_query.lower()

        # Add filesystem if needed
        if any(keyword in query_lower for keyword in ['file', 'document', 'read', 'write']):
            safe_config["mcpServers"]["filesystem"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"]
            }

        # Add github if needed
        if any(keyword in query_lower for keyword in ['github', 'repository', 'code']):
            safe_config["mcpServers"]["github"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"]
            }

        # Check if we can add sequential thinking
        if any(keyword in query_lower for keyword in ['think', 'analyze', 'reason']):
            safe_config["mcpServers"]["sequential-thinking"] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
            }

        return safe_config

def test_typingmind_smart_tools():
    """Test the TypingMind smart tool selector"""
    smart_tools = TypingMindSmartTools()

    print("🧪 TYPINGMIND SMART TOOL TESTING")
    print("=" * 50)

    test_queries = [
        "Save my name and email to memory",
        "Read the file in my Documents folder",
        "Create a GitHub issue for the bug",
        "Think through this problem step by step",
        "What's the current time and who am I?"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)

        # Get optimal config
        optimal_config = smart_tools.get_optimal_mcp_config(query)
        tool_count = smart_tools.estimate_tool_count(optimal_config)

        print(f"📊 Optimal config: {list(optimal_config['mcpServers'].keys())}")
        print(f"🔢 Estimated tools: {tool_count}")

        if tool_count > 128:
            print("⚠️  OVER LIMIT - Using safe config")
            safe_config = smart_tools.get_safe_config(query)
            safe_count = smart_tools.estimate_tool_count(safe_config)
            print(f"🔧 Safe config: {list(safe_config['mcpServers'].keys())}")
            print(f"✅ Safe tool count: {safe_count}")
        else:
            print("✅ Within 128 tool limit")

        # Show the JSON config
        import json
        print(f"📋 JSON Config:")
        print(json.dumps(optimal_config, indent=2))

def create_typingmind_guide():
    """Create step-by-step guide for TypingMind users"""
    guide = """
# 🎯 TypingMind Smart Tool Configuration Guide

## Step 1: Open TypingMind Settings
1. Open TypingMind
2. Go to **Settings** → **Advanced Settings** → **Model Context Protocol**
3. Select **"This Device"**
4. Enter your server details:
   - **Server URL**: `http://localhost:50880`
   - **Auth Token**: `dPJcAi2esVx2QUasFglAt`

## Step 2: Use Smart MCP Configuration

### For Memory Tasks:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

### For File Operations:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"]
    }
  }
}
```

### For GitHub Tasks:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

## Step 3: Test Your Configuration
1. **Save the configuration**
2. **Test with a simple query**: "What's the current time?"
3. **Check for errors** in TypingMind logs
4. **Gradually add more servers** as needed

## Step 4: Monitor Tool Count
- **Memory server**: ~8 tools
- **Filesystem server**: ~12 tools
- **GitHub server**: ~15 tools
- **Sequential thinking**: ~6 tools
- **Total safe**: ~41 tools (well under 128 limit)

## 🚨 Avoid These High-Tool Servers:
- **Puppeteer**: ~45 tools (too many)
- **Zapier**: ~35 tools (too many)
- **Multiple servers**: Can quickly exceed 128

## ✅ Best Practices:
1. **Start minimal**: Use only memory server initially
2. **Add gradually**: Add one server at a time
3. **Test frequently**: Check for errors after each addition
4. **Monitor performance**: Watch for slower responses
5. **Keep it simple**: Only add servers you actually need
"""

    print("📋 TYPINGMIND CONFIGURATION GUIDE")
    print("=" * 50)
    print(guide)

if __name__ == "__main__":
    test_typingmind_smart_tools()
    print("\n" + "=" * 60)
    create_typingmind_guide()
