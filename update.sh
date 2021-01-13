#!/bin/bash
set -e

local_branch=$(git rev-parse --symbolic-full-name --abbrev-ref HEAD)
remote_branch=$(git rev-parse --abbrev-ref --symbolic-full-name @{u})
remote=$(git config branch."$local_branch".remote)

git_updated=false

echo "Fetching from $remote..."
git fetch "$remote"

# shellcheck disable=SC2086
if git merge-base --is-ancestor $remote_branch HEAD; then
    echo 'Already up-to-date'
    # shellcheck disable=SC2034
    git_updated=true
    # exit 0
fi

# shellcheck disable=SC2078
if [ ! git_updated ]; then
    if git merge-base --is-ancestor HEAD "$remote_branch"; then
        echo 'Fast-forward possible. Merging...'
        # shellcheck disable=SC2086
        git merge --ff-only --stat $remote_branch
    else
        echo 'Fast-forward not possible. Rebasing...'
        git rebase --preserve-merges --stat "$remote_branch"
    fi
fi

# upgrade Python virtual environment
DIR_SCRIPT=$(pwd) # set current directory

# create venv if not exist
if [ ! -d "$DIR_SCRIPT"/venv ]; then
  python -m venv venv;
fi

# pip upgrade
source "$DIR_SCRIPT"/venv/bin/activate
pip install -r requirements.txt --disable-pip-version-check
deactivate

# clear
CLR="\033[1;34m"
NCLR="\033[0m"
# shellcheck disable=SC2027
echo -e """${CLR}""Update Success..""${NCLR}"
