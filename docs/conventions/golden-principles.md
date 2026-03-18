# Golden Principles

These are the foundational conventions for this repository. When forking this template, replace these with principles specific to your project's language, framework, and team practices.

The principles below are **language-agnostic defaults** — a starting point, not a final answer.

---

### Principle 1: CLAUDE.md Is a Map, Not a Manual

**Rule:** Keep the instruction file under 120 lines. It indexes deeper docs — it doesn't contain them.

**Why:** Agents have limited context windows. A bloated instruction file pushes out the actual code and conversation, reducing agent effectiveness. Short maps are also easier for humans to review and maintain.

**Enforcement:** `harness-audit` checks line count; `harness-maintain` flags drift.

**Bad:**
```markdown
# CLAUDE.md
[400 lines of detailed coding standards, architecture diagrams,
API docs, and deployment procedures all in one file]
```

**Good:**
```markdown
# CLAUDE.md
## Key Conventions
- See `docs/conventions/golden-principles.md` for full details
```

---

### Principle 2: Enforce Conventions Mechanically

**Rule:** Every convention that can be checked by a linter, formatter, hook, or CI job must be. Never rely on agents "knowing" a rule — make violations fail loudly.

**Why:** Agents don't reliably follow prose instructions. Mechanical enforcement catches mistakes before they reach review, saving significant cleanup time.

**Enforcement:** Pre-commit hooks, CI pipelines, linter configs.

**Bad:**
```markdown
# CLAUDE.md
Please remember to format code with prettier before committing.
```

**Good:**
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/mirrors-prettier
  hooks:
    - id: prettier
```

---

### Principle 3: All Knowledge Lives in the Repo

**Rule:** If an agent needs to know it, it must be in a versioned file in this repository. Not in a wiki, not in Slack, not in someone's head.

**Why:** Agents can only read what's in front of them. External knowledge doesn't exist to an agent. Co-located, versioned docs also stay in sync with the code they describe.

**Enforcement:** Manual review; `harness-maintain` drift scanning.

**Bad:**
```
See the team wiki for deployment procedures.
Check Slack #dev channel for the latest API conventions.
```

**Good:**
```
See docs/guides/deployment.md for deployment procedures.
See docs/conventions/api-standards.md for API conventions.
```

---

### Principle 4: One Responsibility per File

**Rule:** Each file should have a single clear purpose. When a file exceeds ~300 lines or handles multiple concerns, split it.

**Why:** Agents work better with focused files. Large multi-purpose files cause agents to miss context, make incorrect assumptions about scope, and produce changes with unintended side effects.

**Enforcement:** Linter rules for file length (configure per language).

**Bad:**
```
src/utils.py  # 800 lines: logging, HTTP helpers, string parsing,
              # date formatting, and database connection pooling
```

**Good:**
```
src/logging.py         # Structured logging setup
src/http_client.py     # HTTP helper functions
src/parsing.py         # String parsing utilities
```

---

### Principle 5: Validate at Boundaries, Trust Internally

**Rule:** Parse and validate data at system boundaries (user input, API responses, file reads). Internal function calls between trusted modules don't need redundant validation.

**Why:** Defensive coding everywhere creates noise that obscures real logic. Agents add excessive validation when they see it modeled. Boundary validation is where bugs actually occur.

**Enforcement:** Code review; consider linter rules for common patterns.

**Bad:**
```python
def calculate_total(items):
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not all(isinstance(i, dict) for i in items):
        raise TypeError("each item must be a dict")
    # ... 10 more type checks before actual logic
```

**Good:**
```python
def calculate_total(items: list[OrderItem]) -> Decimal:
    """Items are already validated at the API boundary."""
    return sum(item.price * item.quantity for item in items)
```

---

### Principle 6: Document Decisions, Not Descriptions

**Rule:** Use ADRs in `docs/architecture/` for significant decisions. Don't document what the code does — document *why* it does it that way.

**Why:** Agents can read code to understand what it does. They can't infer why a particular approach was chosen over alternatives. ADRs prevent agents from "improving" code by reverting intentional decisions.

**Enforcement:** Manual review; check that `docs/architecture/` receives updates when architecture changes.

**Bad:**
```markdown
# The UserService class handles user operations including
# creating users, updating users, and deleting users.
# It uses the UserRepository for database access.
```

**Good:**
```markdown
# ADR-003: Use repository pattern for database access
# We chose the repository pattern over active record because...
```

---

### Principle 7: No Implementation Without Feedback Plan

**Rule:** Every feature must have a feedback loop plan (tests + observability) before any code is written.

**Why:** Retrofitting tests after implementation leads to tests that verify behavior rather than specify it. Agents take shortcuts when feedback loops are undefined, producing code that cannot be validated.

**Enforcement:** Planning Agent blocks Design Feedback Loop transition until feedback_completeness_score >= 6.

**Bad:**
```
# Write code first, then add tests
src/auth/login.py    # implemented without any test plan
tests/test_login.py  # written after the fact to match behavior
```

**Good:**
```
docs/feedback-loops/{issue.identifier}-feedback.md  # created at Planning stage
# Contains: test scenarios, observability hooks, acceptance criteria
# Design Feedback Loop Agent writes fail-first tests from this doc
```

---

### Principle 8: One Issue = One Conceptual Change

**Rule:** Each issue must have a scope_score <= 6. Issues scoring higher must be decomposed into sub-issues before work begins.

**Why:** Oversized issues cause agents to make architectural decisions that should be explicit. Decomposed issues produce smaller, reviewable changesets and clearer audit trails.

**Enforcement:** Scoping Agent calculates scope_score; Scoping Agent writes `.orca/decomposition.json`; orchestrator creates sub-issues and blocking relations.

**Bad:**
```
Issue: "Build the entire auth system"
# Touches user model, sessions, middleware, endpoints, tests, and docs
# Scope score: 14 — too large for one agent run
```

**Good:**
```
Issue: "Add user model"          # scope_score: 3
Issue: "Add auth middleware"     # scope_score: 4
Issue: "Add login endpoint"      # scope_score: 5
```

---

### Principle 9: Docs Are Mandatory Deliverables

**Rule:** Every implementation must update all affected documentation. PR creation is blocked until doc validation returns PASS.

**Why:** Documentation drift makes agents unreliable over time. Agents working from stale docs make incorrect assumptions, compounding errors across issues.

**Enforcement:** Docs Agent runs validate-docs skill; PR creation blocked until PASS.

**Bad:**
```
PR: "Add login endpoint"
# 12 files changed in src/
# 0 files changed in docs/
# Docs Agent skipped "no docs needed"
```

**Good:**
```
PR: "Add login endpoint"
# Code changes in src/
# docs/agents/implementation.md updated with new endpoint
# Doc impact checklist completed, validation PASS
```

---

### Principle 10: Tests Before Implementation (TDD)

**Rule:** Design Feedback Loop Agent writes fail-first test scaffolds before Implementation Agent writes any code. Implementation Agent cannot modify test assertions.

**Why:** Tests written after implementation verify behavior rather than specify requirements. Fail-first tests force explicit thinking about what success looks like before solving the problem.

**Enforcement:** Design Feedback Loop Agent verifies tests FAIL before transitioning to Implementing state; Implementation Agent role prompt includes explicit constraint against modifying test assertions.

**Bad:**
```
# Implementation Agent writes code, then writes matching tests
src/login.py         # implemented first
tests/test_login.py  # written after to match the implementation
```

**Good:**
```
# Design Feedback Loop Agent commits failing tests; Implementation Agent makes them pass
tests/test_login.py  # FAILING — committed by Design Feedback Loop Agent
src/login.py         # not yet created — Implementation Agent's job
```

---

### Principle 11: Agent Separation of Concerns

**Rule:** Each agent role has hard constraints on what it can and cannot modify. Violations are treated as failures, not shortcuts.

**Why:** Without hard constraints, agents take shortcuts — Implementation Agents update docs to avoid failing validation, Design Feedback Loop Agents skip ahead to implementation. Constraints prevent compounding errors and maintain audit trails.

**Enforcement:** Role prompts include explicit "Do NOT" constraints; validation catches violations.

**Bad:**
```
# Implementation Agent also updates docs and modifies test expectations
# to avoid failing validation — saves time but destroys audit trail
```

**Good:**
```
Scoping Agent:       modifies docs/plans/{issue.identifier}-scope.md only
Design Feedback Loop Agent:        modifies test files only
Implementation Agent: modifies src/ files only
Validation Agent:    pushes branch, creates draft PR, polls CI, writes .orca/validation-report.md — does NOT modify code or run checks locally
Docs Agent:          modifies docs/ files, finalizes draft PR for review
```

---

### Principle 12: Canonical Artifact Paths

**Rule:** Agents communicate via files at predefined paths using `{issue.identifier}` as the namespace. No ad-hoc file locations.

**Why:** When artifact paths are unpredictable, downstream agents cannot reliably find upstream work. Canonical paths make agent handoffs deterministic and auditable.

**Enforcement:** Role prompts specify exact artifact paths; skills validate paths before reading.

**Bad:**
```
# Scoping Agent saves to: notes/my-analysis.md
# Planning Agent looks for: docs/scope-analysis.txt
# Result: Planning Agent cannot find scoping output
```

**Good:**
```
docs/plans/{issue.identifier}-scope.md           # Scoping Agent output
docs/plans/{issue.identifier}-plan.md            # Planning Agent output
docs/feedback-loops/{issue.identifier}-feedback.md  # Planning Agent feedback loop
```

---

## Adding New Principles

When forking this template:

1. Start with 5–7 principles specific to your stack
2. Each principle must address a real pain point you've observed
3. Every principle needs a concrete enforcement mechanism
4. Review and update quarterly using `harness-maintain`
