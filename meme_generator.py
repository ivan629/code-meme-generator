def save_to_history(analysis: Dict):
    """Save analysis to a history file for tracking over time."""
    history_path = os.path.join(os.path.expanduser("~"), ".code_quality_history.json")
    
    # Create entry
    entry = {
        "date": datetime.now().isoformat(),
        "score": analysis["score"],
        "quality": analysis["quality"],
        "message": analysis["message"],
        "lines_added": analysis["lines_added"],
        "lines_removed": analysis["lines_removed"],
        "issue_count": len(analysis["issues"])
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
    try:
        # Get staged files
        staged_files = get_staged_files()
        if not staged_files:
            print(f"{Colors.YELLOW}No files staged. Commit will proceed without analysis :-({Colors.RESET}")
            return 0
        
        print(f"{Colors.CYAN}Analyzing {len(staged_files)} staged files for code quality issues...{Colors.RESET}")
        
        # Analyze code quality
        analysis = analyze_code_quality(staged_files)
        
        # Display results
        display_results(analysis)
        
        # Print summary based on quality
        if analysis["quality"] in ["terrible", "bad"]:
            print(f"\n{Colors.RED}This code needs serious help, but the commit will proceed anyway.{Colors.RESET}")
            print(f"{Colors.RED}Consider fixing the critical and high severity issues before your colleagues see this.{Colors.RESET}")
        elif analysis["quality"] == "mediocre":
            print(f"\n{Colors.YELLOW}Your code is mediocre. You can do better than this, but the commit will proceed.{Colors.RESET}")
        elif analysis["quality"] == "good":
            print(f"\n{Colors.GREEN}Not bad! Your code is actually decent. Commit will proceed.{Colors.RESET}")
        else:
            print(f"\n{Colors.PURPLE}Exceptional code quality! Are you showing off? Commit will proceed.{Colors.RESET}")
        
        # Print counts of issues by severity
        critical_count = sum(1 for i in analysis["issue_details"] if i.get("severity") == "critical")
        high_count = sum(1 for i in analysis["issue_details"] if i.get("severity") == "high")
        medium_count = sum(1 for i in analysis["issue_details"] if i.get("severity") == "medium")
        low_count = sum(1 for i in analysis["issue_details"] if i.get("severity") not in ["critical", "high", "medium"])
        
        if critical_count or high_count or medium_count or low_count:
            print(f"\n{Colors.CYAN}Issue summary: {Colors.RED}{critical_count} critical{Colors.RESET}, {Colors.RED}{high_count} high{Colors.RESET}, {Colors.YELLOW}{medium_count} medium{Colors.RESET}, {Colors.BLUE}{low_count} low{Colors.RESET}")
            
        return 0
    except Exception as e:
        # Don't let the hook crash the commit process
        print(f"{Colors.RED}Error analyzing code: {str(e)}{Colors.RESET}")
        print(f"{Colors.YELLOW}Allowing commit to proceed despite analysis failure{Colors.RESET}")
        return 0


if __name__ == "__main__":
    sys.exit(main())#!/usr/bin/env python3

"""
BRUTAL Code Quality Check Pre-commit Hook

This hook ruthlessly analyzes your code changes, gives you a shocking assessment,
and provides clickable links to all the horrors found in your code.
"""

import os
import sys
import subprocess
import random
import re
import json
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
    UNDERLINE = "\033[4m"

# Make terminal hyperlinks work
def make_hyperlink(uri, text):
    return f"\033]8;;{uri}\033\\{text}\033]8;;\033\\"

# Enhanced ASCII art templates with more style and impact
ASCII_TEMPLATES = {
    "terrible": """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║      (╯°□°)╯︵ ┻━┻  ┻━┻ ︵ヽ(`Д´)ﾉ︵┻━┻   (ノಠ益ಠ)ノ彡┻━┻   ║
    ║                                                          ║
    ║               CODE CRIME SCENE DETECTED!                 ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """,
    "bad": """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║      (ಠ_ಠ)  ಠ╭╮ಠ  ಠ▃ಠ  (¬_¬)                            ║
    ║                                                          ║
    ║         THIS CODE WILL HAUNT YOUR NIGHTMARES            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """,
    "mediocre": """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       ¯\\_(ツ)_/¯  ¯\\(°_o)/¯  (－‸ლ)                       ║
    ║                                                          ║
    ║              BARELY AVOIDING DISASTER                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """,
    "good": """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║      (•̀ᴗ•́)و ̑̑   ✧*｡٩(ˊᗜˋ*)و✧*｡   (☞ﾟヮﾟ)☞                ║
    ║                                                          ║
    ║         NOT BAD, UNEXPECTEDLY NOT TERRIBLE!             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """,
    "excellent": """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║      ( •_•)                                              ║
    ║      ( •_•)>⌐■-■                                         ║
    ║      (⌐■_■)  YEAAAAAAAAH!                                ║
    ║                                                          ║
    ║           UNICORN CODE ACHIEVEMENT UNLOCKED!            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
}

# Enhanced quality messages with more shocking and creative content
QUALITY_MESSAGES = {
    "terrible": [
        "YOUR CODE MADE A SENIOR DEVELOPER CRY",
        "THIS CODE IS WHY ALIENS WON'T TALK TO US",
        "IF TECHNICAL DEBT WERE MONEY, YOU'D BE JEFF BEZOS",
        "MY GOD, WHAT HAVE YOU DONE?",
        "THIS REPO NEEDS AN EXORCISM, NOT A COMMIT",
        "CONGRATULATIONS! YOUR CODE BROKE THE STATIC ANALYZER",
        "THIS CODE IS CURSED. LITERALLY CURSED.",
        "THIS CODE IS SO BAD IT SHOULD BE ILLEGAL",
        "FOUND CRIMES AGAINST COMPUTER SCIENCE",
        "THE COMPILER CALLED. IT WANTS A RESTRAINING ORDER"
    ],
    "bad": [
        "THIS IS WHY CODE REVIEWS EXIST",
        "WHAT HAPPENED IN YOUR CHILDHOOD TO MAKE YOU WRITE CODE LIKE THIS?",
        "I'VE SEEN BETTER CODE GENERATED BY MONKEYS WITH KEYBOARDS",
        "THIS COMMIT SHOULD COME WITH THERAPY SESSIONS FOR THE REVIEWERS",
        "IS THIS CODE OR A CRYPTOGRAPHIC PUZZLE?",
        "SOMEHOW THIS CODE WORKS... LIKE BLACK MAGIC",
        "CODE FROM THE DEPTHS OF STACKOVERFLOW HELL",
        "404: CODE QUALITY NOT FOUND",
        "THIS CODE NEEDS JESUS",
        "DEBUGGING THIS LATER WILL BE LIKE SOLVING A MURDER MYSTERY"
    ],
    "mediocre": [
        "NEITHER IMPRESSIVE NOR HORRIFYING - THE PROGRAMMING EQUIVALENT OF BEIGE",
        "IT WORKS, BUT SO DOES DUCT TAPE",
        "THIS CODE IS LIKE FAST FOOD - IT'LL DO THE JOB, BUT NOBODY'S PROUD OF IT",
        "CONGRATULATIONS ON MEETING THE BARE MINIMUM REQUIREMENTS",
        "YOUR CODE WOULD GET A SOLID 'MEH' ON THE CREATIVITY SCALE",
        "AT LEAST IT'S BETTER THAN THE LAST COMMIT",
        "THE CODE EQUIVALENT OF A PARTICIPATION TROPHY",
        "BARELY PASSES THE SMELL TEST",
        "YOUR CODE IS THE DEVELOPER EQUIVALENT OF ROOM-TEMPERATURE WATER",
        "THIS CODE IS WHAT HAPPENS WHEN MEDIOCRITY AIMS HIGH"
    ],
    "good": [
        "THIS CODE DOESN'T SUCK, WHICH IS HIGHER PRAISE THAN YOU THINK",
        "SURPRISINGLY DECENT, ARE YOU FEELING OK?",
        "YOUR FUTURE SELF MIGHT ACTUALLY THANK YOU FOR THIS CODE",
        "SOMEONE MIGHT ACTUALLY ENJOY MAINTAINING THIS",
        "CLEAN AND FUNCTIONAL - LIKE A WELL-DESIGNED BATHROOM",
        "I'D ACTUALLY PUT MY NAME ON THIS CODE",
        "THIS CODE DOESN'T MAKE ME WANT TO CHANGE CAREERS",
        "LOOKS LIKE YOU ACTUALLY CARED WHEN WRITING THIS",
        "THIS IS THE CODE OF SOMEONE WHO GOT ENOUGH SLEEP",
        "YOUR CODE LOOKS PROFESSIONAL. SUSPICIOUS."
    ],
    "excellent": [
        "THIS CODE IS SO CLEAN I COULD EAT OFF IT",
        "POETRY IN PROGRAMMING FORM",
        "THIS BELONGS IN A MUSEUM OF BEAUTIFUL CODE",
        "ARE YOU SHOWING OFF? BECAUSE IT'S WORKING",
        "THIS IS THE CODE EQUIVALENT OF A PERFECTLY RIPE AVOCADO",
        "YOUR CODE SPARKS JOY - MARIE KONDO WOULD BE PROUD",
        "COMPILER BOWS DOWN IN RESPECT",
        "THIS CODE IS MORE ELEGANT THAN A BALLET DANCER",
        "SOMEONE DESERVES A RAISE FOR THIS MASTERPIECE",
        "THIS CODE IS SO GOOD IT'S MAKING ME QUESTION MY OWN ABILITIES"
    ]
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


def get_file_line_position(file_path: str, pattern: str, occurrence: int = 1) -> Tuple[int, str]:
    """
    Find the line number where a pattern occurs in a file.
    Returns (line_number, line_content) or (0, "") if not found.
    """
    try:
        content = get_file_content(file_path)
        lines = content.split('\n')
        
        count = 0
        for i, line in enumerate(lines):
            if pattern in line:
                count += 1
                if count == occurrence:
                    return (i + 1, line.strip())
        
        # If specific occurrence not found, return first match
        for i, line in enumerate(lines):
            if pattern in line:
                return (i + 1, line.strip())
                
        return (0, "")
    except:
        return (0, "")


def analyze_code_quality(files: List[str]) -> Dict:
    """Analyze code quality of the staged files - now with more brutal honesty and deeper analysis.
    
    This function scans your code for a wide variety of issues across multiple languages including:
    - Python, JavaScript, TypeScript, Java, C/C++, Go, Ruby, PHP, C#
    - HTML, CSS, SQL statements embedded in code
    - And many other common programming languages
    
    It performs static analysis to find actual problems that could hurt your code quality,
    security, maintainability, and performance.
    """
    total_score = 0
    max_possible_score = 0
    issues = []
    issue_details = []
    
    # Get basic stats
    lines_added, lines_removed = get_diff_stats()
    
    # Analyze individual files
    for file_path in files:
        # Skip obvious non-code files
        if file_path.endswith(('.png', '.jpg', '.gif', '.svg', '.pdf', '.md')):
            continue
            
        content = get_file_content(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Enhanced metrics with more brutal and specific checks
        metrics = {
            # Common code smells across languages
            "long_lines": [],  # Will store (line_num, length) tuples
            "todo_comments": [],  # Will store (line_num, content) tuples
            "commented_code": [],  # Will store line numbers
            "magic_numbers": [],  # Will store (line_num, value) tuples
            "empty_catch": [],  # Will store line numbers
            "nested_conditionals": [],  # Will store line numbers
            "long_functions": [],  # Will store (start_line, length) tuples
            "inconsistent_spacing": [],  # Will store line numbers
            "debug_statements": [],  # Will store (line_num, statement) tuples
            "force_push_comments": [],  # Will store (line_num, content) tuples
            
            # Language-specific checks
            "css_important": [],  # !important flags in CSS
            "sql_select_star": [],  # SELECT * in SQL
            "hardcoded_credentials": [],  # Potential passwords/keys
            "dead_code": [],  # Unreachable code
            "potential_memory_leaks": [],  # Patterns that might cause memory leaks
            "unhandled_errors": [],  # Missing error handling
            "insecure_functions": [],  # Known insecure function calls
            "large_indentation": []  # Excessive indentation
        }
        
        # Check for long lines
        for i, line in enumerate(content.split('\n')):
            line_stripped = line.strip()
            
            # Long lines
            if len(line_stripped) > 100:
                metrics["long_lines"].append((i+1, len(line_stripped)))
            
            # TODO comments
            if re.search(r'\b(TODO|FIXME|XXX|BUG|HACK)\b', line, re.IGNORECASE):
                metrics["todo_comments"].append((i+1, line_stripped))
            
            # Force push comments
            if re.search(r'\b(force|FORCE|yolo|YOLO|quick|dirty|DIRTY|nobody\s+will\s+notice)\b', line, re.IGNORECASE):
                metrics["force_push_comments"].append((i+1, line_stripped))
            
            # Excessive indentation (more than 4 levels)
            indent_level = (len(line) - len(line.lstrip())) // 4
            if indent_level > 4:
                metrics["large_indentation"].append((i+1, indent_level))
            
            # Debug statements
            if re.search(r'\b(console\.log|print|System\.out\.println|fmt\.Println|puts|echo|var_dump|printf|alert)\b', line):
                metrics["debug_statements"].append((i+1, line_stripped))
            
            # Magic numbers (not in obvious places like array indices)
            magic_matches = re.finditer(r'(?<!\w)[-+]?[0-9]+(?:\.[0-9]+)?(?![0-9_\.])(?!\w)', line_stripped)
            for match in magic_matches:
                # Skip if it's likely an array index or common value
                value = match.group(0)
                if not (re.search(r'\[\s*' + re.escape(value) + r'\s*\]', line_stripped) or value in ['0', '1', '-1', '100']):
                    metrics["magic_numbers"].append((i+1, value))
            
            # Empty catch blocks
            if re.search(r'catch\s*\([^)]*\)\s*{?\s*}?', line_stripped) or re.search(r'except:?\s*pass', line_stripped):
                metrics["empty_catch"].append(i+1)
            
            # Commented code (simplified detection)
            if (line_stripped.startswith('//') or line_stripped.startswith('#')) and re.search(r'[;{}()]', line_stripped):
                metrics["commented_code"].append(i+1)
            
            # Potential hardcoded credentials
            if re.search(r'\b(password|passwd|pwd|secret|key|token|api_?key|auth|credential)s?\s*[=:]+\s*["\'][^"\']+["\']', line_stripped, re.IGNORECASE):
                metrics["hardcoded_credentials"].append((i+1, line_stripped))
            
            # SELECT * in SQL
            if re.search(r'SELECT\s+\*\s+FROM', line_stripped, re.IGNORECASE):
                metrics["sql_select_star"].append(i+1)
            
            # !important in CSS
            if file_ext in ['.css', '.scss', '.less'] and '!important' in line_stripped:
                metrics["css_important"].append(i+1)
            
            # Known insecure functions
            insecure_funcs = [
                r'eval\(', r'exec\(', r'system\(', r'shell_exec\(', r'unserialize\(',
                r'md5\(', r'sha1\(', r'rand\(', r'random\(', r'dangerouslySetInnerHTML'
            ]
            for func in insecure_funcs:
                if re.search(func, line_stripped):
                    metrics["insecure_functions"].append((i+1, func.replace('\\', '')))
        
        # Detect nested conditionals and control structures
        nested_pattern = r'(if|for|while|switch|catch).*?{.*?(if|for|while|switch|catch).*?{'
        for match in re.finditer(nested_pattern, content, re.DOTALL):
            line_num = content[:match.start()].count('\n') + 1
            metrics["nested_conditionals"].append(line_num)
        
        # Detect long functions (simplified)
        function_pattern = r'(function|def|public|private|protected).*?{.*?}'
        for match in re.finditer(function_pattern, content, re.DOTALL):
            func_content = match.group(0)
            if len(func_content.split('\n')) > 30:  # Functions over 30 lines
                line_num = content[:match.start()].count('\n') + 1
                metrics["long_functions"].append((line_num, len(func_content.split('\n'))))
        
        # Calculate file score with enhanced penalties (lower is worse)
        file_score = 100
        
        # Apply penalties for each issue type
        penalty_map = {
            "long_lines": 2,
            "todo_comments": 3,
            "commented_code": 3,
            "magic_numbers": 1,
            "empty_catch": 10,
            "nested_conditionals": 5,
            "long_functions": 8,
            "inconsistent_spacing": 2,
            "debug_statements": 5,
            "force_push_comments": 15,
            "css_important": 5,
            "sql_select_star": 7,
            "hardcoded_credentials": 25,
            "dead_code": 5,
            "potential_memory_leaks": 10,
            "unhandled_errors": 7,
            "insecure_functions": 20,
            "large_indentation": 4
        }
        
        for issue_type, issues_list in metrics.items():
            if isinstance(issues_list, list):
                count = len(issues_list)
                if count > 0:
                    penalty = count * penalty_map.get(issue_type, 3)
                    file_score -= penalty
        
        # Add detailed issue information with clickable links to file locations
        if metrics["long_lines"]:
            for line_num, length in metrics["long_lines"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"📏 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has a line {length} chars long (recommended max: 100)")
                issue_details.append({"type": "long_line", "file": file_path, "line": line_num, "severity": "low"})
        
        if metrics["todo_comments"]:
            for line_num, content in metrics["todo_comments"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"⏰ {make_hyperlink(file_uri, f'{file_path}:{line_num}')} contains TODO/FIXME that will never be addressed")
                issue_details.append({"type": "todo", "file": file_path, "line": line_num, "severity": "low"})
        
        if metrics["empty_catch"]:
            for line_num in metrics["empty_catch"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"🕳️ {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has an empty catch block swallowing errors")
                issue_details.append({"type": "empty_catch", "file": file_path, "line": line_num, "severity": "high"})
        
        if metrics["nested_conditionals"]:
            for line_num in metrics["nested_conditionals"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"🪆 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has deeply nested conditionals (inception level)")
                issue_details.append({"type": "nested_conditionals", "file": file_path, "line": line_num, "severity": "medium"})
        
        if metrics["long_functions"]:
            for line_num, length in metrics["long_functions"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"📜 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has a {length}-line function (longer than most attention spans)")
                issue_details.append({"type": "long_function", "file": file_path, "line": line_num, "severity": "medium"})
        
        if metrics["debug_statements"]:
            for line_num, stmt in metrics["debug_statements"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"👀 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} contains debug statement that will leak to production")
                issue_details.append({"type": "debug_statement", "file": file_path, "line": line_num, "severity": "medium"})
        
        if metrics["force_push_comments"]:
            for line_num, content in metrics["force_push_comments"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"💥 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} contains YOLO/force comments indicating desperation")
                issue_details.append({"type": "force_comment", "file": file_path, "line": line_num, "severity": "high"})
        
        if metrics["hardcoded_credentials"]:
            for line_num, content in metrics["hardcoded_credentials"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"🔑 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has hardcoded credentials that everyone can now see")
                issue_details.append({"type": "credentials", "file": file_path, "line": line_num, "severity": "critical"})
        
        if metrics["insecure_functions"]:
            for line_num, func in metrics["insecure_functions"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"🔓 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} uses insecure function {func}")
                issue_details.append({"type": "insecure_function", "file": file_path, "line": line_num, "severity": "critical"})
        
        if metrics["sql_select_star"]:
            for line_num in metrics["sql_select_star"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"💾 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} uses SELECT * (future performance nightmare)")
                issue_details.append({"type": "select_star", "file": file_path, "line": line_num, "severity": "medium"})
        
        if metrics["css_important"]:
            for line_num in metrics["css_important"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"🎨 {make_hyperlink(file_uri, f'{file_path}:{line_num}')} uses !important (CSS specificity hack)")
                issue_details.append({"type": "css_important", "file": file_path, "line": line_num, "severity": "low"})
        
        if metrics["large_indentation"]:
            for line_num, indent in metrics["large_indentation"]:
                file_uri = f"file://{os.path.abspath(file_path)}:{line_num}"
                issues.append(f"↪️ {make_hyperlink(file_uri, f'{file_path}:{line_num}')} has {indent} levels of indentation (code pyramid of doom)")
                issue_details.append({"type": "indentation", "file": file_path, "line": line_num, "severity": "medium"})
        
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
    
    # Get a shocking message based on quality
    message = random.choice(QUALITY_MESSAGES[quality])
    
    return {
        "score": percentage,
        "quality": quality,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "message": message,
        "issues": issues,
        "issue_details": issue_details
    }


def display_results(analysis: Dict):
    """Display the analysis results with enhanced styling."""
    quality = analysis["quality"]
    color = {
        "terrible": Colors.RED,
        "bad": Colors.RED,
        "mediocre": Colors.YELLOW,
        "good": Colors.GREEN,
        "excellent": Colors.PURPLE
    }.get(quality, Colors.RESET)
    
    # Print fancy header
    print("\n" + "═" * 80)
    print(f"{color}╔{'═' * 78}╗{Colors.RESET}")
    print(f"{color}║{Colors.WHITE_BG}{Colors.BLACK_TEXT}                   💥  BRUTAL CODE QUALITY ASSESSMENT  💥                   {Colors.RESET}{color}║{Colors.RESET}")
    print(f"{color}╚{'═' * 78}╝{Colors.RESET}")
    
    # Print the ASCII art with fancy border
    print(f"{color}{ASCII_TEMPLATES[quality]}{Colors.RESET}")
    
    # Print the shocking message
    print(f"{color}   {analysis['message']}{Colors.RESET}")
    
    # Print analysis with enhanced formatting
    print(f"\n{Colors.CYAN}▓▒░ Quality score: {color}{analysis['score']:.1f}%{Colors.RESET} {Colors.CYAN}░▒▓{Colors.RESET}")
    print(f"{Colors.CYAN}▓▒░ Changes: +{analysis['lines_added']} lines, -{analysis['lines_removed']} lines {Colors.CYAN}░▒▓{Colors.RESET}")
    
    # Print issues if any - with emoji and color
    if analysis["issues"]:
        print(f"\n{Colors.YELLOW}🚨 DETECTED ISSUES [CLICK TO JUMP TO LOCATION]:{Colors.RESET}")
        
        # Group issues by severity
        critical_issues = [i for i in analysis["issue_details"] if i.get("severity") == "critical"]
        high_issues = [i for i in analysis["issue_details"] if i.get("severity") == "high"]
        medium_issues = [i for i in analysis["issue_details"] if i.get("severity") == "medium"]
        
        if critical_issues:
            print(f"\n{Colors.RED}💀 CRITICAL ISSUES:{Colors.RESET}")
            critical_indexes = [i for i, detail in enumerate(analysis["issue_details"]) if detail.get("severity") == "critical"]
            for idx in critical_indexes:
                print(f"  {Colors.RED}•{Colors.RESET} {analysis['issues'][idx]}")
        
        if high_issues:
            print(f"\n{Colors.RED}🔥 HIGH SEVERITY ISSUES:{Colors.RESET}")
            high_indexes = [i for i, detail in enumerate(analysis["issue_details"]) if detail.get("severity") == "high"]
            for idx in high_indexes:
                print(f"  {Colors.RED}•{Colors.RESET} {analysis['issues'][idx]}")
        
        if medium_issues:
            print(f"\n{Colors.YELLOW}⚠️ MEDIUM SEVERITY ISSUES:{Colors.RESET}")
            medium_indexes = [i for i, detail in enumerate(analysis["issue_details"]) if detail.get("severity") == "medium"]
            for idx in medium_indexes:
                print(f"  {Colors.YELLOW}•{Colors.RESET} {analysis['issues'][idx]}")
        
        # Remaining issues (low severity)
        other_indexes = [i for i, detail in enumerate(analysis["issue_details"]) if detail.get("severity") not in ["critical", "high", "medium"]]
        if other_indexes:
            print(f"\n{Colors.BLUE}ℹ️ OTHER ISSUES:{Colors.RESET}")
            for idx in other_indexes:
                print(f"  {Colors.BLUE}•{Colors.RESET} {analysis['issues'][idx]}")
    
    print("\n" + "═" * 80)
    
    # Add educational tips based on issues found
    tips_shown = False
    
    if any("credentials" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"\n{Colors.YELLOW}💡 TIP: Hardcoded credentials should be moved to environment variables or a secure vault.{Colors.RESET}")
        tips_shown = True
    
    if any("debug_statement" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Remove debug statements before committing, or use a proper logging framework.{Colors.RESET}")
        tips_shown = True
    
    if any("empty_catch" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Empty catch blocks hide errors. Log or handle exceptions properly.{Colors.RESET}")
        tips_shown = True
    
    if any("long_function" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Break long functions into smaller, more focused ones for better maintainability.{Colors.RESET}")
        tips_shown = True
        
    if any("nested_conditionals" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Deeply nested conditions are hard to follow. Extract code into helper functions.{Colors.RESET}")
        tips_shown = True
        
    if any("insecure_function" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Insecure functions can lead to vulnerabilities. Use recommended secure alternatives.{Colors.RESET}")
        tips_shown = True
    
    if any("select_star" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Avoid SELECT * queries - they can cause performance issues and break when schema changes.{Colors.RESET}")
        tips_shown = True
        
    if any("indentation" in i.get("type", "") for i in analysis["issue_details"]):
        print(f"{Colors.YELLOW}💡 TIP: Deep indentation creates code that's hard to understand. Refactor to reduce nesting levels.{Colors.RESET}")
        tips_shown = True
    
    if tips_shown:
        print("\n" + "═" * 80)
    
    # Save to history
    save_to_history(analysis)
