#!/bin/bash
# Script to switch between local and CI build configurations

case "$1" in
  "local")
    echo "Switching to local setuptools configuration..."
    if [ -f "pyproject_backup.toml" ]; then
      cp pyproject.toml pyproject_ci.toml 2>/dev/null || true
      cp pyproject_backup.toml pyproject.toml
      echo "✅ Switched to setuptools configuration (local builds)"
    else
      echo "❌ pyproject_backup.toml not found"
      exit 1
    fi
    ;;
  "ci")
    echo "Switching to CI maturin configuration..."
    if [ -f "pyproject_backup.toml" ]; then
      cp pyproject.toml pyproject_local.toml 2>/dev/null || true
      cp pyproject_backup.toml pyproject.toml
      echo "✅ Switched to maturin configuration (CI builds)"
    else
      echo "❌ pyproject_backup.toml not found"
      exit 1
    fi
    ;;
  "restore")
    echo "Restoring setuptools configuration..."
    if [ -f "pyproject_local.toml" ]; then
      cp pyproject_local.toml pyproject.toml
      echo "✅ Restored setuptools configuration"
    else
      echo "❌ No backup found, creating from current setuptools setup"
      cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "setuptools-rust"]
build-backend = "setuptools.build_meta"

[project]
name = "rusty_tags"
version = "0.6.0"
requires-python = ">=3.10"
description = "Core HTML generation library with Rust-based Python extension - high performance, minimal dependencies"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "RustyTags Contributors"}
]
keywords = ["html", "svg", "performance", "rust", "core", "generation"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup :: HTML",
]

[project.urls]
Homepage = "https://github.com/ndendic/rustyTags"
Repository = "https://github.com/ndendic/rustyTags"
Issues = "https://github.com/ndendic/rustyTags/issues"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pyright]
include = ["rusty_tags"]
pythonVersion = "3.12"
typeCheckingMode = "basic"

[tool.setuptools.packages]
# Pure Python packages/modules
find = { where = ["rusty_tags"] }

[[tool.setuptools-rust.ext-modules]]
# Build the extension as core.* inside the package directory (rusty_tags/core.*)
target = "core"
path = "Cargo.toml"
binding = "PyO3"
EOF
      echo "✅ Created default setuptools configuration"
    fi
    ;;
  *)
    echo "Usage: $0 {local|ci|restore}"
    echo ""
    echo "  local   - Switch to setuptools config for local development"
    echo "  ci      - Switch to maturin config for CI builds"
    echo "  restore - Restore setuptools config from backup"
    echo ""
    echo "Current configuration:"
    if grep -q "maturin" pyproject.toml 2>/dev/null; then
      echo "  📦 Maturin (CI builds)"
    elif grep -q "setuptools" pyproject.toml 2>/dev/null; then
      echo "  🔧 Setuptools (local development)"
    else
      echo "  ❓ Unknown configuration"
    fi
    exit 1
    ;;
esac