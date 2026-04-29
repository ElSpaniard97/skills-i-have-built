#!/usr/bin/env python3
"""
Measure system prompt token savings from category filtering.
Simulates the skills section with and without filters.
"""
import sys
import subprocess
import json

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken (cl100k_base for Claude/GPT-4)"""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback: rough estimate (1 token ≈ 4 chars)
        return len(text) // 4

def get_skills_list(category_filter=None) -> str:
    """Get skills list output with optional category filter"""
    cmd = ["hermes", "skills", "list", "--format=json"]
    if category_filter:
        cmd.extend(["--category", ",".join(category_filter)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            return ""
    except Exception as e:
        print(f"Error running skills list: {e}", file=sys.stderr)
        return ""

def main():
    print("# System Prompt Token Savings Analysis\n")
    
    # Baseline: no filter (all skills)
    print("Measuring baseline (no filter)...")
    baseline_output = get_skills_list()
    baseline_tokens = count_tokens(baseline_output)
    
    # Current filter from config
    current_filter = [
        "autonomous-ai-agents",
        "github", 
        "software-development",
        "devops",
        "reporting",
        "discord",
        "security",
        "note-taking",
        "productivity",
        "media",
        "research"
    ]
    
    print(f"Measuring with current filter ({len(current_filter)} categories)...")
    filtered_output = get_skills_list(current_filter)
    filtered_tokens = count_tokens(filtered_output)
    
    # Calculate savings
    tokens_saved = baseline_tokens - filtered_tokens
    percent_saved = (tokens_saved / baseline_tokens * 100) if baseline_tokens > 0 else 0
    
    print(f"\n## Results")
    print(f"- **Baseline** (all skills): {baseline_tokens:,} tokens")
    print(f"- **Filtered** ({len(current_filter)} categories): {filtered_tokens:,} tokens")
    print(f"- **Saved**: {tokens_saved:,} tokens ({percent_saved:.1f}% reduction)")
    
    # Cost impact calculation
    # Assume this reduction applies to cache reads only
    # Opus cache reads: $1.50/M tokens
    # Sonnet cache reads: $0.30/M tokens
    
    print(f"\n## Cost Impact per 1,000 cached turns")
    opus_savings = (tokens_saved * 1000 / 1_000_000) * 1.50
    sonnet_savings = (tokens_saved * 1000 / 1_000_000) * 0.30
    print(f"- Opus (cache read @ $1.50/M): **${opus_savings:.2f}** saved")
    print(f"- Sonnet (cache read @ $0.30/M): **${sonnet_savings:.2f}** saved")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
