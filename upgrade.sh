#!/bin/bash
VENV=".venv/bin/activate"
PROJECT_ENV=".env"

function run_with_check {
    command=$1
    description=$2
    echo "Running: $description"
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

if [[ ! -f $VENV ]] || [[ ! -f $PROJECT_ENV ]];then
    echo "No virtual environment, working in incorrect directory or project not set up"
    exit 1
else
    echo "Activating environment"
    source $VENV
    source $PROJECT_ENV
fi

run_with_check "backup_db" "database backup"
run_with_check "supervisorctl stop homer" "stop Homer"
run_with_check "git pull" "pull latest changes"
run_with_check "uv sync --no-dev" "update dependencies"
run_with_check "flask db upgrade" "run DB migration"
run_with_check "supervisorctl start homer" "start Homer"

echo "END"
