# Implementation Plan - Show Command

**Date:** November 4, 2025  
**Priority:** High for v0.2.0  
**Estimated Effort:** 4-6 hours

---

## 1. Overview

Implement the `show` command to display detailed information about an installed package. This command reads from the `dumpty.lock` file and presents package metadata, installation details, and file information in a user-friendly format.

---

## 2. Command Signature

```bash
dumpty show <package-name>
```

**Arguments:**
- `package_name` (required): The name of the package as defined in its manifest

**Options:**
- None initially (can add `--verbose` or `--json` in future iterations)

---

## 3. Implementation Details

### Location
**File:** `dumpty/cli.py`

### Code Structure

```python
@cli.command()
@click.argument("package_name")
def show(package_name: str):
    """Display detailed information about an installed package."""
    try:
        # 1. Load lockfile
        lockfile = LockfileManager()
        
        # 2. Find package in lockfile
        package = lockfile.get_package(package_name)
        if not package:
            console.print(f"[red]Error:[/] Package '{package_name}' is not installed")
            console.print("\nRun [cyan]dumpty list[/] to see installed packages")
            sys.exit(1)
        
        # 3. Display package information
        _display_package_info(package)
        
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        sys.exit(1)


def _display_package_info(package: InstalledPackage):
    """Display formatted package information using Rich."""
    
    # Header section
    console.print(f"\n[bold cyan]{package.name}[/] [dim]v{package.version}[/]")
    console.print()
    
    # Metadata section
    console.print("[bold]Package Information[/]")
    console.print(f"  Description: {package.description or '[dim]N/A[/]'}")
    console.print(f"  Author:      {package.author or '[dim]N/A[/]'}")
    console.print(f"  License:     {package.license or '[dim]N/A[/]'}")
    console.print(f"  Homepage:    {package.homepage or '[dim]N/A[/]'}")
    console.print()
    
    # Installation details
    console.print("[bold]Installation Details[/]")
    console.print(f"  Source:      {package.source}")
    console.print(f"  Version:     {package.installed_version}")
    console.print(f"  Installed:   {package.installed_date}")
    console.print()
    
    # Installed files grouped by agent
    console.print("[bold]Installed Files[/]")
    
    # Group files by agent
    files_by_agent = {}
    for file in package.installed_files:
        agent = file.agent
        if agent not in files_by_agent:
            files_by_agent[agent] = []
        files_by_agent[agent].append(file)
    
    # Display each agent's files
    for agent, files in sorted(files_by_agent.items()):
        console.print(f"\n  [cyan]{agent.upper()}[/] ({len(files)} files)")
        
        # Create table for files
        table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 2),
        )
        table.add_column("Artifact", style="dim")
        table.add_column("Path")
        
        for file in sorted(files, key=lambda f: f.target_path):
            table.add_row(
                file.artifact_name or "-",
                str(file.target_path)
            )
        
        console.print(table)
    
    console.print()
```

---

## 4. Data Requirements

### Lockfile Manager Extension

The `LockfileManager` class needs a method to retrieve a package by name:

```python
def get_package(self, package_name: str) -> Optional[InstalledPackage]:
    """Get an installed package by name.
    
    Args:
        package_name: The name of the package
        
    Returns:
        InstalledPackage if found, None otherwise
    """
    lockfile_data = self.load()
    
    for pkg in lockfile_data.packages:
        if pkg.name == package_name:
            return pkg
    
    return None
```

**File:** `dumpty/lockfile.py`

---

## 5. Output Format

### Example Output

```
bdd-workflows v1.0.0

Package Information
  Description: Behavior-Driven Development workflows for AI agents
  Author:      your-org
  License:     MIT
  Homepage:    https://github.com/org/bdd-workflows

Installation Details
  Source:      https://github.com/org/bdd-workflows
  Version:     v1.0.0
  Installed:   2025-11-04 10:30:15

Installed Files

  COPILOT (3 files)
    Artifact                Path
    planning               .github/prompts/planning.prompt.md
    code-review            .github/prompts/code-review.prompt.md
    tdd-workflow           .github/prompts/tdd.prompt.md

  CLAUDE (2 files)
    Artifact                Path
    code-review            .claude/commands/code-review.md
    tdd-workflow           .claude/commands/tdd.md
```

### Error Output

```
Error: Package 'non-existent-package' is not installed

Run dumpty list to see installed packages
```

---

## 6. Testing Strategy

### Test File
**Create:** `tests/test_cli_show.py`

### Test Cases

1. **Test show existing package**
   ```python
   def test_show_existing_package(tmp_path, runner):
       # Setup: Create lockfile with sample package
       # Execute: dumpty show bdd-workflows
       # Assert: Output contains package name, version, metadata, files
   ```

2. **Test show non-existent package**
   ```python
   def test_show_nonexistent_package(tmp_path, runner):
       # Setup: Empty or minimal lockfile
       # Execute: dumpty show missing-package
       # Assert: Error message, exit code 1, suggests using list command
   ```

3. **Test show package with multiple agents**
   ```python
   def test_show_package_multiple_agents(tmp_path, runner):
       # Setup: Package installed for copilot, claude, cursor
       # Execute: dumpty show multi-agent-package
       # Assert: All agents listed, files grouped correctly
   ```

4. **Test show package with minimal metadata**
   ```python
   def test_show_package_minimal_metadata(tmp_path, runner):
       # Setup: Package with only required fields (no author, homepage, etc.)
       # Execute: dumpty show minimal-package
       # Assert: Shows N/A for missing fields, doesn't crash
   ```

5. **Test show output formatting**
   ```python
   def test_show_output_formatting(tmp_path, runner):
       # Setup: Package with known data
       # Execute: dumpty show test-package
       # Assert: Verify table structure, color codes, formatting
   ```

6. **Test show with corrupt lockfile**
   ```python
   def test_show_corrupt_lockfile(tmp_path, runner):
       # Setup: Invalid lockfile
       # Execute: dumpty show any-package
       # Assert: Graceful error message
   ```

### Test Fixtures

Use existing test fixtures from `tests/fixtures/`:
- `sample_package/` - For package structure
- Create lockfile fixtures in test setup

---

## 7. Edge Cases

### Handled Cases

1. **Package not found**
   - Clear error message
   - Suggest using `dumpty list`
   - Exit code 1

2. **Missing metadata fields**
   - Display "N/A" for optional fields
   - Don't crash or show empty strings

3. **No installed files**
   - Show "No files installed" message
   - Should be impossible in normal operation (validation exists)

4. **Lockfile doesn't exist**
   - Error: "No packages installed"
   - Suggest running `dumpty install`

5. **Multiple packages with similar names**
   - Exact match only
   - Case-sensitive matching

---

## 8. Integration Points

### Dependencies (Existing)
- `LockfileManager.load()` - Read lockfile
- `InstalledPackage` model - Package data structure
- `Rich` library - Formatting and tables
- `Console` - Output handling

### New Dependencies
- `LockfileManager.get_package()` - New method to add

### Files Modified
1. `dumpty/cli.py` - Add `show` command
2. `dumpty/lockfile.py` - Add `get_package()` method
3. `tests/test_cli_show.py` - New test file

---

## 9. Implementation Checklist

### Phase 1: Core Implementation
- [ ] Add `get_package()` method to `LockfileManager`
- [ ] Implement `show` command in `cli.py`
- [ ] Implement `_display_package_info()` helper function
- [ ] Handle package not found error
- [ ] Format output with Rich tables

### Phase 2: Testing
- [ ] Create `tests/test_cli_show.py`
- [ ] Write test for existing package
- [ ] Write test for non-existent package
- [ ] Write test for multiple agents
- [ ] Write test for minimal metadata
- [ ] Write test for output formatting
- [ ] Achieve 85%+ coverage

### Phase 3: Documentation
- [ ] Update website documentation (mark as implemented)
- [ ] Add examples to README if needed
- [ ] Update CHANGELOG

---

## 10. Future Enhancements

Potential additions for future versions:

1. **JSON Output**
   ```bash
   dumpty show <package> --json
   ```
   - Machine-readable output for scripting

2. **Verbose Mode**
   ```bash
   dumpty show <package> --verbose
   ```
   - Show checksums for each file
   - Display source file paths
   - Show more detailed timestamps

3. **Validation**
   ```bash
   dumpty show <package> --verify
   ```
   - Check if installed files still match checksums
   - Detect modified or missing files

4. **Dependency Information**
   - If packages can depend on other packages in future
   - Show dependency tree

---

## 11. Success Criteria

- [ ] Command executes successfully for installed packages
- [ ] Output is clear, readable, and well-formatted
- [ ] Error messages are helpful and actionable
- [ ] Test coverage ≥85%
- [ ] No regressions in existing commands
- [ ] Documentation updated
- [ ] Matches behavior described on website

---

## 12. Time Estimates

| Task | Estimated Time |
|------|----------------|
| Implement `get_package()` | 30 minutes |
| Implement `show` command | 1.5 hours |
| Implement output formatting | 1 hour |
| Write tests | 1.5 hours |
| Test coverage and debugging | 30 minutes |
| Documentation updates | 30 minutes |
| **Total** | **4-6 hours** |

---

## 13. Risk Assessment

### Low Risk
- Well-defined requirements
- Simple data retrieval operation
- No file system modifications
- Existing patterns to follow

### Mitigation
- Follow patterns from `list` command
- Reuse existing Rich formatting utilities
- Comprehensive error handling
- Thorough testing

---

## 14. Review Points

Before considering complete:
1. ✅ Command works with real lockfile data
2. ✅ Error handling covers all edge cases
3. ✅ Output formatting is consistent with other commands
4. ✅ Tests pass with 85%+ coverage
5. ✅ Documentation is accurate
6. ✅ No performance issues with large packages
7. ✅ Code follows project style guidelines
