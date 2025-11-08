# workOutLoud

An automation/workflow toolkit to write and keep track of projects as they are added for resume, LinkedIn, and related showcases.

## Branching automation workflow

The repository ships with a reusable branching workflow definition stored in [`automation/workflow.toml`](automation/workflow.toml). It captures the key decisions and follow-up actions required to turn a project idea into a published showcase and retrospective.

You can load and navigate the workflow with the `wol.workflow` module:

```python
from pathlib import Path
from wol.workflow import Workflow

workflow = Workflow.from_toml(Path("automation/workflow.toml"))

# follow the happy path for a new project idea
path = workflow.traverse(["ready", "approved", "published", "logged"])
print([step.key for step in path])
```

The module exposes structured `AutomationStep` objects so you can build automation or reporting tooling around each decision point, integrate with checklists, or layer on notifications.

## Running tests

The project includes a small `unittest` suite that validates the workflow definition. Run it with:

```bash
python -m unittest discover
```
