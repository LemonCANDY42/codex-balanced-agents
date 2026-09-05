# Repository maintenance

This repository ships two personal Codex role presets and a non-clobbering installer.

- `presets/quality/agents` and `presets/balanced/agents` own the installed role definitions. Keep their names, instructions and scope aligned; only documented model/effort choices may differ.
- `skills/codex-balanced-agents/SKILL.md` owns the lead's role-selection guidance. This root file is for contributors, never installed as a user's global AGENTS.md.
- `install.py` owns file installation, model catalogue checks and uninstall. Never add authentication handling, model inference, telemetry, automatic upgrades, or broad config replacement to installation.
- Installation asks at most two questions: preset and consolidated review/missing-model handling. No silent model substitution.
- Keep English and Chinese README/install guides synchronized. Keep claims scoped to recorded evidence; do not infer savings or task quality from reasoning effort alone.
- Never copy a developer's home configuration, credentials, private paths, MCP inventory, session logs or project instructions into this repository.
- Use targeted temporary-directory tests for the installer. Run `python3 -m unittest discover -s tests -v` before publishing changes. Live model tests are separate from offline tests and should have bounded synthetic prompts.
- Use an independent read-only review after non-trivial installer or role-boundary changes. Reviewers do not edit or delegate; the lead owns follow-up and acceptance.
