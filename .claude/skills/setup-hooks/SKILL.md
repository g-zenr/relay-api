---
name: setup-hooks
description: Configure Claude Code hooks for automated validation on file edits and commits
disable-model-invocation: true
---

Set up Claude Code hooks for the Relay API project.

Hooks enforce coding standards automatically — they run scripts at specific points in Claude's workflow. Unlike CLAUDE.md instructions (advisory), hooks are deterministic and guarantee the action happens.

## Hook 1 — Python Syntax Check After File Edits
**Event:** `PostToolUse` on `Write` and `Edit` tools
**Purpose:** Catch syntax errors immediately after writing/editing Python files
**Command:** Parse the edited file with `python -c "import ast; ast.parse(open('$CLAUDE_FILE_PATH').read())"` — fails if syntax is broken

## Hook 2 — Future Annotations Check After File Edits
**Event:** `PostToolUse` on `Write` and `Edit` tools
**Purpose:** Enforce `from __future__ import annotations` in every `.py` file under `app/`
**Command:** Check if the file is under `app/` and is `.py`, then verify the import exists

## Hook 3 — Tests After File Edits
**Event:** `PostToolUse` on `Write` and `Edit` tools
**Purpose:** Run tests after modifying source or test files to catch regressions immediately
**Command:** `python -m pytest tests/ -v --tb=short -q`
**Note:** Only trigger on `.py` file edits, not README or config files

## Installation

Write the hooks to `.claude/settings.json` using this structure:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "<shell command here>"
          }
        ]
      }
    ]
  }
}
```

## Important Notes
- Test each hook manually before adding to settings
- Hooks that exit non-zero BLOCK the operation and show the error to the user
- Keep hooks fast (< 5 seconds) — slow hooks degrade the coding experience
- Use `.claude/settings.json` for project hooks (shared via git)
- Use `.claude/settings.local.json` for personal hooks (gitignored)
- See https://code.claude.com/docs/en/hooks for full documentation

## Verification
After setup, test by editing a file and confirming the hook runs:
1. Edit any `.py` file in `app/`
2. Verify the hook output appears
3. Intentionally break something to confirm the hook blocks the operation
