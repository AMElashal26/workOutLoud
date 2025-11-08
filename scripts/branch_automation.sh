#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Create a branch that follows the WorkOutLoud naming convention.

Usage: branch_automation.sh --project <name> --description <summary> [options]

Options:
  --project <name>       Logical project or workstream name (required)
  --description <text>   Short description of the change (required)
  --type <type>          Type of work (feature, bugfix, chore, etc.) [default: feature]
  --ticket <id>          External ticket identifier to include in the branch name
  --base <branch>        Base branch to branch from [default: main]
  --dry-run              Show the branch name without creating it
  -h, --help             Show this help message
USAGE
}

slugify() {
  local input="$1"
  # transliterate to ASCII if possible, ignore errors when iconv is unavailable
  if command -v iconv >/dev/null 2>&1; then
    input=$(printf '%s' "$input" | iconv -t ascii//TRANSLIT 2>/dev/null || printf '%s' "$input")
  fi
  input=$(printf '%s' "$input" | tr '[:upper:]' '[:lower:]')
  input=$(printf '%s' "$input" | sed -E 's/[^a-z0-9]+/-/g; s/-+/-/g; s/^-//; s/-$//')
  printf '%s' "$input"
}

require_clean_worktree() {
  if [[ -n $(git status --porcelain) ]]; then
    echo "Error: working tree is not clean. Please commit or stash changes before continuing." >&2
    exit 1
  fi
}

ensure_base_branch() {
  local base_branch="$1"
  if ! git show-ref --verify --quiet "refs/heads/$base_branch"; then
    echo "Base branch '$base_branch' not found locally. Attempting to fetch from origin." >&2
    if git ls-remote --exit-code origin "$base_branch" >/dev/null 2>&1; then
      git fetch origin "$base_branch":"$base_branch"
    else
      echo "Error: base branch '$base_branch' does not exist locally and could not be fetched from origin." >&2
      exit 1
    fi
  fi
}

main() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: this script must be run inside a git repository." >&2
    exit 1
  fi

  local project="" description="" type="feature" ticket="" base="main" dry_run=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --project)
        project="$2"; shift 2 ;;
      --description)
        description="$2"; shift 2 ;;
      --type)
        type="$2"; shift 2 ;;
      --ticket)
        ticket="$2"; shift 2 ;;
      --base)
        base="$2"; shift 2 ;;
      --dry-run)
        dry_run=true; shift ;;
      -h|--help)
        usage; exit 0 ;;
      *)
        echo "Unknown argument: $1" >&2
        usage
        exit 1 ;;
    esac
  done

  if [[ -z "$project" || -z "$description" ]]; then
    echo "Error: --project and --description are required." >&2
    usage
    exit 1
  fi

  local type_slug project_slug desc_slug ticket_slug branch_name
  type_slug=$(slugify "$type")
  project_slug=$(slugify "$project")
  desc_slug=$(slugify "$description")

  if [[ -n "$ticket" ]]; then
    ticket_slug=$(slugify "$ticket")
    branch_name="$type_slug/${project_slug}-${ticket_slug}-${desc_slug}"
  else
    branch_name="$type_slug/${project_slug}-${desc_slug}"
  fi

  if [[ "$dry_run" == true ]]; then
    printf '%s\n' "$branch_name"
    exit 0
  fi

  require_clean_worktree
  ensure_base_branch "$base"

  echo "Checking out base branch '$base'..."
  git checkout "$base" >/dev/null 2>&1 || {
    echo "Error: unable to checkout base branch '$base'." >&2
    exit 1
  }

  if git remote | grep -q '^origin$'; then
    echo "Updating '$base' from origin..."
    git pull --ff-only origin "$base"
  fi

  if git show-ref --verify --quiet "refs/heads/$branch_name"; then
    echo "Error: branch '$branch_name' already exists." >&2
    exit 1
  fi

  echo "Creating branch '$branch_name' from '$base'..."
  git checkout -b "$branch_name"

  cat <<SUMMARY

Branch '$branch_name' created successfully.
Next steps:
  1. Implement your changes.
  2. Commit with descriptive messages.
  3. Push with: git push -u origin $branch_name
SUMMARY
}

main "$@"
