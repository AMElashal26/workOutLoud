from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from automation.branching import BranchAutomation, GitCommandError


def init_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Configure minimal identity for commits
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (tmp_path / "README.md").write_text("sample\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=tmp_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(["git", "branch", "main"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "checkout", "main"], cwd=tmp_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return tmp_path


def test_create_and_list_branches(tmp_path: Path) -> None:
    repo_path = init_repo(tmp_path)
    automation = BranchAutomation(str(repo_path))
    automation.create_feature_branch("feature/docs", base="main")

    branches = automation.list_branches()
    assert "feature/docs" in branches


def test_merge_requires_valid_source(tmp_path: Path) -> None:
    repo_path = init_repo(tmp_path)
    automation = BranchAutomation(str(repo_path))
    automation.create_feature_branch("feature", base="main")
    (tmp_path / "feature.txt").write_text("hi", encoding="utf-8")
    subprocess.run(["git", "add", "feature.txt"], cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(
        ["git", "commit", "-m", "feature work"],
        cwd=repo_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    automation.merge_branch("feature", "main")
    log = subprocess.run(
        ["git", "log", "--oneline", "main"],
        cwd=repo_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert "feature work" in log.stdout


def test_delete_branch(tmp_path: Path) -> None:
    repo_path = init_repo(tmp_path)
    automation = BranchAutomation(str(repo_path))
    automation.create_feature_branch("cleanup", base="main", checkout=False)
    automation.delete_branch("cleanup")

    branches = automation.list_branches()
    assert "cleanup" not in branches


def test_git_command_error_contains_output(tmp_path: Path) -> None:
    repo_path = init_repo(tmp_path)
    automation = BranchAutomation(str(repo_path))
    with pytest.raises(GitCommandError) as excinfo:
        automation.delete_branch("missing")
    message = str(excinfo.value)
    assert "missing" in message
    assert "stderr" in message.lower()
