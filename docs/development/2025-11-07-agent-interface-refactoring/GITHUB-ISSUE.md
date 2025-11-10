# GitHub Issue - Agent Interface Refactoring

## **Title:**
Refactor Agent Detection to Plugin-like Interface Architecture

---

## **Description:**

### Overview
Refactor PromptyDumpty's agent detection system from a monolithic enum-based design to a plugin-like interface-based architecture. This will enable adding new AI coding assistants by creating a single implementation file, improving extensibility and maintainability while maintaining 100% backward compatibility.

**Full Context:** See development session folder at [`docs/development/2025-11-07-agent-interface-refactoring/`](../../../docs/development/2025-11-07-agent-interface-refactoring/)

### Motivation
Currently, adding a new agent requires modifying the central `Agent` enum and understanding the entire detection flow. This refactoring encapsulates agent-specific logic into individual implementation files, making the codebase more maintainable and extensible.

### Key Documents
- **Requirements:** [`REQUIREMENTS.md`](./REQUIREMENTS.md)
- **Technical Spec:** [`SPEC.md`](./SPEC.md)
- **Implementation Plan:** [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md)

---

## **Scope**

This issue covers **all 6 phases** from the implementation plan:
1. **Foundation**: Base infrastructure (BaseAgent, AgentRegistry)
2. **Proof of Concept**: First 2 agents (Copilot, Claude)
3. **Remaining Agents**: Complete all 8 agents
4. **Integration**: Update Agent enum and AgentDetector
5. **Testing**: Comprehensive test suite
6. **Validation**: Coverage, documentation, cleanup

---

## **Implementation Guidance**

Follow the implementation plan phases sequentially for best results:

### Foundation (Phase 1)
- Create `dumpty/agents/` package structure
- Implement `BaseAgent` abstract class in `dumpty/agents/base.py` (see SPEC.md Section 3)
- Implement `AgentRegistry` singleton in `dumpty/agents/registry.py` (see SPEC.md Section 3)
- Write tests as you go: `tests/test_agents_base.py` and `tests/test_agents_registry.py`

### Agent Implementations (Phases 2-3)
- Start with proof of concept: `CopilotAgent` and `ClaudeAgent`
- Follow the pattern in SPEC.md Appendix B for remaining 6 agents
- Each agent ~30 lines of code with identical structure
- Test each agent: properties, detection when configured, detection when not configured
- Register all agents in `dumpty/agents/__init__.py`

### Integration (Phase 4)
- Update `Agent` enum in `dumpty/agent_detector.py` to delegate to implementations
  - Change enum values from tuples to strings
  - Add `_get_impl()` helper method
  - Update `directory` and `display_name` properties to delegate
- Update `AgentDetector.detect_agents()` to use registry
- **Critical**: All existing tests in `tests/test_agent_detector.py` must pass unchanged

### Testing (Phase 5)
- Add backward compatibility tests to `tests/test_agent_detector.py`
- Run full test suite: `pytest -v`
- Manual smoke tests for CLI commands

### Validation (Phase 6)
- Coverage target: >90% for new code
- Create `ADDING_NEW_AGENTS.md` guide
- Run code quality checks: `black`, `ruff`

---

## **Key Technical Decisions**

Refer to SPEC.md Section 12 for detailed decisions. Key points:

- **Singleton Registry**: Single global instance for consistent state
- **Lazy Delegation**: Enum delegates to implementations via `_get_impl()` method
- **Manual Registration**: Agents explicitly registered in `__init__.py` for clarity
- **Backward Compatibility**: Zero breaking changes - existing API preserved exactly

---

## **Acceptance Criteria**

### Code Implementation
- [ ] `dumpty/agents/base.py` created with `BaseAgent` abstract class
- [ ] `dumpty/agents/registry.py` created with `AgentRegistry` singleton
- [ ] All 8 agent implementations created in `dumpty/agents/*.py`
- [ ] Agents registered in `dumpty/agents/__init__.py`
- [ ] `Agent` enum updated to delegate to implementations
- [ ] `AgentDetector.detect_agents()` updated to use registry

### Testing
- [ ] >50 new tests added across test files
- [ ] All existing tests pass without modification (100%)
- [ ] New tests for: BaseAgent, AgentRegistry, all 8 agents, backward compatibility
- [ ] Test coverage >90% for new code
- [ ] Manual smoke tests pass (detection, CLI init, property access)

### Quality
- [ ] Code formatted with `black dumpty/ tests/`
- [ ] No linting errors: `ruff check dumpty/ tests/`
- [ ] All imports work correctly
- [ ] No circular import issues

### Documentation
- [ ] `ADDING_NEW_AGENTS.md` guide created in session folder
- [ ] Guide explains how to add new agents in <50 lines of code
- [ ] Documentation is clear and includes examples

### Backward Compatibility
- [ ] `Agent.COPILOT`, `Agent.CLAUDE`, etc. still accessible
- [ ] `agent.directory` and `agent.display_name` properties work
- [ ] `Agent.from_name()` and `Agent.all_names()` methods work
- [ ] `AgentDetector` public API unchanged
- [ ] CLI commands work identically (init, install, list, etc.)
- [ ] Zero breaking changes to existing consumer code

---

## **Verification Commands**

Run these commands to verify completion:

```bash
# Run all tests
pytest -v

# Run specific test suites
pytest tests/test_agents_base.py tests/test_agents_registry.py tests/test_agents_implementations.py -v
pytest tests/test_agent_detector.py -v

# Check coverage (target >90% for new code)
pytest --cov=dumpty.agents --cov-report=term-missing
pytest --cov=dumpty --cov-report=html

# Code quality
black dumpty/ tests/
ruff check dumpty/ tests/

# Manual smoke test
python -c "from dumpty.agent_detector import Agent; print(Agent.COPILOT.directory)"

# Test CLI still works
dumpty init --agent copilot
```

---

## **Expected Outcomes**

After completion:
- ✅ Adding new agents requires only ~30 lines in a single file
- ✅ All 8 existing agents migrated to new architecture
- ✅ Zero breaking changes to public API
- ✅ Test coverage >90%
- ✅ Clear documentation for contributors

---

## **Rollback Plan**

If critical issues found (see IMPLEMENTATION-PLAN.md Section 5):

```bash
# Revert main changes
git checkout main -- dumpty/agent_detector.py

# Remove new package
rm -rf dumpty/agents/

# Revert test changes
git checkout main -- tests/test_agent_detector.py

# Remove new test files
rm tests/test_agents_*.py

# Verify rollback
pytest -v
```

**Risk**: Low - changes are isolated and all existing tests verify original behavior.

---

## **Implementation Timeline**

Estimated: **4-6 hours** of focused work

See IMPLEMENTATION-PLAN.md Section 9 for detailed phase breakdown.

---

## **Priority:** Medium

**Target Branch:** `feature/agent-interface-refactoring`

---

## **Labels**
`enhancement` `refactoring` `architecture` `good-first-issue` (for adding future agents after merge)

---

## **Related Documents**
- Original design: [`docs/development/2025-11-01-initial-design/`](../2025-11-01-initial-design/)
- Ways of Working: [`docs/development/WAYS-OF-WORKING.md`](../WAYS-OF-WORKING.md)
