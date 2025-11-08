# workOutLoud

Automation/workflow to write and keep track of projects as they are added for resume, linkedin, etc.

## Branching automation

The `automation` package provides utilities for standardising how project branches are created and managed. Use the CLI to create feature branches, merge them back to the main line, and clean up afterwards.

```bash
python -m automation.cli create feature/my-project --base main
python -m automation.cli list
python -m automation.cli merge feature/my-project main
python -m automation.cli delete feature/my-project
```

### Installing test dependencies

```bash
pip install -e .[dev]
```

### Running tests

```bash
pytest
```
