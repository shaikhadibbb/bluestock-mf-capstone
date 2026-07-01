#!/bin/bash
# schedule_cron.sh — Automated Cron Scheduler for B1 Bonus Challenge
# Installs a cron job to run the live NAV fetcher every weekday (Mon-Fri) at 8:00 PM (20:00).

# Get absolute path of the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_JOB="0 20 * * 1-5 cd $PROJECT_DIR && $PROJECT_DIR/venv/bin/python $PROJECT_DIR/scripts/live_nav_fetch.py >> $PROJECT_DIR/logs/cron.log 2>&1"

# Create logs directory if not exists
mkdir -p "$PROJECT_DIR/logs"

# Add cron job (prevent duplicates by filtering)
(crontab -l 2>/dev/null | grep -Fv "live_nav_fetch.py"; echo "$CRON_JOB") | crontab -

echo "======================================================================"
echo "      BONUS CHALLENGE B1: CRON SCHEDULER"
echo "======================================================================"
echo "Successfully scheduled live NAV fetcher to run Mon-Fri at 8:00 PM."
echo "Command: $CRON_JOB"
echo "======================================================================"
