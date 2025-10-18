#!/usr/bin/env python3
"""
Groq API Tool Manager - Solves 128 Tool Limit
Implements dynamic tool selection based on query context
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ToolCategory:
    """Tool category with priority and keywords"""
    name: str
    tools: List[Dict[str, Any]]
    keywords: List[str]
    priority: int = 1

class GroqToolManager:
    """Manages tool selection for Groq API to stay under 128 limit"""

    def __init__(self):
        self.tool_categories = {}
        self.core_tools = []
        self.max_tools = 128

    def add_category(self, category: ToolCategory):
        """Add a tool category"""
        self.tool_categories[category.name] = category

    def add_core_tools(self, tools: List[Dict[str, Any]]):
        """Add core tools that are always included"""
        self.core_tools.extend(tools)

    def select_tools_for_query(self, user_query: str, max_tools: int = None) -> List[Dict[str, Any]]:
        """Select relevant tools based on query content"""
        if max_tools is None:
            max_tools = self.max_tools

        selected_tools = []
        query_lower = user_query.lower()

        # Always include core tools first
        selected_tools.extend(self.core_tools)

        # Score each category based on keyword matches
        category_scores = {}
        for cat_name, category in self.tool_categories.items():
            score = 0
            for keyword in category.keywords:
                if keyword.lower() in query_lower:
                    score += 1
            category_scores[cat_name] = score

        # Sort categories by score (highest first)
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: (x[1], self.tool_categories[x[0]].priority),
            reverse=True
        )

        # Add tools from highest scoring categories
        for cat_name, score in sorted_categories:
            if score > 0:  # Only include categories with matches
                category = self.tool_categories[cat_name]
                for tool in category.tools:
                    if len(selected_tools) >= max_tools:
                        break
                    if tool not in selected_tools:  # Avoid duplicates
                        selected_tools.append(tool)

        # Safety check: never exceed limit
        if len(selected_tools) > max_tools:
            selected_tools = selected_tools[:max_tools]

        return selected_tools

    def analyze_tool_usage(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze current tool set for optimization"""
        analysis = {
            "total_tools": len(tools),
            "exceeds_limit": len(tools) > self.max_tools,
            "overage": max(0, len(tools) - self.max_tools),
            "tool_names": [tool.get('name', tool.get('function', {}).get('name', 'unnamed')) for tool in tools],
            "duplicates": self._find_duplicates(tools),
            "recommendations": []
        }

        if analysis["exceeds_limit"]:
            analysis["recommendations"].append(f"Remove {analysis['overage']} tools to stay under {self.max_tools} limit")

        if analysis["duplicates"]:
            analysis["recommendations"].append(f"Remove {len(analysis['duplicates'])} duplicate tools")

        return analysis

    def _find_duplicates(self, tools: List[Dict[str, Any]]) -> List[str]:
        """Find duplicate tool names"""
        seen_names = set()
        duplicates = []

        for tool in tools:
            name = tool.get('name', tool.get('function', {}).get('name', ''))
            if name in seen_names:
                duplicates.append(name)
            else:
                seen_names.add(name)

        return duplicates

# Example usage and setup
def setup_example_tool_manager():
    """Example setup for common tool categories"""
    manager = GroqToolManager()

    # Core tools (always included)
    core_tools = [
        {"name": "get_current_time", "type": "function"},
        {"name": "get_user_info", "type": "function"},
        {"name": "log_interaction", "type": "function"}
    ]
    manager.add_core_tools(core_tools)

    # Data processing tools
    data_tools = [
        {"name": "process_csv", "type": "function"},
        {"name": "analyze_data", "type": "function"},
        {"name": "export_json", "type": "function"}
    ]
    manager.add_category(ToolCategory(
        name="data_processing",
        tools=data_tools,
        keywords=["data", "csv", "analyze", "process", "export", "json"],
        priority=2
    ))

    # Web search tools
    search_tools = [
        {"name": "web_search", "type": "function"},
        {"name": "image_search", "type": "function"},
        {"name": "news_search", "type": "function"}
    ]
    manager.add_category(ToolCategory(
        name="web_search",
        tools=search_tools,
        keywords=["search", "find", "lookup", "google", "web", "internet"],
        priority=3
    ))

    # Database tools
    db_tools = [
        {"name": "query_database", "type": "function"},
        {"name": "update_record", "type": "function"},
        {"name": "create_table", "type": "function"}
    ]
    manager.add_category(ToolCategory(
        name="database",
        tools=db_tools,
        keywords=["database", "query", "sql", "table", "record", "db"],
        priority=2
    ))

    return manager

def test_tool_selection():
    """Test the tool selection with example queries"""
    manager = setup_example_tool_manager()

    test_queries = [
        "Search for information about machine learning",
        "Process this CSV file and export to JSON",
        "Query the database for user records",
        "What time is it and who am I?",
        "Help me with everything"  # This should trigger most tools
    ]

    print("🧪 Testing Dynamic Tool Selection")
    print("=" * 50)

    for query in test_queries:
        selected_tools = manager.select_tools_for_query(query)
        print(f"\nQuery: '{query}'")
        print(f"Selected {len(selected_tools)} tools:")
        for tool in selected_tools:
            name = tool.get('name', 'unnamed')
            print(f"  - {name}")

    # Test with a large tool set
    print(f"\n🔍 Testing with large tool set...")
    large_tool_set = [{"name": f"tool_{i}", "type": "function"} for i in range(200)]
    analysis = manager.analyze_tool_usage(large_tool_set)

    print(f"Total tools: {analysis['total_tools']}")
    print(f"Exceeds limit: {analysis['exceeds_limit']}")
    if analysis['exceeds_limit']:
        print(f"Overage: {analysis['overage']} tools")
    print(f"Duplicates found: {len(analysis['duplicates'])}")
    print(f"Recommendations: {analysis['recommendations']}")

if __name__ == "__main__":
    test_tool_selection()
