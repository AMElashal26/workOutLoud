import unittest
from pathlib import Path

from wol.workflow import Workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow_path = Path(__file__).resolve().parents[1] / "automation" / "workflow.toml"
        self.workflow = Workflow.from_toml(self.workflow_path)

    def test_start_step(self) -> None:
        self.assertEqual(self.workflow.start_step.key, "capture_idea")
        self.assertIn("outline_scope", self.workflow.get_step("capture_idea").outcomes.values())

    def test_traverse_primary_path(self) -> None:
        outcomes = ["ready", "approved", "published", "logged"]
        path = self.workflow.traverse(outcomes)
        self.assertEqual([step.key for step in path], [
            "capture_idea",
            "outline_scope",
            "create_showcase",
            "submit_updates",
            "retrospective",
        ])

    def test_invalid_outcome_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.workflow.traverse(["invalid"])


if __name__ == "__main__":
    unittest.main()
