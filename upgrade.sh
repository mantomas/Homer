#!/bin/bash
VENV=".venv/bin/activate"
PROJECT_ENV=".env"

function run_with_check {
    command=$1
    description=$2
    echo "Running: $description"
    # ensure running as regular user
    $command
    if [[ $? -ne 0 ]];then
        echo "Error running: $description"
        exit 1
    fi
}

function backup_db {
    [[ ! -d "backups" ]] && mkdir backups
    latest_db="${DATABASE_URL#sqlite:///}"
    if [[ ! -f $latest_db ]];then
        echo "Database file not found: $latest_db"
        exit 1
    else
        target="backups/db.sqlite3.$(date +%Y-%m-%d-%H-%M-%S)"
        cp $latest_db $target
	    echo "Database backup created: $target"
    fi
}

function check_status {
    echo "Checking environment."
    if [[ ! -f $VENV ]] || [[ ! -f $PROJECT_ENV ]];then
        echo "No virtual environment, working in incorrect directory or project not set up"
        exit 1
    fi
}

function init_env {
    echo "Activating environment"
    source $VENV
    source $PROJECT_ENV
}

# basic check if it looks like the right kind of project
check_status
# init the environment
init_env
# backup DB before any changes
run_with_check "backup_db" "database backup"
# ready, stop Homer then
run_with_check "sudo supervisorctl stop homer" "stop Homer"
# get latest changes
run_with_check "git pull" "pull latest changes"
# sync dependencies
run_with_check "uv sync --no-dev" "update dependencies"
# perform DB migration
run_with_check "flask db upgrade" "run DB migration"
# get Homer back on
run_with_check "sudo supervisorctl start homer" "start Homer"

echo "END"
