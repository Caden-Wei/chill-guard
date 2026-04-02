# Contributing

## Scope

This project is currently focused on the macOS desktop build only. Changes that add other platforms should be discussed in an issue before implementation.

## Before you open a pull request

1. Keep the scope narrow.
2. Explain the user-facing problem you are fixing.
3. Avoid mixing packaging churn with functional changes unless they are directly related.
4. Do not commit local build output, `dist/`, `build/`, `.venv/`, or log files.

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Validation

At minimum, run:

```bash
python -m py_compile chill_guard_app.py
```

If you changed packaging behavior, also rebuild the app:

```bash
./packaging/build_macos_release.sh
```

## Coding guidelines

- Keep macOS-specific behavior explicit instead of hiding it behind vague helper names.
- Preserve existing user settings when possible.
- Avoid adding new heavyweight dependencies unless there is a clear need.
- Update the README or install guide when user-visible behavior changes.

## Pull request checklist

- Describe the root cause
- Describe the fix
- List the checks you ran
- Mention any remaining macOS-specific, packaging, or permission-related risk
