param([switch]$KeepProject)
$ErrorActionPreference = 'Stop'
$testProject = Join-Path ([System.IO.Path]::GetTempPath()) ('stack2rules-test-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $testProject | Out-Null
try {
@'
{"name":"sample-dashboard","private":true,"dependencies":{"next":"*","react":"*","react-dom":"*"},"devDependencies":{"typescript":"*","tailwindcss":"*","vitest":"*"}}
'@ | Set-Content -Path "$testProject/package.json" -Encoding UTF8
@'
fastapi[standard]>=0.100
pandas>=2
sqlalchemy>=2
pydantic>=2
'@ | Set-Content -Path "$testProject/requirements.txt" -Encoding UTF8
@'
[project]
name = "sample-backend"
version = "0.1.0"
dependencies = ["numpy"]
[project.optional-dependencies]
test = ["pytest"]
'@ | Set-Content -Path "$testProject/pyproject.toml" -Encoding UTF8

    stack2rules --dir "$testProject"
    if ($LASTEXITCODE -ne 0) { throw 'Generation failed.' }
    $outputFile = Join-Path $testProject 'CLAUDE.md'
    $generated = Get-Content -Path $outputFile -Raw
    $expected = @('Node.js','Next.js','React','TypeScript','Tailwind CSS','Vitest',
                  'Python','FastAPI','Pandas','SQLAlchemy','Pydantic','NumPy','pytest')
    foreach ($technology in $expected) {
        $pattern = '(?m)^## ' + [regex]::Escape($technology) + '\r?$'
        if ($generated -notmatch $pattern) { throw "Missing rules for: $technology" }
        Write-Host "PASS: $technology" -ForegroundColor Green
    }
    $before = (Get-FileHash -Path $outputFile).Hash
    # The second invocation must refuse to replace the existing output.
    stack2rules --dir "$testProject"
    $exitCode = $LASTEXITCODE
    $after = (Get-FileHash -Path $outputFile).Hash
    if ($exitCode -ne 1 -or $before -ne $after) { throw 'Existing-file protection failed.' }
    Write-Host 'PASS: Existing CLAUDE.md was preserved.' -ForegroundColor Green
    if ($KeepProject) { Write-Host "Inspect the generated file: $outputFile" }
} finally {
    if (-not $KeepProject) { Remove-Item -LiteralPath $testProject -Recurse -Force }
}
# Reset the expected failure status so CI correctly reports this test as successful.
exit 0
