$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workersHelmDir = Join-Path $scriptDir "calculator\workers\helm"
$temporalServerHelmDir = Join-Path $scriptDir "temporal_server\helm"
$triggerServerHelmDir = Join-Path $scriptDir "trigger_server\helm"
$rootDockerfile = Join-Path $scriptDir "Dockerfile"
$temporalServerDockerfile = Join-Path $scriptDir "temporal_server\Dockerfile"
$triggerServerDockerfile = Join-Path $scriptDir "trigger_server\Dockerfile"

if (-not (Test-Path -Path $rootDockerfile -PathType Leaf)) {
    throw "Root Dockerfile not found: $rootDockerfile"
}

if (-not (Test-Path -Path $temporalServerDockerfile -PathType Leaf)) {
    throw "Temporal server Dockerfile not found: $temporalServerDockerfile"
}

if (-not (Test-Path -Path $triggerServerDockerfile -PathType Leaf)) {
    throw "Trigger server Dockerfile not found: $triggerServerDockerfile"
}

if (-not (Test-Path -Path $workersHelmDir -PathType Container)) {
    throw "Workers helm directory not found: $workersHelmDir"
}

if (-not (Test-Path -Path $temporalServerHelmDir -PathType Container)) {
    throw "Temporal server helm directory not found: $temporalServerHelmDir"
}

if (-not (Test-Path -Path $triggerServerHelmDir -PathType Container)) {
    throw "Trigger server helm directory not found: $triggerServerHelmDir"
}

if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
    throw "minikube command not found in PATH"
}

Write-Host "Switching Docker daemon to Minikube"
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

Write-Host "Building calculator worker image from $scriptDir"
docker build -t calculator-worker:latest $scriptDir

$temporalServerBuildDir = Join-Path $scriptDir "temporal_server"
Write-Host "Building temporal server image from $temporalServerBuildDir"
docker build -t temporal-server:latest $temporalServerBuildDir

Write-Host "Building trigger server image from $scriptDir"
docker build -f $triggerServerDockerfile -t trigger-server:latest $scriptDir

Write-Host "Deploying temporal-server from $temporalServerHelmDir"
helm upgrade --install temporal-server $temporalServerHelmDir

Write-Host "Deploying trigger-server from $triggerServerHelmDir"
helm upgrade --install trigger-server $triggerServerHelmDir

Get-ChildItem -Path $workersHelmDir -Directory | ForEach-Object {
    $workerName = $_.Name
    $releaseName = "$workerName-worker"
    $chartDir = $_.FullName

    Write-Host "Deploying $releaseName from $chartDir"
    helm upgrade --install $releaseName $chartDir
}

Write-Host "Images built, temporal/trigger servers deployed, and all calculator workers deployed/upgraded."
