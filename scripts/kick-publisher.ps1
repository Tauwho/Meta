# Backup trigger for the cloud publisher: GitHub's cron is best-effort and can stop firing for hours.
# Runs hourly from Windows Task Scheduler (task "meta-publish-kick"); starts the publish workflow only
# when no run has started in the last 40 minutes. The --min-gap check in the workflow makes extra runs safe.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$log = Join-Path $PSScriptRoot "kick-publisher.log"
try {
    $last = gh run list --workflow publish.yml -L 1 --json createdAt -q ".[0].createdAt"
    $age = if ($last) { ((Get-Date).ToUniversalTime() - [datetime]::Parse($last).ToUniversalTime()).TotalMinutes } else { 999 }
    if ($age -ge 40) {
        gh workflow run publish.yml
        "$(Get-Date -Format s) kicked (last run $([int]$age) min ago)" | Add-Content $log
    }
} catch {
    "$(Get-Date -Format s) error: $_" | Add-Content $log
}
