#!/usr/bin/env python3
"""
Quick Fix for Groq 128 Tool Limit Error
Implements immediate solutions for your specific case
"""

def diagnose_tool_problem(tools):
    """Step 1: Diagnose your current tool situation"""
    print("🔍 DIAGNOSING TOOL PROBLEM")
    print("=" * 40)

    total_tools = len(tools)
    print(f"Number of tools: {total_tools}")
    print(f"Error will occur if: {total_tools} > 128")

    if total_tools > 128:
        overage = total_tools - 128
        print(f"⚠️  WARNING: Exceeding limit by {overage} tools!")
        print(f"Need to remove {overage} tools to fix this")
    else:
        print("✅ Tool count is within limits")

    # List all tool names
    print(f"\n📋 All {total_tools} tool names:")
    for i, tool in enumerate(tools, 1):
        name = tool.get('name', tool.get('function', {}).get('name', f'unnamed_{i}'))
        print(f"  {i:3d}. {name}")

    return total_tools

def quick_fix_remove_unused(tools, max_tools=128):
    """Solution 1: Remove unused tools (5 min fix)"""
    print(f"\n✂️  QUICK FIX: Remove unused tools")
    print("=" * 40)

    # Common unused tool patterns
    unused_patterns = [
        'test_', 'debug_', 'temp_', 'old_', 'deprecated_',
        'unused_', 'backup_', 'legacy_', 'experimental_'
    ]

    filtered_tools = []
    removed_count = 0

    for tool in tools:
        name = tool.get('name', tool.get('function', {}).get('name', ''))

        # Check if tool matches unused patterns
        is_unused = any(pattern in name.lower() for pattern in unused_patterns)

        if not is_unused and len(filtered_tools) < max_tools:
            filtered_tools.append(tool)
        else:
            removed_count += 1
            print(f"  Removed: {name}")

    print(f"\n✅ Removed {removed_count} unused tools")
    print(f"Remaining: {len(filtered_tools)} tools")

    return filtered_tools

def smart_tool_selection(tools, user_query, max_tools=128):
    """Solution 3: Dynamic tool selection based on query"""
    print(f"\n🎯 SMART TOOL SELECTION")
    print("=" * 40)

    # Define tool categories and keywords
    categories = {
        'search': ['search', 'find', 'lookup', 'google', 'web', 'internet'],
        'data': ['data', 'csv', 'json', 'analyze', 'process', 'export'],
        'database': ['database', 'query', 'sql', 'table', 'record', 'db'],
        'email': ['email', 'send', 'mail', 'message', 'notification'],
        'calculation': ['calculate', 'math', 'compute', 'number', 'formula'],
        'file': ['file', 'document', 'upload', 'download', 'save'],
        'time': ['time', 'date', 'schedule', 'calendar', 'reminder']
    }

    selected_tools = []
    query_lower = user_query.lower()

    # Score each tool based on query relevance
    tool_scores = []
    for tool in tools:
        name = tool.get('name', tool.get('function', {}).get('name', ''))
        score = 0

        # Check against all categories
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in query_lower and keyword in name.lower():
                    score += 1

        tool_scores.append((tool, score))

    # Sort by score (highest first) and select top tools
    tool_scores.sort(key=lambda x: x[1], reverse=True)

    for tool, score in tool_scores:
        if len(selected_tools) < max_tools:
            selected_tools.append(tool)
        else:
            break

    print(f"Query: '{user_query}'")
    print(f"Selected {len(selected_tools)} most relevant tools")

    return selected_tools

def batch_tools(tools, batch_size=128):
    """Solution 4: Split tools into batches"""
    print(f"\n📦 TOOL BATCHING")
    print("=" * 40)

    batches = []
    for i in range(0, len(tools), batch_size):
        batch = tools[i:i + batch_size]
        batches.append(batch)
        print(f"Batch {len(batches)}: {len(batch)} tools")

    return batches

def implement_groq_fix(tools, user_query=None):
    """Main function to implement the Groq fix"""
    print("🚀 GROQ TOOL LIMIT FIX")
    print("=" * 50)

    # Step 1: Diagnose
    total_tools = diagnose_tool_problem(tools)

    if total_tools <= 128:
        print("\n✅ No fix needed - you're under the limit!")
        return tools

    # Step 2: Choose solution based on situation
    if total_tools <= 150:
        print("\n🔧 RECOMMENDED: Quick fix (remove unused tools)")
        fixed_tools = quick_fix_remove_unused(tools)
    elif user_query:
        print("\n🔧 RECOMMENDED: Smart tool selection")
        fixed_tools = smart_tool_selection(tools, user_query)
    else:
        print("\n🔧 RECOMMENDED: Tool batching")
        batches = batch_tools(tools)
        print(f"Split into {len(batches)} batches")
        return batches[0]  # Return first batch

    # Step 3: Verify fix
    print(f"\n✅ FINAL RESULT:")
    print(f"Original tools: {total_tools}")
    print(f"Fixed tools: {len(fixed_tools)}")
    print(f"Under limit: {len(fixed_tools) <= 128}")

    return fixed_tools

# Example usage
if __name__ == "__main__":
    # Example: You have 200 tools and get the error
    example_tools = [{"name": f"tool_{i}", "type": "function"} for i in range(200)]
    example_query = "Search for information about machine learning"

    # Fix the problem
    fixed_tools = implement_groq_fix(example_tools, example_query)

    print(f"\n🎉 SUCCESS: You can now send {len(fixed_tools)} tools to Groq!")
