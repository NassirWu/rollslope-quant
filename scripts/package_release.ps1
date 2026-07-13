param(
    [string]$Version = "v0.10.0",
    [string]$SourceRef = "HEAD",
    [string]$BeginnerDocxPath = "release_inputs/word/RollSlope_Quant_MVP_完全新手操作說明_v0.10.0.docx",
    [string]$TechnicalDocxPath = "release_inputs/word/RollSlope_Quant_MVP_專業技術交付說明_v0.10.0.docx"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ("=" * 72)
Write-Host "RollSlope Quant MVP - Release Packaging"
Write-Host ("=" * 72)
Write-Host "Version         : $Version"
Write-Host "SourceRef       : $SourceRef"
Write-Host "BeginnerDocx    : $BeginnerDocxPath"
Write-Host "TechnicalDocx   : $TechnicalDocxPath"
Write-Host ("=" * 72)

# --- Step 1: Verify all required inputs exist before touching anything ---
if (-not (Test-Path $BeginnerDocxPath)) {
    Write-Error "找不到完全新手操作說明 Word 檔：$BeginnerDocxPath，請先把檔案放到 release_inputs/word/ 底下再執行。"
    exit 1
}
if (-not (Test-Path $TechnicalDocxPath)) {
    Write-Error "找不到專業技術交付說明 Word 檔：$TechnicalDocxPath，請先把檔案放到 release_inputs/word/ 底下再執行。"
    exit 1
}

$ReleaseNotesPath = "docs/release_notes_$Version.md"
if (-not (Test-Path $ReleaseNotesPath)) {
    Write-Error "找不到 release notes：$ReleaseNotesPath，請先新增這份文件再執行。"
    exit 1
}

git rev-parse --verify "$SourceRef^{commit}" *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "SourceRef 不存在或不是有效的 git 版本：$SourceRef"
    exit 1
}

# --- Step 2: Clean previous packaging outputs (only known generated files, never source folders) ---
Write-Host "Cleaning previous release outputs..."

if (Test-Path "release") {
    Remove-Item -Path "release/*" -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path "release" | Out-Null

Remove-Item -Path "reports/*.png" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "reports/*.csv" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data/raw/sample_v_reversal.csv" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "data/raw/sample_market_kline.csv" -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "." -Filter "test_delivery_*" -Force -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path "." -Filter "*.zip" -File -Force -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

# --- Step 3: Generate source zip directly from git (only tracked files; no venv, no .git, no secrets) ---
$SourceZipPath = "release/RollSlope_Quant_MVP_${Version}_Source.zip"
Write-Host "Creating source zip from $SourceRef ..."
git archive --format=zip -o $SourceZipPath $SourceRef
if ($LASTEXITCODE -ne 0) {
    Write-Error "git archive 失敗，無法產生 source zip。"
    exit 1
}

# --- Step 4: Copy Word guides and release notes into release/ ---
Copy-Item -Path $BeginnerDocxPath -Destination "release/" -Force
Copy-Item -Path $TechnicalDocxPath -Destination "release/" -Force
Copy-Item -Path $ReleaseNotesPath -Destination "release/" -Force

# --- Step 5: Build final delivery zip ---
$DeliveryZipPath = "release/RollSlope_Quant_MVP_${Version}_Delivery.zip"
$DeliveryParts = @(
    $SourceZipPath,
    (Join-Path "release" (Split-Path -Leaf $BeginnerDocxPath)),
    (Join-Path "release" (Split-Path -Leaf $TechnicalDocxPath)),
    (Join-Path "release" (Split-Path -Leaf $ReleaseNotesPath))
)
Compress-Archive -Path $DeliveryParts -DestinationPath $DeliveryZipPath -Force

Write-Host ("=" * 72)
Write-Host "Release packaging complete"
Write-Host ("=" * 72)
Write-Host "source_zip      : $SourceZipPath"
Write-Host "beginner_docx   : release/$(Split-Path -Leaf $BeginnerDocxPath)"
Write-Host "technical_docx  : release/$(Split-Path -Leaf $TechnicalDocxPath)"
Write-Host "release_notes   : release/$(Split-Path -Leaf $ReleaseNotesPath)"
Write-Host "delivery_zip    : $DeliveryZipPath"
Write-Host ("=" * 72)
