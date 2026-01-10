#!/bin/bash

# GitHub Profile Screenshot Automation - Cron Scheduling Script
# This script can be added to crontab for automated daily execution

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/cron-$(date +%Y-%m-%d).log"

# Create logs directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Log start time
echo "===========================================================" >> "${LOG_FILE}"
echo "Starting GitHub Screenshot Automation at $(date)" >> "${LOG_FILE}"
echo "===========================================================" >> "${LOG_FILE}"

# Change to script directory
cd "${SCRIPT_DIR}"

# Run with Docker Compose
docker-compose run --rm github-screenshot-automation >> "${LOG_FILE}" 2>&1

# Capture exit code
EXIT_CODE=$?

# Log completion
echo "-----------------------------------------------------------" >> "${LOG_FILE}"
echo "Completed at $(date) with exit code: ${EXIT_CODE}" >> "${LOG_FILE}"
echo "===========================================================" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

# Optional: Send notification on failure
if [ ${EXIT_CODE} -ne 0 ]; then
    echo "ERROR: Screenshot automation failed with exit code ${EXIT_CODE}" >> "${LOG_FILE}"
    # Add notification command here (e.g., send email, Slack notification)
fi

# Cleanup old log files (keep last 30 days)
find "${LOG_DIR}" -name "cron-*.log" -type f -mtime +30 -delete

exit ${EXIT_CODE}
