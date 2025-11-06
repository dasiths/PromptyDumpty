# Ways of Working with AI Agents

This document outlines the structured approach for development sessions with AI coding agents in this project.

- [Ways of Working with AI Agents](#ways-of-working-with-ai-agents)
  - [Overview](#overview)
  - [The Three-Phase Workflow](#the-three-phase-workflow)
    - [Phase 1: Explore](#phase-1-explore)
    - [Phase 2: Define](#phase-2-define)
    - [Phase 3: Execute](#phase-3-execute)
  - [Document Organization](#document-organization)
    - [Document Templates](#document-templates)
  - [Principles](#principles)
    - [1. Phase Discipline](#1-phase-discipline)
    - [2. Documentation as Communication](#2-documentation-as-communication)
    - [3. Iterative Refinement](#3-iterative-refinement)
    - [4. Collaborative Intelligence](#4-collaborative-intelligence)
  - [Usage Guidelines](#usage-guidelines)
    - [Starting a New Feature](#starting-a-new-feature)
    - [Resuming Work](#resuming-work)
    - [Working with AI Agents](#working-with-ai-agents)
  - [Benefits](#benefits)


## Overview

Development work is organized into deliberate phases that ensure thorough understanding before implementation. Each phase builds on the previous one, creating a traceable decision trail and comprehensive documentation.

## The Three-Phase Workflow

### Phase 1: Explore

**Purpose**: Discover, investigate, and understand the problem space.

**Activities**:
- Research and fact-finding about the issue or problem
- Assess feasibility of various implementation directions
- Identify grey areas requiring clarification
- Probe assumptions and scrutinize constraints
- Investigate technical trade-offs and implications

**Artifacts**:
- `REQUIREMENTS.md` - Captures the problem statement and desired outcomes
- `FEASIBILITY.md` - Documents research findings and technical considerations

**Outcome**: Shared understanding of the problem space and viable solution directions.

---

### Phase 2: Define

**Purpose**: Establish clear specifications based on exploration findings.

**Activities**:
- Define what needs to be built
- Create specifications and success criteria
- Make intentional scoping decisions
- Document architectural choices
- Establish acceptance criteria

**Artifacts**:
- Updated `REQUIREMENTS.md` with refined specifications
- `PRD.md` - Product Requirements Document (when applicable)
- `SPEC.md` - Technical specifications and design details
- Design documents with clear boundaries and constraints
- Success criteria and validation approach

**Outcome**: Unambiguous specification ready for implementation.

---

### Phase 3: Execute

**Purpose**: Build the solution according to defined specifications.

**Activities**:
- Create detailed implementation plans
- Break work into actionable tasks
- Generate tracking artifacts (GitHub issues, task lists)
- Implement features per specification
- Validate against success criteria from Phase 2

**Artifacts**:
- `IMPLEMENTATION-PLAN.md` - Step-by-step execution roadmap
- `GITHUB-ISSUE.md` - Formal work tracking that can be assigned to GitHub Copilot's coding agent to automatically create PRs (see [GitHub Copilot agent workflow](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-a-pr))
- Code changes and tests
- Progress documentation

**Outcome**: Fully implemented and validated feature.

**Leveraging GitHub Copilot Coding Agent**:

Phase 3 is where you can leverage GitHub Copilot's autonomous coding agent to handle implementation:

1. **Prepare the issue**:
   - Write a concise issue description with the key objective
   - Reference the development session folder (e.g., `docs/development/YYYY-MM-DD-feature-name/`)
   - Point to specific artifacts: `REQUIREMENTS.md`, `IMPLEMENTATION-PLAN.md`, etc.
   - Copilot can read these files from the repo - no need to duplicate content in the issue

2. **Create and assign the GitHub issue**:
   - Create the issue on GitHub referencing your documentation artifacts
   - Assign the issue to Copilot from the Assignees dropdown
   - Add optional instructions in the prompt field for specific guidance
   - Select the appropriate base branch if not using the default
   - Consider using custom agents if you have specialized requirements

3. **Monitor and guide**:
   - Copilot will create a draft PR and begin working
   - Watch for the PR notification and review its initial approach
   - Add comments to the PR (not the issue) if adjustments are needed
   - Copilot will iteratively push changes as it implements the solution

4. **Review and validate**:
   - When Copilot adds you as a reviewer, thoroughly review the PR
   - Validate against the success criteria from Phase 2
   - Request changes if needed
   - Merge when the implementation meets specifications

**Benefits of this approach**:
- Documented context ensures Copilot has full understanding
- Human defines "what" and "why" (Phases 1-2), agent handles "how" (Phase 3)
- Specifications serve as validation criteria for PR review
- Traceability from requirements through to implementation

---

## Document Organization

Development sessions are organized in dated folders i.e.:
```
docs/development/
  YYYY-MM-DD-feature-name/
    REQUIREMENTS.md
    FEASIBILITY.md (optional)
    PRD.md (optional)
    SPEC.md (optional)
    IMPLEMENTATION-PLAN.md
    GITHUB-ISSUE.md (optional)
```

This structure:
- Captures the chronological evolution of the project
- Provides context for future AI agents joining development
- Creates an audit trail of decisions and rationale
- Enables quick onboarding and context recovery

### Document Templates

Templates for each document type are available in [templates/](./templates/):
- [REQUIREMENTS.md](./templates/REQUIREMENTS.md) - Problem statement and requirements
- [FEASIBILITY.md](./templates/FEASIBILITY.md) - Technical feasibility analysis
- [PRD.md](./templates/PRD.md) - Product requirements document
- [SPEC.md](./templates/SPEC.md) - Technical specifications
- [IMPLEMENTATION-PLAN.md](./templates/IMPLEMENTATION-PLAN.md) - Implementation roadmap
- [GITHUB-ISSUE.md](./templates/GITHUB-ISSUE.md) - Issue for GitHub Copilot agent

These templates are **intentionally flexible** - use what's helpful, skip what isn't. See [templates/README.md](./templates/README.md) for usage guidance.

## Principles

### 1. Phase Discipline
Don't skip phases. Each phase has distinct value:
- Explore prevents building the wrong thing
- Define prevents building it the wrong way
- Execute ensures quality implementation

### 2. Documentation as Communication
Documents serve as the primary communication interface between human and AI agents across sessions. They:
- Align understanding between human and AI
- Enable new AI agents to pick up work mid-stream
- Preserve context that would otherwise be lost

### 3. Iterative Refinement
Documents evolve through phases:
- Start with rough understanding
- Refine through exploration
- Crystallize in definition
- Reference during execution

### 4. Collaborative Intelligence
The human and AI work as partners:
- Human provides vision, priorities, and judgment
- AI provides research, analysis, and implementation
- Both challenge assumptions and validate decisions

## Usage Guidelines

### Starting a New Feature

1. Create a dated folder: `YYYY-MM-DD-feature-name/`
2. Begin with Phase 1: Create `REQUIREMENTS.md`
3. Explore thoroughly before moving to Phase 2
4. Only proceed to Phase 3 when specifications are clear

### Resuming Work

1. Review artifacts from previous phases
2. Reference specifications during implementation
3. Update documents if new insights emerge
4. Maintain traceability to original requirements

### Working with AI Agents

- **Be explicit** about which phase you're in
- **Reference documents** to ground discussions
- **Challenge and probe** during Explore phase
- **Demand clarity** during Define phase
- **Validate against specs** during Execute phase

## Benefits

This structured approach provides:

- **Reduced rework**: Thorough exploration prevents wrong turns
- **Better solutions**: Multiple perspectives considered before committing
- **Faster onboarding**: New agents can read context vs. being told
- **Quality assurance**: Clear specs enable validation
- **Knowledge retention**: Decisions and rationale preserved
- **Audit trail**: Complete history of how and why decisions were made

---

*This is a living document. Update it as the workflow evolves and improves.*
