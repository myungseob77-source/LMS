[CmdletBinding()]
param(
    [string]$Destination = (Join-Path $env:USERPROFILE 'source\LMS'),
    [switch]$LoginGitHub,
    [switch]$SkipOpen
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Repository = 'https://github.com/myungseob77-source/LMS.git'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable failed (exit $LASTEXITCODE)." }
}
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
        [Environment]::GetEnvironmentVariable('Path','User')
}
function Ensure-Tool {
    param([string]$Command, [string]$Package)
    if (Get-Command $Command -ErrorAction SilentlyContinue) { return }
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Install or update App Installer from Microsoft Store, then rerun.'
    }
    Invoke-Checked 'winget' @('install','--id',$Package,'--exact','--source','winget',
        '--accept-source-agreements','--accept-package-agreements','--disable-interactivity')
    Refresh-Path
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        throw "$Package installed; reopen PowerShell and rerun this script."
    }
}

Ensure-Tool 'git' 'Git.Git'
Ensure-Tool 'gh' 'GitHub.cli'
Ensure-Tool 'code' 'Microsoft.VisualStudioCode'
Ensure-Tool 'py' 'Python.Python.3.12'
Invoke-Checked 'py' @('-3.12','-c','import sys; assert sys.version_info >= (3,12)')

$Destination = [IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $Destination) {
    if (-not (Test-Path -LiteralPath (Join-Path $Destination '.git'))) {
        throw 'Destination exists but is not a Git checkout. Choose a different -Destination.'
    }
    $Origin = & git -C $Destination remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $Origin -notin @($Repository, $Repository.Replace('.git',''), 'git@github.com:myungseob77-source/LMS.git')) {
        throw 'Destination belongs to another repository; no files were changed.'
    }
    Write-Host 'Using existing LMS checkout without reset, pull or overwrite.'
} else {
    $Parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    Invoke-Checked 'git' @('clone',$Repository,$Destination)
}
if (-not (Test-Path -LiteralPath (Join-Path $Destination 'pyproject.toml'))) {
    throw 'Checkout does not contain the engineering setup. Update it to the setup commit, then rerun.'
}
Push-Location $Destination
try {
    $Python = Join-Path $Destination '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $Python)) {
        Invoke-Checked 'py' @('-3.12','-m','venv','.venv')
    }
    Invoke-Checked $Python @('-m','pip','install','-e','.')
    Invoke-Checked $Python @('-m','unittest','discover','-s','tests','-v')
    Invoke-Checked $Python @('-m','lms_engine','--mode','graph')
    Invoke-Checked 'code' @('--install-extension','ms-python.python')
    Invoke-Checked 'code' @('--install-extension','ms-python.debugpy')
    Invoke-Checked 'code' @('--install-extension','GitHub.vscode-pull-request-github')
    if ($LoginGitHub) {
        Invoke-Checked 'gh' @('auth','login','--hostname','github.com','--git-protocol','https','--web')
        Invoke-Checked 'gh' @('auth','setup-git')
    }
    Write-Host "Setup complete: $Destination"
    Write-Host 'VS Code: use F5 for graph demo; Terminal > Run Task for tests.'
    if (-not $SkipOpen) { Invoke-Checked 'code' @($Destination) }
} finally { Pop-Location }
