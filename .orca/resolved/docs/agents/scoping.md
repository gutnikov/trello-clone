# Scoping Agent Context

## Project Architecture

<!-- CUSTOMIZE: architecture-overview -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

This is a template repository. Replace this section with your project's architecture overview.

### Subsystems

<!-- CUSTOMIZE: subsystems -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

### Boundary Rules

<!-- CUSTOMIZE: boundary-rules -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## Scope Score Adjustments

The default scope_score formula (defined in the scope-analysis skill) uses:
- Files affected: 1-3 = 1pt, 4-7 = 2pt, 8+ = 3pt
- Subsystems crossed: 1 = 0pt, 2 = 1pt, 3+ = 2pt
- Estimated LOC: < 100 = 0pt, 100-300 = 1pt, 300+ = 2pt
- Migration needed: +2pt
- API surface change: +1pt

<!-- CUSTOMIZE: scope-thresholds -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

## Decomposition Preferences

<!-- CUSTOMIZE: decomposition-strategy -->
*Populated by `/orca` setup workflows. Run `/orca` to configure.*
<!-- END CUSTOMIZE -->

When decomposing, write `.orca/decomposition.json` — the orchestrator creates sub-issues in Scoping state and sets blocking relations automatically. Each sub-issue should:
1. Have a clear, specific title
2. Reference the parent issue in the description
3. Include the scope_score and affected files in the description
4. Be independently implementable and testable
5. Use `key` and `depends_on` fields to express dependency ordering between siblings
