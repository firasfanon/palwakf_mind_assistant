$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Root = $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'
$Runtime = Join-Path $Root '.runtime'
New-Item -ItemType Directory -Path $Runtime -Force | Out-Null

function Get-FreeLoopbackPort {
  $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
  try {
    $listener.Start()
    return ([System.Net.IPEndPoint]$listener.LocalEndpoint).Port
  }
  finally {
    $listener.Stop()
  }
}

function Assert-Command([string]$Name) {
  $command = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $command) { throw ('TOOL_NOT_FOUND:{0}' -f $Name) }
  return $command.Source
}

$PythonExe = Assert-Command 'python'
$null = Assert-Command 'flutter'
$null = Assert-Command 'dart'

if (-not (Test-Path (Join-Path $Frontend 'web\index.html'))) {
  throw 'WEB_PLATFORM_SCAFFOLD_MISSING'
}

Write-Host '=== PALWAKF MIND ASSISTANT FINAL INTEGRATED MEGA BATCH TEST ==='
Write-Host '[1/6] Backend repository-native gates'
Push-Location $Backend
try {
  & $PythonExe -m pip install -e '.[dev]'
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_DEPENDENCY_INSTALL_FAILED' }
  & $PythonExe -m ruff check --fix src tests
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_RUFF_AUTOFIX_FAILED' }
  & $PythonExe -m ruff check src tests
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_RUFF_LINT_FAILED' }
  & $PythonExe -m compileall -q src tests
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_COMPILE_FAILED' }
  & $PythonExe -m pytest -q
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_TESTS_FAILED' }
}
finally {
  Pop-Location
}

$ApiPort = Get-FreeLoopbackPort
$WebPort = Get-FreeLoopbackPort
$ApiBaseUrl = ('http://127.0.0.1:{0}' -f $ApiPort)
$BackendStdout = Join-Path $Runtime 'uvicorn.stdout.log'
$BackendStderr = Join-Path $Runtime 'uvicorn.stderr.log'
Remove-Item $BackendStdout,$BackendStderr -Force -ErrorAction SilentlyContinue

Write-Host ('[2/6] Starting read-only backend on {0}' -f $ApiBaseUrl)
$BackendProcess = Start-Process -FilePath $PythonExe -ArgumentList @(
  '-m','uvicorn','palwakf_mind_assistant.api.app:app','--app-dir','src',
  '--host','127.0.0.1','--port',"$ApiPort"
) -WorkingDirectory $Backend -RedirectStandardOutput $BackendStdout -RedirectStandardError $BackendStderr -PassThru

try {
  $health = $null
  for ($attempt = 1; $attempt -le 20; $attempt++) {
    Start-Sleep -Seconds 1
    $BackendProcess.Refresh()
    if ($BackendProcess.HasExited) {
      Write-Host '--- UVICORN STDOUT ---'
      if (Test-Path $BackendStdout) { Get-Content $BackendStdout }
      Write-Host '--- UVICORN STDERR ---'
      if (Test-Path $BackendStderr) { Get-Content $BackendStderr }
      throw ('BACKEND_EXITED_EARLY:{0}' -f $BackendProcess.ExitCode)
    }
    try {
      $health = Invoke-RestMethod -Uri "$ApiBaseUrl/health" -Method Get -TimeoutSec 2
      if ($null -ne $health) { break }
    }
    catch {
      Write-Host ('Health wait {0}/20' -f $attempt)
    }
  }
  if ($null -eq $health) { throw 'BACKEND_HEALTH_TIMEOUT' }
  if ($health.status -ne 'ok' -or $health.mutation_mode -ne 'READ_ONLY') {
    throw 'BACKEND_HEALTH_INVARIANT_FAILED'
  }
  Write-Host 'BACKEND_HEALTH_GATE=PASS'

  Write-Host 'FINAL_MEGA_BATCH_API_SMOKE=START'
  $Headers = @{ 'Content-Type' = 'application/json; charset=utf-8' }

  $PlanningBody = @{
    project_id = 'PALWAKF_MIND_ASSISTANT'
    goal = 'governed integrated development'
  } | ConvertTo-Json -Compress
  $Planning = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/planning" -Method Post -Headers $Headers -Body $PlanningBody
  if ($Planning.approval_required -ne $true) { throw 'PLANNING_APPROVAL_GATE_FAILED' }

  $ImpactBody = @{
    project_id = 'PALWAKF_MIND_ASSISTANT'
    proposed_change = 'shared contract change'
  } | ConvertTo-Json -Compress
  $Impact = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/impact" -Method Post -Headers $Headers -Body $ImpactBody
  if ($Impact.mutation_mode -ne 'READ_ONLY') { throw 'IMPACT_READ_ONLY_GATE_FAILED' }

  $Envelope = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/capabilities/PALWAKF_MIND_ASSISTANT/envelope" -Method Get
  if ($Envelope.client_can_widen -ne $false) { throw 'CAPABILITY_CLIENT_WIDEN_GATE_FAILED' }

  $Repository = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/repositories/PALWAKF_MIND_ASSISTANT" -Method Get
  if ($Repository.mutation_ready -ne $false) { throw 'REPOSITORY_MUTATION_READY_FALSE_GATE_FAILED' }

  $ExecutionBody = @{
    project_id = 'PALWAKF_MIND_ASSISTANT'
    capability_id = 'repo.write'
    requested_paths = @('README.md')
    simulate = $true
  } | ConvertTo-Json -Compress
  $Execution = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/execution/simulate" -Method Post -Headers $Headers -Body $ExecutionBody
  if ($Execution.mutation_executed -ne $false) { throw 'EXECUTION_MUTATION_GATE_FAILED' }

  $Agents = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/agents/PALWAKF_MIND_ASSISTANT" -Method Get
  if ($Agents.authority_expanded -ne $false) { throw 'AGENT_AUTHORITY_EXPANSION_GATE_FAILED' }

  $Lifecycle = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/lifecycle/PALWAKF_MIND_ASSISTANT" -Method Get
  if ($Lifecycle.mutation_mode -ne 'SIMULATION_ONLY') { throw 'LIFECYCLE_MUTATION_GATE_FAILED' }

  $Operations = Invoke-RestMethod -Uri "$ApiBaseUrl/v1/operations/PALWAKF_MIND_ASSISTANT" -Method Get
  if ($Operations.recovery.canonical_data_loss -ne $false) { throw 'RECOVERY_CANONICAL_DATA_LOSS_GATE_FAILED' }

  Write-Host 'FINAL_MEGA_BATCH_API_SMOKE=PASS'

  Write-Host '[3/6] Flutter format/analyze/test gates'
  Push-Location $Frontend
  try {
    flutter pub get
    if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_PUB_GET_FAILED' }

    dart format lib test
    if ($LASTEXITCODE -ne 0) { throw 'DART_FORMAT_WRITE_FAILED' }
    dart format --output=none --set-exit-if-changed lib test
    if ($LASTEXITCODE -ne 0) { throw 'DART_FORMAT_IDEMPOTENCE_FAILED' }

    flutter analyze
    if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_ANALYZE_FAILED' }
    flutter test
    if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_TEST_FAILED' }

    Write-Host '[4/6] Flutter web build gate'
    flutter build web --dart-define="MIND_API_BASE_URL=$ApiBaseUrl"
    if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_BUILD_WEB_FAILED' }
    Write-Host 'FLUTTER_BUILD_WEB_GATE=PASS'

    Write-Host '[5/6] Launching Chrome runtime'
    Write-Host ('API_BASE={0}' -f $ApiBaseUrl)
    Write-Host ('WEB_PORT={0}' -f $WebPort)
    Write-Host 'Use the acceptance checklist while this process remains open.'
    flutter run -d chrome --web-port $WebPort --dart-define="MIND_API_BASE_URL=$ApiBaseUrl"
    if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_CHROME_RUNTIME_FAILED' }
  }
  finally {
    Pop-Location
  }

  Write-Host '[6/6] Runtime closed by operator'
}
finally {
  if ($null -ne $BackendProcess) {
    $BackendProcess.Refresh()
    if (-not $BackendProcess.HasExited) {
      Stop-Process -Id $BackendProcess.Id -Force
    }
  }
}
