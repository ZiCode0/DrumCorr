#!/bin/bash
set -e

local_branch=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
remote_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u})
remote=$(git config branch."$local_branch".remote)

echo "Fetching from $remote..."
git fetch "$remote"

# shellcheck disable=SC2086
if git merge-base --is-ancestor $remote_branch HEAD; then
    echo 'Already up-to-date'
    exit 0
fi

if git merge-base --is-ancestor HEAD "$remote_branch"; then
    echo 'Fast-forward possible. Merging...'
    # shellcheck disable=SC2086
    git merge --ff-only --stat $remote_branch
else
    echo 'Fast-forward not possible. Rebasing...'
    git rebase --preserve-merges --stat "$remote_branch"
fi

DIR_SCRIPT=$(pwd) # Current directory

# create new venv if not exist
if [ ! -d "$DIR_SCRIPT"/venv ]; then
  python -m venv venv;
fi

source "$DIR_SCRIPT"/venv/bin/activate
pip install -r requirements.txt
deactivate