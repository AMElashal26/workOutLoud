# workOutLoud

automation/workflow to write and keep track of projects as they are added for resume, linkedin, etc

## Branch automation

Use the helper script in `scripts/branch_automation.sh` to generate consistent branch names and ensure you are branching from an up-to-date base branch.

### Requirements
- Bash 4+
- Git installed and configured for the repository

### Usage
```bash
./scripts/branch_automation.sh \
  --project "portfolio" \
  --description "add-api-for-new-metrics" \
  --type feature \
  --ticket 1234
```

#### Options
- `--project` *(required)*: Logical project or workstream name.
- `--description` *(required)*: Short summary of the change.
- `--type`: Type of work (defaults to `feature`).
- `--ticket`: Optional external ticket or issue identifier.
- `--base`: Base branch to branch from (defaults to `main`).
- `--dry-run`: Output the generated branch name without creating it.

The script validates that the working tree is clean, fetches the base branch when available, and creates a new branch following the pattern `<type>/<project>-<ticket?>-<description>`.
