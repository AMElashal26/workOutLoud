"""Branch management utilities for automating project workflows.

This module provides a high-level interface for creating, switching, and
merging git branches. The goal is to make it easy to standardise the branching
workflow for resume and portfolio projects without requiring deep git
knowledge.
"""
from __future__ import annotations

from dataclasses import dataclass
import subprocess
from typing import Iterable, List


class GitCommandError(RuntimeError):
    """Raised when an underlying git command fails."""

    def __init__(self, command: Iterable[str], stdout: str, stderr: str) -> None:
        command_display = " ".join(command)
        message = (
            f"Git command failed: {command_display}\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}"
        )
        super().__init__(message)
        self.command = list(command)
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class GitResult:
    """Represents the result of a git command invocation."""

    command: List[str]
    stdout: str
    stderr: str


class BranchAutomation:
    """High level automation for managing git branches."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = repo_path

    def _run_git(self, *args: str, check: bool = True) -> GitResult:
        """Execute a git command and optionally raise on error."""
        command = ["git", *args]
        proc = subprocess.run(
            command,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        result = GitResult(command=command, stdout=proc.stdout.strip(), stderr=proc.stderr.strip())
        if check and proc.returncode != 0:
            raise GitCommandError(command, result.stdout, result.stderr)
        return result

    def current_branch(self) -> str:
        """Return the name of the current branch."""
        result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout

    def list_branches(self, remote: bool = False) -> List[str]:
        """List local or remote branches."""
        args = ["branch"]
        if remote:
            args.append("-r")
        result = self._run_git(*args)
        branches = [line.strip().lstrip("*") for line in result.stdout.splitlines() if line]
        return [branch.strip() for branch in branches]

    def create_feature_branch(self, name: str, base: str = "main", checkout: bool = True) -> GitResult:
        """Create a new feature branch from the provided base."""
        self._run_git("fetch", "origin", base, check=False)
        self._run_git("checkout", base)
        self._run_git("pull", "--ff-only", "origin", base, check=False)
        result = self._run_git("checkout", "-B", name)
        if not checkout:
            self._run_git("checkout", base)
        return result

    def ensure_tracking_branch(self, name: str, remote: str = "origin") -> GitResult:
        """Ensure the local branch has an upstream tracking branch."""
        return self._run_git("push", "-u", remote, name)

    def merge_branch(self, source: str, target: str) -> GitResult:
        """Merge the source branch into the target branch."""
        self._run_git("checkout", target)
        try:
            self._run_git("pull", "--ff-only")
        except GitCommandError:
            # Ignore failures caused by missing upstream tracking branches
            pass
        return self._run_git("merge", "--no-ff", source)

    def delete_branch(self, name: str, remote: bool = False, remote_name: str = "origin") -> GitResult:
        """Delete the specified branch locally or remotely."""
        if remote:
            return self._run_git("push", remote_name, "--delete", name)
        return self._run_git("branch", "-D", name)


__all__ = ["BranchAutomation", "GitCommandError", "GitResult"]
