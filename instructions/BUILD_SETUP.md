# Build Setup Documentation

This project uses a dual-configuration setup to handle different build systems for local development vs CI/PyPI publishing.

## Configuration Files

- **`pyproject.toml`** - Current active configuration (switches between local/CI)
- **`pyproject_backup.toml`** - Maturin configuration for CI builds and PyPI publishing
- **`switch-config.sh`** - Script to switch between configurations

## Local Development (Setuptools)

For local development, use the setuptools configuration:

```bash
# Switch to local configuration (if not already)
./switch-config.sh local

# Build locally
pip install -e .
# or
python setup.py develop
```

## CI/PyPI Publishing (Maturin)

The GitHub Actions automatically use the maturin configuration for building and publishing:

- **Triggers**: Push tags like `v0.6.0`, `v1.0.0`, etc.
- **Platforms**: Linux (x86_64, aarch64, etc.), Windows (x64, x86), macOS (x86_64, aarch64)
- **Publishing**: Uses OIDC trusted publishing (no API tokens needed)

### Setting Up Trusted Publishing

1. Go to [PyPI](https://pypi.org/manage/project/rusty-tags/settings/publishing/)
2. Add a new trusted publisher:
   - **Owner**: `ndendic` (or your GitHub username)
   - **Repository**: `rustyTags`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

## Workflows

### 1. CI and Publishing (`CI.yml`)

Your existing maturin-generated workflow that:
- **Tests builds** on push/PR to main/master branches
- **Automatically publishes to PyPI** when you push version tags
- **Supports all platforms**: Linux (including musl), Windows, macOS with multiple architectures

```bash
git tag v0.6.1
git push origin v0.6.1
```

### 2. Test Build (`test-build.yml`)

Tests the build process on push/PR without publishing:
- Builds wheel using maturin
- Tests installation and basic functionality
- Runs on every push to main/develop

## Manual Configuration Switching

```bash
# Switch to local development (setuptools)
./switch-config.sh local

# Switch to CI configuration (maturin) - for testing
./switch-config.sh ci

# Restore to local configuration
./switch-config.sh restore

# Show current configuration
./switch-config.sh
```

## Dependencies

- **Local**: No runtime dependencies (minimal core)
- **CI/PyPI**: Includes `datastar-py>=0.6.5` for Datastar integration

## Build Process Flow

1. **Local Development**: `pyproject.toml` (setuptools) → `pip install -e .`
2. **CI Testing**: `pyproject_backup.toml` → maturin build → test installation
3. **PyPI Release**: `pyproject_backup.toml` → maturin build all platforms → publish

This setup allows you to:
- ✅ Develop locally with working setuptools (no maturin issues)
- ✅ Publish to PyPI with optimized maturin builds
- ✅ Test CI builds without publishing
- ✅ Switch configurations easily with one script

## Triggering a Release

1. Update version in both configuration files
2. Commit and push changes
3. Create and push a version tag:
   ```bash
   git tag v0.6.1
   git push origin v0.6.1
   ```
4. GitHub Actions will build and publish automatically