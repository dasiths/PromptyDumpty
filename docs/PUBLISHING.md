# Publishing to PyPI with GitHub Actions

This repository uses GitHub Actions to publish releases to PyPI using **Trusted Publishing** (OpenID Connect), which is more secure than using API tokens.

## Setup Instructions

### 1. Configure Trusted Publishing on PyPI

Before you can use the workflow, you need to configure trusted publishers on PyPI:

#### For TestPyPI (recommended for testing first):

1. Go to https://test.pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `prompty-dumpty`
   - **Owner**: `dasiths` (your GitHub username)
   - **Repository name**: `PromptyDumpty`
   - **Workflow name**: `publish-to-pypi.yml`
   - **Environment name**: `testpypi`
4. Click "Add"

#### For PyPI (production):

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name**: `prompty-dumpty`
   - **Owner**: `dasiths` (your GitHub username)
   - **Repository name**: `PromptyDumpty`
   - **Workflow name**: `publish-to-pypi.yml`
   - **Environment name**: `pypi`
4. Click "Add"

### 2. Configure GitHub Environments

1. Go to your GitHub repository: https://github.com/dasiths/PromptyDumpty/settings/environments
2. Create two environments:
   - **testpypi** (for testing)
   - **pypi** (for production)
3. (Optional) Add protection rules:
   - For `pypi` environment, add required reviewers to prevent accidental releases
   - Add deployment branches rule to only allow `main` branch

### 3. Using the Workflow

#### To publish to TestPyPI (for testing):

1. Go to the **Actions** tab in your GitHub repository
2. Select **"Publish to PyPI"** workflow from the left sidebar
3. Click **"Run workflow"** button (top right)
4. Select:
   - Branch: `main`
   - Environment: `testpypi`
5. Click **"Run workflow"**

The workflow will:
- Extract the version from `pyproject.toml`
- Build the distribution packages
- Run `twine check` to verify metadata
- Upload to TestPyPI
- Provide a direct link to the published package

#### To publish to PyPI (production):

1. **Important**: Make sure you've tested on TestPyPI first!
2. Update the version in `pyproject.toml` (you cannot overwrite versions)
3. Commit and push the version change
4. Go to the **Actions** tab
5. Select **"Publish to PyPI"** workflow
6. Click **"Run workflow"**
7. Select:
   - Branch: `main`
   - Environment: `pypi`
8. Click **"Run workflow"**

### 4. Workflow Features

The workflow automatically:

✅ **Extracts version** from `pyproject.toml` (no manual input needed)  
✅ **Builds** the distribution packages (`.tar.gz` and `.whl`)  
✅ **Validates** packages with `twine check`  
✅ **Separates** build and publish jobs for security  
✅ **Uses Trusted Publishing** (no tokens/passwords needed)  
✅ **Generates attestations** for package integrity  
✅ **Provides direct links** to published packages  
✅ **Shows file hashes** for verification  

### 5. Version Management

The workflow reads the version from `pyproject.toml`:

```toml
[project]
name = "prompty-dumpty"
version = "0.1.0"  # Update this for each release
```

**Important**: 
- You cannot republish the same version to PyPI
- Always increment the version before publishing:
  - `0.1.0` → `0.1.1` (patch)
  - `0.1.0` → `0.2.0` (minor)
  - `0.1.0` → `1.0.0` (major)

### 6. Recommended Release Process

1. **Make changes** in a feature branch
2. **Update version** in `pyproject.toml`
3. **Run tests** locally: `make test`
4. **Merge** to `main` branch
5. **Tag the release** (optional but recommended):
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
6. **Test on TestPyPI** first using the workflow
7. **Verify installation**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ prompty-dumpty
   ```
8. **Publish to PyPI** using the workflow

### 7. Troubleshooting

**"Trusted publishing exchange failure"**
- Make sure you configured the trusted publisher on PyPI exactly as specified
- Check that the environment name in the workflow matches what you configured

**"File already exists"**
- You're trying to upload a version that already exists
- Update the version in `pyproject.toml` and try again

**"No such file or directory: dist/"**
- The build job failed
- Check the build logs in the Actions tab

**"Workflow requires approval"**
- If you set up environment protection rules, an approver needs to approve the deployment
- This is a security feature to prevent accidental releases

### 8. Security Benefits

Using Trusted Publishing instead of API tokens:

🔒 **No secrets to manage** - No tokens that can leak or expire  
🔒 **Automatic credential rotation** - Credentials are temporary and single-use  
🔒 **Audit trail** - Clear connection between GitHub workflow and PyPI releases  
🔒 **Scoped permissions** - Can only publish from specified repository/workflow  
🔒 **Phishing resistant** - No credentials that can be stolen  

## PyPI README Configuration

This project maintains a separate `PYPI_README.md` file optimized for the PyPI package page.

### Why a Separate PyPI README?

The `PYPI_README.md` is condensed and focused on:
- Installation and quick start
- Core features and usage
- Removing development-specific content (Makefile, website dev, etc.)
- PyPI-specific badges

### Using the PyPI README

To use it for PyPI publishing, update `pyproject.toml`:

```toml
[project]
readme = "PYPI_README.md"  # Changed from README.md
```

### Maintaining Both Files

When making changes:
1. **Always update `README.md` first** - This is the source of truth for GitHub
2. **Periodically sync `PYPI_README.md`** - Copy relevant user-facing changes
3. **Keep PYPI_README.md focused** - Exclude development/contributor details

## Additional Resources

- [PyPI Trusted Publishing Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging User Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
