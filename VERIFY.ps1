$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Root = $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'

if (-not (Test-Path (Join-Path $Frontend 'web\index.html'))) { throw 'WEB_PLATFORM_SCAFFOLD_MISSING' }

Push-Location $Backend
try {
  python -m pip install -e '.[dev]'
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_DEPENDENCY_INSTALL_FAILED' }
  python -m ruff check src tests
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_RUFF_LINT_FAILED' }
  python -m compileall -q src tests
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_COMPILE_FAILED' }
  python -m pytest -q
  if ($LASTEXITCODE -ne 0) { throw 'BACKEND_TESTS_FAILED' }
}
finally {
  Pop-Location
}

Push-Location $Frontend
try {
  flutter pub get
  if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_PUB_GET_FAILED' }
  dart format --output=none --set-exit-if-changed lib test
  if ($LASTEXITCODE -ne 0) { throw 'DART_FORMAT_CHECK_FAILED' }
  flutter analyze
  if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_ANALYZE_FAILED' }
  flutter test
  if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_TEST_FAILED' }
  flutter build web
  if ($LASTEXITCODE -ne 0) { throw 'FLUTTER_BUILD_WEB_FAILED' }
}
finally {
  Pop-Location
}

Write-Host 'FINAL_MEGA_BATCH_TECHNICAL_GATE=PASS'
