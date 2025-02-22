#!/bin/bash

# Install script for code-meme-generator pre-commit hook
# This will set up the hook for the current repository

# Install pre-commit if needed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit framework..."
    pip install pre-commit
fi

# Create or update .pre-commit-config.yaml
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Updating existing .pre-commit-config.yaml..."
    # Check if our hook is already in the config
    if ! grep -q "code-meme-generator" .pre-commit-config.yaml; then
        # Add our repo to the existing config
        printf "\n# Code quality meme generator\n-   repo: https://github.com/ivan629/code-meme-generator\n    rev: v1.0.0\n    hooks:\n    -   id: code-quality-meme\n" >> .pre-commit-config.yaml
    fi
else
    echo "Creating .pre-commit-config.yaml..."
    cat > .pre-commit-config.yaml << 'EOF'
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

# Code quality meme generator
-   repo: https://github.com/ivan629/code-meme-generator
    rev: v1.0.0
    hooks:
    -   id: code-quality-meme
EOF
fi

# Install the pre-commit hooks
echo "Installing hooks..."
pre-commit install

echo "✨ Code Quality Meme Generator installed successfully! ✨"
echo "Your commits will now come with quality judgment in meme form."
