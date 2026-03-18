Read the skill definition at `.claude/skills/orca-setup/SKILL.md` and follow its instructions exactly.

The user wants to set up their project. The skill contains the full setup process with 15 workflows (task-management, linter, type-checker, CI, tests, etc.).

If the user provided arguments like `setup-linter` or `setup-all`, pass them through as described in the skill's Invocation section. If no arguments, show the status overview.

Arguments: $ARGUMENTS
