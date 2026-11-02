# Ascend Interface Docs Skill

OpenCode skill for writing and reviewing Ascend TLA/TileLang interface documentation.

## Install

```bash
mkdir -p ~/.config/opencode/skills
git clone git@github.com:aka-adi/ascend-interface-docs.git \
  ~/.config/opencode/skills/ascend-interface-docs
```

Restart opencode after cloning.

## Contents

- `SKILL.md`: workflow and rules
- `reference/`: templates, AVE TD guidance, Sphinx workflow, pitfalls
- `scripts/`: API extraction, docstring checks, preview build/stop helpers

## Scripts

```bash
python3 scripts/extract_api.py path/to/file.py --names vadd,vsub
python3 scripts/check_docstrings.py path/to/file.py --names vadd,vsub --strict
python3 scripts/build_preview.sh --serve
python3 scripts/stop_preview.sh
```

## Scope

The skill is portable: it uses environment variables such as `REPO_ROOT`, `CANN_ROOT`, `PYTHON`, `DOCS_DIR`, and `PREVIEW_DIR` instead of machine-specific paths.
