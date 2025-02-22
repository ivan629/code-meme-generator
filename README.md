# 💥 Shocking & Stylish Code Quality Meme Generator 💥

A pre-commit Git hook that analyzes your code, judges its quality, and **generates hilarious memes** to either celebrate your coding excellence or shame your questionable decisions.

![Meme Generator Example](https://api.memegen.link/images/keanu-breathtaking/YOUR_CODE/BELONGS_IN_A_MUSEUM.jpg)

## What Is This?

This is a pre-commit hook that runs whenever you make a Git commit. Instead of just silently checking your code or displaying boring errors, it:

1. Analyzes the quality of your code changes
2. Generates a shocking and stylish meme tailored to your code quality
3. Shows you terminal ASCII art for immediate feedback
4. Offers to open a real meme in your browser
5. Keeps a history of your coding quality over time

## Features

- 😎 **Stylish Terminal Output**: Colorful ASCII art and emoji-rich feedback
- 🤣 **Quality-Based Memes**: Different meme templates based on how "good" or "terrible" your code is
- 🔍 **Code Analysis**: Checks for common issues like:
  - Long lines
  - TODO comments that will never be addressed
  - Empty catch blocks
  - Nested conditionals
  - Long functions
  - Debug statements left in production code
  - And more!
- 📊 **Score Tracking**: Keeps a history of your code quality over time
- 🌐 **Real Meme Generation**: Opens actual memes in your browser using memegen.link API

## Installation

1. Download the script:

```bash
curl -o pre-commit https://raw.githubusercontent.com/yourusername/code-meme-hook/main/pre-commit
```

2. Make it executable:

```bash
chmod +x pre-commit
```

3. Place it in your repository's `.git/hooks/` directory:

```bash
mv pre-commit /path/to/your/repo/.git/hooks/
```

4. For team-wide installation, consider using a tool like [pre-commit](https://pre-commit.com/) by adding to your `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/yourusername/code-meme-hook
    rev: v1.0.0
    hooks:
    -   id: code-quality-meme-generator
```

## How It Works

When you make a commit, the hook:

1. Gets a list of all staged files in your commit
2. Analyzes the code in each file for quality issues
3. Calculates an overall quality score (0-100%)
4. Determines a quality level ("terrible", "bad", "mediocre", "good", or "excellent")
5. Generates a meme matching that quality level
6. Displays both ASCII art in the terminal and offers to open a real meme
7. Saves the result to a history file (`~/.code_meme_history.json`)

## Quality Levels

The hook classifies your code into one of five quality levels:

- **Terrible** (< 20%): "CODE SO BRUTAL IT VIOLATES GENEVA CONVENTION"
- **Bad** (20-40%): "MERGED THIS CODE, BLAMED THE INTERN"
- **Mediocre** (40-60%): "FIXED ONE BUG, CREATED THREE MORE"
- **Good** (60-80%): "PR APPROVED WITHOUT A SINGLE COMMENT"
- **Excellent** (80-100%): "CODE SO ELEGANT COULD MAKE A GROWN DEV CRY"

## Example Output

```
═══════════════════════════════════════════════════════════════════════════
╔══════════════════════════════════════════════════════════════════════════╗
║           💥  CODE QUALITY MEME GENERATOR  💥                            ║
╚══════════════════════════════════════════════════════════════════════════╝

    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      (•̀ᴗ•́)و ̑̑   ✧*｡٩(ˊᗜˋ*)و✧*｡          ║
    ║                                          ║
    ║         YOUR CODE IS IMPRESSIVE!         ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    
▓▒░ Quality score: 73.5% ░▒▓
▓▒░ Changes: +45 lines, -12 lines ░▒▓

🔍 TOP ISSUES:
  • 📏 src/components/UserProfile.js has 3 lines longer than a CVS receipt
  • 📜 src/utils/helpers.js has 1 functions longer than War and Peace

🖼️ Meme text: CODE SO CLEAN - COULD EAT OFF IT
🔗 Meme URL: https://api.memegen.link/images/goodguygrag/CODE_SO_CLEAN/COULD_EAT_OFF_IT.jpg

Want to see this as a real meme? (y/n)
```

## Customization

You can customize the script by:

1. Adding more meme templates to `MEME_TEMPLATES`
2. Adjusting the scoring algorithm in `analyze_code_quality()`
3. Adding more code quality checks
4. Modifying the ASCII art in `ASCII_TEMPLATES`

## Why Use This?

- **Makes Code Reviews Fun**: Motivates better coding with humor
- **Team Building**: Share your memes with teammates for laughs
- **Learning Tool**: Highlights common issues in a memorable way
- **Actually Useful**: Despite the humor, it provides genuine code quality feedback
- **No Blocking**: Unlike strict linters, this lets your commit proceed while providing feedback

## Requirements

- Python 3.6+
- Git
- Web browser (optional, for viewing memes)

## History Tracking

The hook maintains a history file at `~/.code_meme_history.json` that keeps track of your code quality over time. You could build additional tools to visualize trends in your coding quality based on this data.

## License

MIT - Feel free to modify and share!

## Contributing

Contributions welcome! Add more meme templates, improve code analysis, or enhance the ASCII art.

---

*Remember: Good code may be temporary, but dank memes are forever.*
