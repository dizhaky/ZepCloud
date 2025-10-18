#!/usr/bin/env python3
"""
Quick Groq Tool Limit Diagnostic
Run this to check your current tool count and get immediate fixes
"""

def diagnose_your_tools():
    """Diagnose your current tool situation"""
    print("🔍 GROQ TOOL LIMIT DIAGNOSTIC")
    print("=" * 50)

    # Replace this with your actual tools list
    # tools = your_actual_tools_list

    # For demonstration, let's simulate a problematic scenario
    tools = [{"name": f"tool_{i}", "type": "function"} for i in range(150)]  # 150 tools = over limit

    print(f"📊 Current tool count: {len(tools)}")
    print(f"🚨 Groq limit: 128 tools")

    if len(tools) > 128:
        overage = len(tools) - 128
        print(f"❌ PROBLEM: You're {overage} tools over the limit!")
        print(f"🔧 SOLUTION: Need to remove {overage} tools")

        # Quick fixes
        print(f"\n🚀 IMMEDIATE FIXES:")
        print(f"1. Remove unused tools (quickest)")
        print(f"2. Use dynamic tool selection (best)")
        print(f"3. Split into multiple API calls")

        # Show which tools to remove
        print(f"\n✂️  TOOLS TO REMOVE (first {overage}):")
        for i in range(overage):
            tool_name = tools[i].get('name', f'tool_{i}')
            print(f"   - {tool_name}")

    else:
        print("✅ GOOD: You're within the 128 tool limit")

    return len(tools)

def quick_fix_implementation():
    """Show how to implement the quick fix"""
    print(f"\n🔧 QUICK FIX IMPLEMENTATION")
    print("=" * 50)

    # Your original tools (replace with actual)
    original_tools = [{"name": f"tool_{i}", "type": "function"} for i in range(150)]

    print(f"Original tools: {len(original_tools)}")

    # Fix 1: Remove unused tools
    unused_keywords = ['test_', 'debug_', 'temp_', 'old_', 'unused_']
    filtered_tools = []

    for tool in original_tools:
        name = tool.get('name', '')
        is_unused = any(keyword in name.lower() for keyword in unused_keywords)

        if not is_unused and len(filtered_tools) < 128:
            filtered_tools.append(tool)

    print(f"After filtering: {len(filtered_tools)} tools")

    if len(filtered_tools) <= 128:
        print("✅ SUCCESS: Now under 128 tool limit!")
        return filtered_tools
    else:
        # Fix 2: Take only first 128 tools
        limited_tools = filtered_tools[:128]
        print(f"✅ SUCCESS: Limited to {len(limited_tools)} tools")
        return limited_tools

def groq_api_call_example():
    """Show how to use the fixed tools with Groq"""
    print(f"\n🚀 GROQ API CALL EXAMPLE")
    print("=" * 50)

    # Get your fixed tools
    fixed_tools = quick_fix_implementation()

    # Example Groq API call
    api_call_code = f"""
# Your fixed Groq API call
import groq

client = groq.Groq(api_key="your-api-key")

response = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[{{"role": "user", "content": "Your query here"}}],
    tools={fixed_tools},  # ← Now under 128 tools!
    max_completion_tokens=4096
)

print("✅ API call successful!")
"""

    print("Python code for your Groq API call:")
    print(api_call_code)

if __name__ == "__main__":
    # Run the diagnostic
    tool_count = diagnose_your_tools()

    if tool_count > 128:
        # Show the fix
        quick_fix_implementation()
        groq_api_call_example()

        print(f"\n🎉 SUMMARY:")
        print(f"✅ Problem identified: {tool_count} tools exceeds 128 limit")
        print(f"✅ Solution provided: Reduce to 128 tools")
        print(f"✅ Code ready: Use the fixed tools in your Groq API call")
    else:
        print(f"\n✅ No problem detected - you're within limits!")
