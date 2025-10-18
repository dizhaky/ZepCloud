#!/usr/bin/env python3
"""
Smart Tool Selector for TypingMind MCP + Groq
Implements dynamic tool selection to stay under 128 tool limit
"""

import re
from typing import List, Dict, Any

class SmartToolSelector:
    """Intelligent tool selection based on query context"""

    def __init__(self):
        self.tool_categories = {
            'memory': {
                'keywords': ['remember', 'save', 'store', 'recall', 'memory', 'forgot'],
                'tools': ['create_memory', 'search_memory', 'update_memory', 'delete_memory']
            },
            'filesystem': {
                'keywords': ['file', 'document', 'read', 'write', 'save', 'open', 'folder', 'directory'],
                'tools': ['read_file', 'write_file', 'list_directory', 'create_directory', 'delete_file']
            },
            'github': {
                'keywords': ['github', 'repository', 'commit', 'pull', 'push', 'issue', 'pr', 'code'],
                'tools': ['create_issue', 'get_repository', 'list_commits', 'create_pull_request', 'search_code']
            },
            'search': {
                'keywords': ['search', 'find', 'lookup', 'google', 'web', 'internet', 'browse'],
                'tools': ['web_search', 'image_search', 'news_search', 'academic_search']
            },
            'calculation': {
                'keywords': ['calculate', 'math', 'compute', 'number', 'formula', 'equation', 'solve'],
                'tools': ['calculate_expression', 'solve_equation', 'statistical_analysis', 'graph_plot']
            },
            'communication': {
                'keywords': ['email', 'send', 'message', 'notify', 'contact', 'mail'],
                'tools': ['send_email', 'create_message', 'schedule_notification', 'contact_user']
            }
        }

        # Core tools that are always included
        self.core_tools = [
            'get_current_time',
            'get_user_info',
            'log_interaction',
            'help_user'
        ]

    def analyze_query(self, query: str) -> Dict[str, int]:
        """Analyze query to determine relevant tool categories"""
        query_lower = query.lower()
        category_scores = {}

        for category, config in self.tool_categories.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in query_lower:
                    score += 1
            category_scores[category] = score

        return category_scores

    def select_tools(self, all_tools: List[Dict[str, Any]], query: str, max_tools: int = 128) -> List[Dict[str, Any]]:
        """Select relevant tools based on query analysis"""
        print(f"🔍 Analyzing query: '{query}'")

        # Analyze query to get category scores
        category_scores = self.analyze_query(query)
        print(f"📊 Category scores: {category_scores}")

        selected_tools = []

        # Always include core tools first
        for tool in all_tools:
            if tool.get('name') in self.core_tools:
                selected_tools.append(tool)
                print(f"  ✅ Added core tool: {tool.get('name')}")

        # Add tools from relevant categories
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

        for category, score in sorted_categories:
            if score > 0:  # Only include categories with matches
                print(f"  🎯 Category '{category}' (score: {score})")

                # Get tools for this category
                category_tools = self.tool_categories[category]['tools']

                for tool in all_tools:
                    if len(selected_tools) >= max_tools:
                        break

                    tool_name = tool.get('name', '')
                    if tool_name in category_tools and tool not in selected_tools:
                        selected_tools.append(tool)
                        print(f"    ✅ Added: {tool_name}")

        # If we still have room, add some general tools
        if len(selected_tools) < max_tools:
            for tool in all_tools:
                if len(selected_tools) >= max_tools:
                    break
                if tool not in selected_tools:
                    selected_tools.append(tool)
                    print(f"  📦 Added general tool: {tool.get('name')}")

        # Safety check
        if len(selected_tools) > max_tools:
            selected_tools = selected_tools[:max_tools]
            print(f"  ⚠️  Limited to {max_tools} tools")

        print(f"🎉 Selected {len(selected_tools)} tools for query")
        return selected_tools

    def get_tool_recommendations(self, query: str) -> List[str]:
        """Get tool recommendations for a query"""
        category_scores = self.analyze_query(query)
        recommendations = []

        for category, score in category_scores.items():
            if score > 0:
                recommendations.extend(self.tool_categories[category]['tools'])

        return list(set(recommendations))  # Remove duplicates

def test_smart_selection():
    """Test the smart tool selector with example queries"""
    selector = SmartToolSelector()

    # Create example tools (simulating your MCP server tools)
    example_tools = []

    # Add core tools
    for tool_name in selector.core_tools:
        example_tools.append({"name": tool_name, "type": "function"})

    # Add category tools
    for category, config in selector.tool_categories.items():
        for tool_name in config['tools']:
            example_tools.append({"name": tool_name, "type": "function"})

    # Add some extra tools to exceed limit
    for i in range(100):
        example_tools.append({"name": f"extra_tool_{i}", "type": "function"})

    print(f"🧪 Testing Smart Tool Selection")
    print(f"📊 Total available tools: {len(example_tools)}")
    print("=" * 60)

    # Test queries
    test_queries = [
        "Save my name and email to memory",
        "Search for information about machine learning",
        "Read the file in my Documents folder",
        "Create a GitHub issue for the bug",
        "Calculate the square root of 144",
        "Send an email to my team",
        "What time is it and who am I?"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)

        selected_tools = selector.select_tools(example_tools, query)

        print(f"✅ Result: {len(selected_tools)} tools selected")
        print(f"📋 Tool names: {[tool['name'] for tool in selected_tools[:5]]}...")

        # Verify we're under limit
        if len(selected_tools) <= 128:
            print("✅ SUCCESS: Under 128 tool limit")
        else:
            print("❌ ERROR: Still over 128 tool limit")

def create_typingmind_integration():
    """Create integration code for TypingMind"""
    integration_code = '''
# TypingMind Integration Code
def call_groq_with_smart_tools(user_query, all_tools):
    """Use smart tool selection with Groq API"""
    selector = SmartToolSelector()

    # Select relevant tools
    selected_tools = selector.select_tools(all_tools, user_query)

    # Verify tool count
    if len(selected_tools) > 128:
        print(f"⚠️  WARNING: {len(selected_tools)} tools still exceeds limit")
        selected_tools = selected_tools[:128]
        print(f"🔧 Limited to 128 tools")

    # Make Groq API call
    import groq
    client = groq.Groq(api_key="your-api-key")

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": user_query}],
        tools=selected_tools,  # ← Now under 128!
        max_completion_tokens=4096
    )

    return response

# Usage example
user_query = "Save my contact information to memory"
all_tools = get_all_available_tools()  # Your MCP server tools
response = call_groq_with_smart_tools(user_query, all_tools)
'''

    print("🔧 TYPINGMIND INTEGRATION CODE")
    print("=" * 50)
    print(integration_code)

if __name__ == "__main__":
    test_smart_selection()
    print("\n" + "=" * 60)
    create_typingmind_integration()
