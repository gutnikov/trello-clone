---
name: logging
description: Configure structured logging and optional metrics
dependencies: [package-management]
docs:
  - docs/agents/implementation.md
---

# Setup: Structured Logging & Metrics

Structured logging is required — agents need machine-readable logs to diagnose issues during validation. Metrics are optional.

## Detect

Check for existing structured logging setup:

- Structured logging libraries: `structlog`, `pino`, `slog`, `log/slog`
- Logging config in application code (look for JSON formatters, structured output)
- Check if the app already writes structured (JSON) logs to stdout

Also check for metrics libraries (optional): prometheus client, statsd, opentelemetry.

Report "configured" if structured logging is already producing JSON output. Report "not configured" otherwise.

## Propose

| Language | Logging Library | Why |
|----------|----------------|-----|
| Python | structlog or stdlib with JSON formatter | Structured, machine-readable |
| TypeScript/JS | pino | Fast, structured JSON logging |
| Go | log/slog | Stdlib, structured |
| Rust | tracing + tracing-subscriber | Industry standard, JSON layer available |

The key requirement is that logs are:
1. **Structured** — JSON format, not free-text
2. **Written to stdout** — so agents and CI can capture them
3. **Include context fields** — request IDs, operation names, durations, error details

Metrics: note as optional, skip unless user specifically requests.

Present the proposal and wait for approval.

## Configure

1. Install the structured logging library
2. Configure a JSON formatter that writes to stdout
3. Set up a base logger configuration that all application code can use
4. Ensure log levels are sensible (INFO for business events, WARN for recoverable errors, ERROR for failures)

Example for Python (structlog):
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

## Verify

1. Start the app (or import the logging module in a test script)
2. Trigger a log event
3. Confirm output is valid JSON with timestamp, level, and message fields
4. Confirm output goes to stdout

Log output must be parseable JSON — not plain text.

## Docs Update

Update `docs/agents/implementation.md` — add logging setup to the Coding Conventions `<!-- CUSTOMIZE -->` section:

```markdown
### Logging
- Library: <logging library>
- Config: `<config location>`
- Import: `<exact import/setup pattern>`
- Format: JSON to stdout
```

If staging is configured, also note how to access staging logs:

```markdown
### Staging Logs
- `<command or URL to access staging logs>`
```

## Definition of Done

- [ ] Structured logging library is installed
- [ ] Logger config produces valid JSON output to stdout
- [ ] A log event can be triggered and output is parseable JSON
- [ ] `docs/agents/implementation.md` has logging setup info
