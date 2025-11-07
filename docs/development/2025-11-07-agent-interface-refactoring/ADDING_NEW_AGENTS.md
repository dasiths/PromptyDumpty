# Adding New Agents to PromptyDumpty

After the agent interface refactoring, adding support for a new AI coding agent is straightforward and requires minimal code changes.

## Overview

With the new plugin-like architecture, adding a new agent requires:
1. Creating a single implementation file (~30 lines)
2. Registering the agent in `__init__.py` (2 lines)
3. Adding an enum member (1 line)
4. Writing tests (optional but recommended)

Total effort: **Under 50 lines of code**

---

## Step-by-Step Guide

### Step 1: Create Agent Implementation File

Create a new file in `dumpty/agents/` named after your agent (e.g., `newagent.py`):

```python
"""New Agent agent implementation."""

from pathlib import Path
from .base import BaseAgent


class NewAgentAgent(BaseAgent):
    """New Agent agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier (lowercase)."""
        return "newagent"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "New Agent"
    
    @property
    def directory(self) -> str:
        """Default directory path."""
        return ".newagent"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if New Agent is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .newagent directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Key Points:**
- File name should be descriptive (avoid Python keywords)
- Class name should be `<AgentName>Agent`
- `name` must be unique and lowercase
- `display_name` is shown to users
- `directory` is the default folder (e.g., `.newagent`)
- `is_configured()` defines detection logic

### Step 2: Register Agent

In `dumpty/agents/__init__.py`, add your import and registration:

```python
# Add to imports section
from .newagent import NewAgentAgent

# Add to registration section
_registry.register(NewAgentAgent())

# Add to __all__ exports
__all__ = [
    # ... existing exports
    "NewAgentAgent",
]
```

### Step 3: Add Enum Member

In `dumpty/agent_detector.py`, add to the `Agent` enum:

```python
class Agent(Enum):
    """Supported AI agents with their directory structures."""
    
    # ... existing members
    NEWAGENT = "newagent"  # Value must match agent.name
```

### Step 4: Add Tests (Recommended)

In `tests/test_agents_implementations.py`, add test class:

```python
from dumpty.agents.newagent import NewAgentAgent


class TestNewAgentAgent:
    """Tests for NewAgentAgent."""
    
    def test_properties(self):
        """Test agent properties."""
        agent = NewAgentAgent()
        assert agent.name == "newagent"
        assert agent.display_name == "New Agent"
        assert agent.directory == ".newagent"
    
    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".newagent").mkdir()
        
        agent = NewAgentAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = NewAgentAgent()
        assert agent.is_configured(tmp_path) is False
```

### Step 5: Verify Implementation

Run the tests to ensure everything works:

```bash
# Test your specific agent
pytest tests/test_agents_implementations.py::TestNewAgentAgent -v

# Test all agent-related code
pytest tests/test_agent*.py tests/test_agents*.py -v

# Test that the enum works
python -c "from dumpty.agent_detector import Agent; print(Agent.NEWAGENT.directory)"
```

---

## Advanced: Custom Detection Logic

If your agent requires more sophisticated detection than simple directory existence, override `is_configured()`:

### Example: Check for Configuration File

```python
def is_configured(self, project_root: Path) -> bool:
    """Check for both directory and config file."""
    agent_dir = project_root / self.directory
    config_file = agent_dir / "config.json"
    return (
        agent_dir.exists() 
        and agent_dir.is_dir() 
        and config_file.exists()
    )
```

### Example: Multiple Directories

```python
def is_configured(self, project_root: Path) -> bool:
    """Check for either primary or alternate directory."""
    primary = project_root / ".newagent"
    alternate = project_root / ".newagent-alt"
    return (
        (primary.exists() and primary.is_dir()) or
        (alternate.exists() and alternate.is_dir())
    )
```

### Example: File Content Validation

```python
def is_configured(self, project_root: Path) -> bool:
    """Check directory and validate configuration."""
    agent_dir = project_root / self.directory
    config_file = agent_dir / "config.json"
    
    if not (agent_dir.exists() and config_file.exists()):
        return False
    
    try:
        import json
        with config_file.open() as f:
            config = json.load(f)
        return "agent" in config and config["agent"] == "newagent"
    except (json.JSONDecodeError, IOError):
        return False
```

---

## Code Quality Checklist

Before submitting your agent:

- [ ] Code formatted with `black dumpty/agents/ tests/`
- [ ] No linting errors: `ruff check dumpty/agents/ tests/`
- [ ] All tests pass: `pytest tests/test_agents_implementations.py::TestNewAgentAgent -v`
- [ ] Agent properties match specification
- [ ] Detection logic is correct
- [ ] Documentation strings are clear

---

## Common Issues

### Issue: "Agent implementation not found"

**Cause:** Agent not registered in `__init__.py` or enum value doesn't match `name` property.

**Fix:** 
1. Ensure `_registry.register(NewAgentAgent())` is in `agents/__init__.py`
2. Verify enum value matches: `NEWAGENT = "newagent"` and `def name(self) -> str: return "newagent"`

### Issue: Enum member not accessible

**Cause:** Enum member not added to `Agent` enum.

**Fix:** Add `NEWAGENT = "newagent"` to the `Agent` enum in `agent_detector.py`

### Issue: Tests failing with "already registered"

**Cause:** Running tests multiple times without clearing registry.

**Fix:** Use the `registry` fixture in tests, which automatically saves/restores state.

---

## Example: Complete Agent Addition

Here's a complete example of adding support for "Windsurf":

**File: `dumpty/agents/windsurf.py`**
```python
"""Windsurf agent implementation."""

from pathlib import Path
from .base import BaseAgent


class WindsurfAgent(BaseAgent):
    """Windsurf agent implementation."""
    
    @property
    def name(self) -> str:
        return "windsurf"
    
    @property
    def display_name(self) -> str:
        return "Windsurf"
    
    @property
    def directory(self) -> str:
        return ".windsurf"
    
    def is_configured(self, project_root: Path) -> bool:
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**In `dumpty/agents/__init__.py`:**
```python
from .windsurf import WindsurfAgent
_registry.register(WindsurfAgent())
__all__ = [..., "WindsurfAgent"]
```

**In `dumpty/agent_detector.py`:**
```python
class Agent(Enum):
    ...
    WINDSURF = "windsurf"
```

**Total lines:** ~35 lines of code

---

## Getting Help

If you encounter issues:

1. Check existing agent implementations in `dumpty/agents/` for reference
2. Review the base class documentation in `dumpty/agents/base.py`
3. Look at test examples in `tests/test_agents_implementations.py`
4. Open an issue on GitHub with the "agent-support" label

---

## Summary

Adding a new agent is now a **simple, isolated change**:

1. ✅ Single implementation file (~30 lines)
2. ✅ Two registration lines
3. ✅ One enum member
4. ✅ Tests (3-5 test methods)

**Total:** Under 50 lines of code, fully tested and integrated!
