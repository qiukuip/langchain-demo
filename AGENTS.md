# Repository Guidelines

## Project Structure & Module Organization

This repository contains standalone LangChain/LangGraph examples organized by topic in numbered directories from `00_overview/` through `14_long_term_memory/`. Filenames such as `01_build_base_agent.py` indicate example order. MCP servers are in `11_mcp/servers/`; a sample skill is in `08-skills/skills/`. There is no shared application package or centralized test directory. Add examples to the relevant topic directory and follow its numbering and naming pattern.

## Build, Test, and Development Commands

There is no repository-wide build or test command. Use Python 3.10+ and install the example's dependencies as described in `README.md`. Run scripts from the repository root so relative paths and `.env` loading work:

```bash
python 00_overview/01_create_an_agent.py
python 14_mcp/servers/math_server.py
```

Examples may call live model APIs or services; configure required keys and optional services first. PostgreSQL, MCP, and DeepAgents dependencies are needed only by examples that use them.

## Coding Style & Naming Conventions

Follow neighboring examples: four-space indentation, `snake_case` filenames and identifiers, and descriptive feature names. Keep each script focused on one concept, comment non-obvious setup, and reuse existing LangChain/LangGraph patterns.

## Testing Guidelines

No automated test framework or coverage requirement is configured. Run a changed example when dependencies and credentials are available; confirm documented setup matches the code. For prose changes, review Markdown and links. Some examples require API keys or services.

## Commit & Pull Request Guidelines

Recent commits use short imperative summaries, often with emoji prefixes (for example, `♻️ refactor code`); Chinese summaries also appear. Keep commits focused. Pull requests should describe the example or behavior, required configuration, and related issues; include output or screenshots when useful.

## Security & Configuration

Keep API keys, passwords, and personal configuration in an untracked `.env`; never commit secrets or real user data. Use placeholders in `.env.example` for new variables.

## Middleware Example Troubleshooting

`09-part-middleware/06_human_in_the_loop_middleware.py` pauses for email approval; without interactive input it safely rejects the pending send. Resume HITL with `Command(resume={"decisions": [decision]})`. Keep the `Email` schema aligned with the model's `subject`, `body`, and `recipient` tool arguments. When running offline, disable LangSmith tracing to avoid connection warnings.
