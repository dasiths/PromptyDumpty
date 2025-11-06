# Document Templates

This folder contains templates for the structured development workflow documented in [WAYS-OF-WORKING.md](../WAYS-OF-WORKING.md).

## Available Templates

### Phase 1: Explore

- **[REQUIREMENTS.md](./REQUIREMENTS.md)** - Capture problem statement, goals, user stories, and functional requirements
- **[FEASIBILITY.md](./FEASIBILITY.md)** - Analyze technical feasibility, compare approaches, assess risks

### Phase 2: Define

- **[PRD.md](./PRD.md)** - Product Requirements Document (when applicable)
- **[SPEC.md](./SPEC.md)** - Technical specifications and design details (when applicable)

### Phase 3: Execute

- **[IMPLEMENTATION-PLAN.md](./IMPLEMENTATION-PLAN.md)** - Detailed implementation roadmap
- **[GITHUB-ISSUE.md](./GITHUB-ISSUE.md)** - Issue template for assignment to GitHub Copilot coding agent

## Usage

### Starting a New Development Session

1. **Create a dated folder:**
   ```bash
   mkdir docs/development/YYYY-MM-DD-feature-name
   cd docs/development/YYYY-MM-DD-feature-name
   ```

2. **Copy relevant templates:**
   ```bash
   # Phase 1: Always start with requirements
   cp ../templates/REQUIREMENTS.md ./
   
   # If technical feasibility needs analysis
   cp ../templates/FEASIBILITY.md ./
   
   # Phase 2: If formal specs needed
   cp ../templates/PRD.md ./
   cp ../templates/SPEC.md ./
   
   # Phase 3: When ready to implement
   cp ../templates/IMPLEMENTATION-PLAN.md ./
   cp ../templates/GITHUB-ISSUE.md ./
   ```

3. **Fill in the templates** as you work through each phase

## Template Philosophy

These templates are intentionally **high-level and flexible**:

- **Not all sections are required** - Remove what doesn't apply
- **Add sections as needed** - These are starting points, not rigid structures
- **Adapt to context** - Simple features may need simpler docs
- **Focus on value** - Document what helps, skip what doesn't

## When to Use Which Template

| Template | Use When | Skip When |
|----------|----------|-----------|
| REQUIREMENTS.md | Always (starting point) | Never - this grounds everything |
| FEASIBILITY.md | Multiple approaches to evaluate | Approach is obvious/well-known |
| PRD.md | User-facing features with UX considerations | Pure technical/internal work |
| SPEC.md | Complex technical design needed | Implementation is straightforward |
| IMPLEMENTATION-PLAN.md | Always (for execute phase) | Never - guides implementation |
| GITHUB-ISSUE.md | Assigning to Copilot agent | Implementing manually without agent |

## Customization

Feel free to:
- Add project-specific sections
- Remove sections that don't apply
- Combine documents (e.g., merge REQUIREMENTS and FEASIBILITY for simple features)
- Create additional templates for your specific needs

## Examples

See existing development sessions for examples:
- [2025-11-01-initial-design/](../2025-11-01-initial-design/) - Initial project setup
- [2025-11-04-improvements/](../2025-11-04-improvements/) - Adding missing features
- [2025-11-04-show-command/](../2025-11-04-show-command/) - Single command implementation
