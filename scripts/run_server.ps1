Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\NLPCC_tasks"
try {
    python .\start_server.py
}
finally {
    Pop-Location
}
