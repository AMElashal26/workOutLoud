"""Utilities for describing branching automation workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional
import sys

if sys.version_info >= (3, 11):
    import tomllib  # type: ignore[attr-defined]
else:  # pragma: no cover - fallback for Python < 3.11
    import tomli as tomllib  # type: ignore[assignment]


@dataclass
class AutomationStep:
    """A single actionable unit within an automation workflow."""

    key: str
    description: str
    outcomes: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def next_step(self, outcome: str) -> Optional[str]:
        """Return the key for the next step given an outcome label."""

        return self.outcomes.get(outcome)


class Workflow:
    """A branching workflow composed of linked :class:`AutomationStep` objects."""

    def __init__(self, steps: Mapping[str, AutomationStep], start_step: str) -> None:
        if start_step not in steps:
            raise ValueError(f"Start step '{start_step}' is not defined in the workflow")
        self._steps: Dict[str, AutomationStep] = dict(steps)
        self._start_step = start_step

    @property
    def start_step(self) -> AutomationStep:
        """Return the starting step for the workflow."""

        return self._steps[self._start_step]

    def get_step(self, key: str) -> AutomationStep:
        """Retrieve a step by its key."""

        try:
            return self._steps[key]
        except KeyError as exc:  # pragma: no cover - defensive programming
            raise KeyError(f"Step '{key}' does not exist in the workflow") from exc

    def traverse(self, outcomes: Iterable[str]) -> List[AutomationStep]:
        """Follow a series of outcomes and return the visited steps."""

        path: List[AutomationStep] = [self.start_step]
        current = self.start_step
        for outcome in outcomes:
            next_key = current.next_step(outcome)
            if next_key is None:
                raise ValueError(
                    f"Outcome '{outcome}' is not valid for step '{current.key}'"
                )
            current = self.get_step(next_key)
            path.append(current)
        return path

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "Workflow":
        """Create a workflow from a dictionary structure."""

        steps_section = data.get("steps")
        if not isinstance(steps_section, Mapping):
            raise ValueError("Workflow definition requires a 'steps' mapping")
        start_key = data.get("start")
        if not isinstance(start_key, str):
            raise ValueError("Workflow definition requires a 'start' string key")

        steps: Dict[str, AutomationStep] = {}
        for key, raw_step in steps_section.items():
            if not isinstance(raw_step, MutableMapping):
                raise ValueError(f"Step '{key}' must be a mapping of properties")
            description = raw_step.get("description")
            if not isinstance(description, str):
                raise ValueError(f"Step '{key}' requires a string description")
            outcomes = raw_step.get("outcomes", {})
            if not isinstance(outcomes, Mapping):
                raise ValueError(f"Step '{key}' outcomes must be a mapping")
            metadata = raw_step.get("metadata", {})
            if not isinstance(metadata, Mapping):
                raise ValueError(f"Step '{key}' metadata must be a mapping")
            steps[key] = AutomationStep(
                key=key,
                description=description,
                outcomes=dict(outcomes),
                metadata=dict(metadata),
            )

        return cls(steps=steps, start_step=start_key)

    @classmethod
    def from_toml(cls, path: Path) -> "Workflow":
        """Load a workflow definition from a TOML file."""

        data = tomllib.loads(path.read_text())
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, object]:
        """Serialise the workflow into a dictionary."""

        return {
            "start": self.start_step.key,
            "steps": {
                key: {
                    "description": step.description,
                    "outcomes": dict(step.outcomes),
                    "metadata": dict(step.metadata),
                }
                for key, step in self._steps.items()
            },
        }


__all__ = ["AutomationStep", "Workflow"]
