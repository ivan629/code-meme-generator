#!/usr/bin/env python3

"""
Shocking & Stylish Code Quality Meme Generator Pre-commit Hook

This hook analyzes your code changes, judges how "shitty" they are,
and generates a stylish and shocking meme to celebrate or shame your work.
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

# Configure your terminal colors with more vibrant options
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE_BG = "\033[107m"
    BLACK_TEXT = "\033[30m"

# Enhanced meme templates with more shocking, cool, and stylish content
MEME_TEMPLATES = {
    "terrible": [
        {"text": "HOLY $#!T\nWHAT DID YOU DO TO THIS CODE", "image": "disaster-girl.jpg"},
        {"text": "YOUR CODE\nMY RETINAS ARE BURNING", "image": "my-eyes-spongebob.jpg"},
        {"text": "PUSHED TO PRODUCTION\nWITHOUT TESTING", "image": "joker-chaos.jpg"},
        {"text": "CODE SO BRUTAL\nIT VIOLATES GENEVA CONVENTION", "image": "shocked-pikachu.jpg"},
    ],
    "bad": [
        {"text": "MERGED THIS CODE\nBLAMED THE INTERN", "image": "evil-kermit.jpg"},
        {"text": "VARIABLE NAMES\nJUST KEYSMASHED THE KEYBOARD", "image": "confused-math-lady.jpg"},
        {"text": "DEPLOYS FRIDAY 5PM\nTURNS OFF SLACK NOTIFICATIONS", "image": "i-too-like-to-live-dangerously.jpg"},
        {"text": "WROTE THIS AT 3AM\nSHIPPED IT ANYWAY", "image": "futurama-fry.jpg"},
    ],
    "mediocre": [
        {"text": "FIXED ONE BUG\nCREATED THREE MORE", "image": "philosoraptor.jpg"},
        {"text": "THIS CODE IS LIKE TEQUILA\nIT WORKS BUT HURTS TOMORROW", "image": "roll-safe.jpg"},
        {"text": "LOOKS WRONG\nWORKS FOR MYSTERIOUS REASONS", "image": "confused-travolta.jpg"},
        {"text": "COPY-PASTED FROM STACKOVERFLOW\nDIDN'T READ THE COMMENTS", "image": "ancient-aliens-guy.jpg"},
    ],
    "good": [
        {"text": "CODE SO CLEAN\nCOULD EAT OFF IT", "image": "good-guy-greg.jpg"},
        {"text": "PR APPROVED\nWITHOUT A SINGLE COMMENT", "image": "success-kid.jpg"},
        {"text": "REFACTORED THE LEGACY CODE\nDIDN'T START A FIRE", "image": "the-most-interesting-man.jpg"},
        {"text": "TESTS PASSED FIRST TRY\nMAKES IT RAIN", "image": "leo-cheers.jpg"},
    ],
    "excellent": [
        {"text": "YOUR CODE\nBELONGS IN A MUSEUM", "image": "keanu-breathtaking.jpg"},
        {"text": "SENIOR DEVS\nASK YOU FOR CODE REVIEWS", "image": "so-beautiful.jpg"},
        {"text": "YOUR COMMIT\nMADE THE REPO MORE VALUABLE THAN BITCOIN", "image": "drake-approves.jpg"},
        {"text": "CODE SO ELEGANT\nCOULD MAKE A GROWN DEV CRY", "image": "challenge-accepted.jpg"},
    ]
}

# Enhanced ASCII art templates with more style and impact
ASCII_TEMPLATES = {
    "terrible": """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      (╯°□°)╯︵ ┻━┻  ┻━┻ ︵ヽ(`Д´)ﾉ︵┻━┻   ║
    ║                                          ║
    ║         CATASTROPHIC CODE ALERT!         ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """,
    "bad": """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      (ಠ_ಠ)  ಠ╭╮ಠ  ಠ_ಠ                    ║
    ║                                          ║
    ║       THIS CODE IS DEEPLY DISTURBING     ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """,
    "mediocre": """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║       ¯\\_(ツ)_/¯  ¯\\(°_o)/¯              ║
    ║                                          ║
    ║        YOUR CODE IS... WHATEVER          ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """,
    "good": """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      (•̀ᴗ•́)و ̑̑   ✧*｡٩(ˊᗜˋ*)و✧*｡          ║
    ║                                          ║
    ║         YOUR CODE IS IMPRESSIVE!         ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """,
    "excellent": """
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      ( •_•)                              ║
    ║      ( •_•)>⌐■-■                         ║
    ║      (⌐■_■)  YEAAAAAAAAH!                ║
    ║                                          ║
    ║       YOUR CODE IS LEGENDARY!            ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
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
    """Analyze code quality of the staged files - now with more brutal honesty."""
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
        
        # Enhanced metrics with more brutal and specific checks
        metrics = {
            "long_lines": sum(1 for line in content.split("\n") if len(line.strip()) > 100),
            "todo_comments": len(re.findall(r"TODO|FIXME", content, re.IGNORECASE)),
            "commented_code": len(re.findall(r"^\s*//.*;\s*$|^\s*#.*\s*$", content, re.MULTILINE)),
            "magic_numbers": len(re.findall(r"(?<!\w)[-+]?[0-9]+(?:\.[0-9]+)?(?![0-9_\.])(?!\w)", content)),
            "empty_catch": len(re.findall(r"catch\s*\([^)]*\)\s*{?\s*}?", content)),
            "nested_conditionals": len(re.findall(r"if.*?{.*?if.*?{", content, re.DOTALL)),
            "long_functions": 0,
            "inconsistent_spacing": len(re.findall(r"\)\s{2,}{|\)\{", content)),  # Check for weird spacing
            "console_log": len(re.findall(r"console\.log", content)),  # Debug statements left in
            "force_push_comments": len(re.findall(r"force|FORCE|yolo|YOLO", content, re.IGNORECASE))  # Signs of desperation
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
        
        # Calculate file score with enhanced penalties (lower is worse)
        file_score = 100
        file_score -= metrics["long_lines"] * 2
        file_score -= metrics["todo_comments"] * 5
        file_score -= metrics["commented_code"] * 3
        file_score -= metrics["magic_numbers"] * 1
        file_score -= metrics["empty_catch"] * 10
        file_score -= metrics["nested_conditionals"] * 5
        file_score -= metrics["long_functions"] * 8
        file_score -= metrics["inconsistent_spacing"] * 3
        file_score -= metrics["console_log"] * 4
        file_score -= metrics["force_push_comments"] * 15  # Severe penalty for YOLO comments
        
        # Add more colorful and brutal issue descriptions
        if metrics["long_lines"] > 0:
            issues.append(f"📏 {file_path} has {metrics['long_lines']} lines longer than a CVS receipt")
        if metrics["todo_comments"] > 0:
            issues.append(f"⏰ {file_path} contains {metrics['todo_comments']} TODOs that will never be done")
        if metrics["empty_catch"] > 0:
            issues.append(f"🕳️ {file_path} swallows {metrics['empty_catch']} exceptions like they're candy")
        if metrics["nested_conditionals"] > 0:
            issues.append(f"🪆 {file_path} has {metrics['nested_conditionals']} nested conditionals (inception level: terrifying)")
        if metrics["long_functions"] > 0:
            issues.append(f"📜 {file_path} has {metrics['long_functions']} functions longer than War and Peace")
        if metrics["console_log"] > 0:
            issues.append(f"👀 {file_path} leaks {metrics['console_log']} debug logs to production")
        if metrics["force_push_comments"] > 0:
            issues.append(f"💥 {file_path} has {metrics['force_push_comments']} YOLO comments indicating desperation")
        
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


def generate_meme(quality: str) -> Dict:
    """Generate a meme URL or ASCII art for the given quality level."""
    # Pick a random meme template for this quality level
    template = random.choice(MEME_TEMPLATES[quality])
    
    # In a real implementation, you'd call a meme generation API or use a library
    # For this example, we'll use memegen.link which is a real meme API
    top_text, bottom_text = template["text"].split("\n") if "\n" in template["text"] else (template["text"], "")
    
    # Clean and format the text
    top_text = top_text.replace(" ", "_")
    bottom_text = bottom_text.replace(" ", "_")
    
    # Format the image name for the API
    image_name = template["image"].replace(".jpg", "").replace("-", "~")
    
    # Return an ASCII meme for terminal and a URL for potential browser opening
    return {
        "ascii": ASCII_TEMPLATES[quality],
        "url": f"https://api.memegen.link/images/{image_name}/{top_text}/{bottom_text}.jpg",
        "text": template["text"].replace("\n", " - ")
    }


def display_results(analysis: Dict, meme: Dict):
    """Display the analysis results and meme in the terminal with enhanced styling."""
    quality = analysis["quality"]
    color = {
        "terrible": Colors.RED,
        "bad": Colors.RED,
        "mediocre": Colors.YELLOW,
        "good": Colors.GREEN,
        "excellent": Colors.PURPLE
    }.get(quality, Colors.RESET)
    
    # Print fancy header
    print("\n" + "═" * 70)
    print(f"{color}╔{'═' * 68}╗{Colors.RESET}")
    print(f"{color}║{Colors.WHITE_BG}{Colors.BLACK_TEXT}           💥  CODE QUALITY MEME GENERATOR  💥           {Colors.RESET}{color}║{Colors.RESET}")
    print(f"{color}╚{'═' * 68}╝{Colors.RESET}")
    
    # Print the meme with fancy border
    print(f"{color}{meme['ascii']}{Colors.RESET}")
    
    # Print analysis with enhanced formatting
    print(f"{Colors.CYAN}▓▒░ Quality score: {color}{analysis['score']:.1f}%{Colors.RESET} {Colors.CYAN}░▒▓{Colors.RESET}")
    print(f"{Colors.CYAN}▓▒░ Changes: +{analysis['lines_added']} lines, -{analysis['lines_removed']} lines {Colors.CYAN}░▒▓{Colors.RESET}")
    
    # Print issues if any - with emoji and color
    if analysis["issues"]:
        print(f"\n{Colors.YELLOW}🔍 TOP ISSUES:{Colors.RESET}")
        for issue in analysis["issues"]:
            print(f"  {Colors.RED}•{Colors.RESET} {issue}")
    
    # Meme info
    print(f"\n{Colors.PURPLE}🖼️ Meme text: {color}{meme['text']}{Colors.RESET}")
    print(f"{Colors.BLUE}🔗 Meme URL: {meme['url']}{Colors.RESET}")
    
    # Ask if user wants to view the meme
    try:
        print(f"\n{Colors.GREEN}Want to see this as a real meme? (y/n){Colors.RESET}")
        choice = input().strip().lower()
        if choice == 'y':
            print(f"{Colors.YELLOW}Opening meme in browser...{Colors.RESET}")
            webbrowser.open(meme['url'])
    except:
        # If we're in a non-interactive environment, just continue
        pass
    
    print("\n" + "═" * 70)
    
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
        print(f"{Colors.YELLOW}No files staged. Commit will proceed without a meme :-({Colors.RESET}")
        return 0
    
    # Analyze code quality
    analysis = analyze_code_quality(staged_files)
    
    # Generate a meme
    meme = generate_meme(analysis["quality"])
    
    # Display results
    display_results(analysis, meme)
    
    # Always allow the commit to proceed - this is just for fun
    print(f"{Colors.GREEN}Commit will proceed regardless of code quality.{Colors.RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
