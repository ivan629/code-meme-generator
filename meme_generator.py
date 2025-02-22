#!/usr/bin/env python3

"""
Code Quality Meme Generator Pre-commit Hook

This hook analyzes your code changes, judges how "shitty" they are,
and generates a relevant meme to celebrate or shame your work.
"""

import os
import sys
import subprocess
import random
import re
import json
import tempfile
import webbrowser
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configure your terminal colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"

# Meme templates for different code quality levels
MEME_TEMPLATES = {
    "terrible": [
        {"text": "THEY SAID WRITE CODE\nI WROTE A CRIME SCENE", "image": "disaster-girl.jpg"},
        {"text": "YOUR CODE\nMY EYES", "image": "my-eyes-spongebob.jpg"},
        {"text": "DOESN'T TEST CODE\nHOPES FOR THE BEST", "image": "bad-luck-brian.jpg"},
        {"text": "CODE SO BAD\nEVEN STACKOVERFLOW CAN'T HELP", "image": "disappointed-kid.jpg"},
    ],
    "bad": [
        {"text": "COMMITS CODE\nCOMMENTS OUT TESTS", "image": "evil-kermit.jpg"},
        {"text": "THAT MOMENT WHEN\nYOUR VARIABLE NAMES ARE JUST ALPHABET", "image": "confused-jackie.jpg"},
        {"text": "DEPLOYS TO PRODUCTION\nON FRIDAY AT 5PM", "image": "i-too-like-to-live-dangerously.jpg"},
        {"text": "NOT SURE IF BAD CODE\nOR I'M TOO TIRED TO SEE IT", "image": "futurama-fry.jpg"},
    ],
    "mediocre": [
        {"text": "MAKES MINOR CHANGE\nREWRITES ENTIRE FILE", "image": "philosoraptor.jpg"},
        {"text": "IT'S NOT STUPID\nIF IT WORKS", "image": "roll-safe.jpg"},
        {"text": "CODE LOOKS WRONG\nRUNS ANYWAY", "image": "skeptical-third-world-kid.jpg"},
        {"text": "WRITES DOCUMENTATION\nTHAT'S ALREADY OUTDATED", "image": "ancient-aliens-guy.jpg"},
    ],
    "good": [
        {"text": "WRITES CLEAN CODE\nDOESN'T BRAG ABOUT IT", "image": "good-guy-greg.jpg"},
        {"text": "CODE REVIEW?\nZERO COMMENTS", "image": "success-kid.jpg"},
        {"text": "ONE DOES NOT SIMPLY\nWRITE PERFECT CODE THE FIRST TIME", "image": "one-does-not-simply.jpg"},
        {"text": "THAT FEELING WHEN\nTHE TESTS PASS ON FIRST TRY", "image": "surprised-pikachu.jpg"},
    ],
    "excellent": [
        {"text": "LOOKS AT YOUR CODE\nSHEDS TEAR OF JOY", "image": "proud-mom.jpg"},
        {"text": "YOUR CODE\nIT'S BEAUTIFUL", "image": "so-beautiful.jpg"},
        {"text": "INHERITANCE DEPTH: 1\nCYCLOMATIC COMPLEXITY: LOW", "image": "drake-approves.jpg"},
        {"text": "THEY SAID IT COULDN'T BE DONE\nHOLD MY KEYBOARD", "image": "challenge-accepted.jpg"},
    ]
}

# ASCII art templates for terminal output when images aren't available
ASCII_TEMPLATES = {
    "terrible": """
    ┌─────────────────────────────┐
    │                             │
    │     (╯°□°)╯︵ ┻━┻           │
    │                             │
    │   YOUR CODE IS TERRIBLE     │
    │                             │
    └─────────────────────────────┘
    """,
    "bad": """
    ┌─────────────────────────────┐
    │                             │
    │       ಠ_ಠ                   │
    │                             │
    │     YOUR CODE NEEDS WORK    │
    │                             │
    └─────────────────────────────┘
    """,
    "mediocre": """
    ┌─────────────────────────────┐
    │                             │
    │       ¯\\_(ツ)_/¯            │
    │                             │
    │    YOUR CODE IS MEDIOCRE    │
    │                             │
    └─────────────────────────────┘
    """,
    "good": """
    ┌─────────────────────────────┐
    │                             │
    │         (•‿•)               │
    │                             │
    │    YOUR CODE LOOKS GOOD!    │
    │                             │
    └─────────────────────────────┘
    """,
    "excellent": """
    ┌─────────────────────────────┐
    │                             │
    │      ヾ(⌐■_■)ノ♪            │
    │                             │
    │   YOUR CODE IS EXCELLENT!   │
    │                             │
    └─────────────────────────────┘
    """
}


def get_staged_files() -> List[str]:
    """Get list of staged files that are being committed."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True, text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f]


def get_file_content(filename: str) -> str:
    """Get the staged content of a file."""
    result = subprocess.run(
        ["git", "show", f":0:{filename}"],
        capture_output=True, text=True
    )
    return result.stdout


def get_diff_stats() -> Tuple[int, int]:
    """Get the number of lines added and removed in this commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True, text=True
    )
    
    # Parse the summary line like "10 files changed, 200 insertions(+), 150 deletions(-)"
    summary = result.stdout.strip().split("\n")[-1]
    
    # Extract numbers
    insertions = re.search(r"(\d+) insertion", summary)
    deletions = re.search(r"(\d+) deletion", summary)
    
    return (
        int(insertions.group(1)) if insertions else 0,
        int(deletions.group(1)) if deletions else 0
    )


def analyze_code_quality(files: List[str]) -> Dict:
    """Analyze code quality of the staged files."""
    total_score = 0
    max_possible_score = 0
    issues = []
    
    # Get basic stats
    lines_added, lines_removed = get_diff_stats()
    
    # Analyze individual files
    for file_path in files:
        # Skip non-code files
        if not any(file_path.endswith(ext) for ext in [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".go", ".rb", ".php", ".cs"
        ]):
            continue
            
        content = get_file_content(file_path)
        
        # Basic metrics that indicate potentially shitty code
        metrics = {
            "long_lines": sum(1 for line in content.split("\n") if len(line.strip()) > 100),
            "todo_comments": len(re.findall(r"TODO|FIXME", content, re.IGNORECASE)),
            "commented_code": len(re.findall(r"^\s*//.*;\s*$|^\s*#.*\s*$", content, re.MULTILINE)),
            "magic_numbers": len(re.findall(r"(?<!\w)[-+]?[0-9]+(?:\.[0-9]+)?(?![0-9_\.])(?!\w)", content)),
            "empty_catch": len(re.findall(r"catch\s*\([^)]*\)\s*{?\s*}?", content)),
            "nested_conditionals": len(re.findall(r"if.*?{.*?if.*?{", content, re.DOTALL)),
            "long_functions": 0
        }
        
        # Count long functions (very basic approximation)
        function_matches = re.finditer(r"(def|function|public|private|protected)\s+\w+\s*\([^)]*\)[^{]*{", content)
        for match in function_matches:
            # Find the matching closing brace (this is a simplification)
            start_pos = match.end()
            brace_count = 1
            pos = start_pos
            while pos < len(content) and brace_count > 0:
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if pos - start_pos > 50:  # More than ~50 characters indicates a long function
                metrics["long_functions"] += 1
        
        # Calculate file score (lower is worse)
        file_score = 100
        file_score -= metrics["long_lines"] * 2
        file_score -= metrics["todo_comments"] * 5
        file_score -= metrics["commented_code"] * 3
        file_score -= metrics["magic_numbers"] * 1
        file_score -= metrics["empty_catch"] * 10
        file_score -= metrics["nested_conditionals"] * 5
        file_score -= metrics["long_functions"] * 8
        
        # Add issues found
        if metrics["long_lines"] > 0:
            issues.append(f"{file_path} has {metrics['long_lines']} excessively long lines")
        if metrics["todo_comments"] > 0:
            issues.append(f"{file_path} contains {metrics['todo_comments']} TODO/FIXME comments")
        if metrics["empty_catch"] > 0:
            issues.append(f"{file_path} has {metrics['empty_catch']} empty catch blocks")
        if metrics["nested_conditionals"] > 0:
            issues.append(f"{file_path} has {metrics['nested_conditionals']} nested conditionals")
        if metrics["long_functions"] > 0:
            issues.append(f"{file_path} has {metrics['long_functions']} excessively long functions")
        
        total_score += max(0, file_score)
        max_possible_score += 100
    
    # Adjust if no scorable files
    if max_possible_score == 0:
        max_possible_score = 100
        total_score = 75  # Default to "good" if no code files to assess
    
    # Calculate overall percentage
    percentage = total_score / max_possible_score * 100
    
    # Determine quality level
    if percentage < 20:
        quality = "terrible"
    elif percentage < 40:
        quality = "bad"
    elif percentage < 60:
        quality = "mediocre"
    elif percentage < 80:
        quality = "good"
    else:
        quality = "excellent"
    
    return {
        "score": percentage,
        "quality": quality,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "issues": issues[:5]  # Limit to top 5 issues
    }


def generate_meme(quality: str) -> str:
    """Generate a meme URL or ASCII art for the given quality level."""
    # Pick a random meme template for this quality level
    template = random.choice(MEME_TEMPLATES[quality])
    
    # In a real implementation, you'd call a meme generation API or use a library
    # For this example, we'll just construct an URL to an imaginary service
    meme_text = template["text"].replace(" ", "%20")
    meme_image = template["image"]
    
    # Return an ASCII meme for terminal and a URL for potential browser opening
    return {
        "ascii": ASCII_TEMPLATES[quality],
        "url": f"https://api.memegen.link/images/{meme_image}/{meme_text}.jpg",
        "text": template["text"].replace("\n", " - ")
    }


def display_results(analysis: Dict, meme: Dict):
    """Display the analysis results and meme in the terminal."""
    quality = analysis["quality"]
    color = {
        "terrible": Colors.RED,
        "bad": Colors.RED,
        "mediocre": Colors.YELLOW,
        "good": Colors.GREEN,
        "excellent": Colors.PURPLE
    }.get(quality, Colors.RESET)
    
    # Print header
    print("\n" + "=" * 60)
    print(f"{color}CODE QUALITY MEME GENERATOR{Colors.RESET}")
    print("=" * 60)
    
    # Print the meme
    print(f"{color}{meme['ascii']}{Colors.RESET}")
    
    # Print analysis
    print(f"Quality score: {color}{analysis['score']:.1f}%{Colors.RESET}")
    print(f"Changes: +{analysis['lines_added']} lines, -{analysis['lines_removed']} lines")
    
    # Print issues if any
    if analysis["issues"]:
        print("\nTop issues:")
        for issue in analysis["issues"]:
            print(f"  - {issue}")
    
    # Meme info
    print(f"\nMeme text: {color}{meme['text']}{Colors.RESET}")
    print(f"Meme URL: {meme['url']}")
    
    # Ask if user wants to view the meme
    try:
        print("\nWant to see this as a real meme? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            webbrowser.open(meme['url'])
    except:
        # If we're in a non-interactive environment, just continue
        pass
    
    print("\n" + "=" * 60)
    
    # Save to meme history
    save_to_history(analysis, meme)


def save_to_history(analysis: Dict, meme: Dict):
    """Save meme to a history file for fun tracking over time."""
    history_path = os.path.join(os.path.expanduser("~"), ".code_meme_history.json")
    
    # Create entry
    entry = {
        "date": datetime.now().isoformat(),
        "score": analysis["score"],
        "quality": analysis["quality"],
        "meme_text": meme["text"],
        "meme_url": meme["url"],
        "lines_added": analysis["lines_added"],
        "lines_removed": analysis["lines_removed"]
    }
    
    # Load existing history or create new
    try:
        with open(history_path, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    # Add new entry and save
    history.append(entry)
    try:
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)
    except:
        # Ignore errors, history saving is not critical
        pass


def main():
    # Get staged files
    staged_files = get_staged_files()
    if not staged_files:
        print("No files staged. Commit will proceed without a meme :-(")
        return 0
    
    # Analyze code quality
    analysis = analyze_code_quality(staged_files)
    
    # Generate a meme
    meme = generate_meme(analysis["quality"])
    
    # Display results
    display_results(analysis, meme)
    
    # Always allow the commit to proceed - this is just for fun
    print("Commit will proceed regardless of code quality.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
