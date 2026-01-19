# .env 파일 열기 스크립트
# 이 스크립트를 실행하면 .env 파일을 기본 에디터로 엽니다

$envFile = Join-Path $PSScriptRoot ".env"

if (Test-Path $envFile) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "환경 변수 설정" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host ".env 파일 위치: $envFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "다음 단계:" -ForegroundColor Yellow
    Write-Host "1. ANTHROPIC_API_KEY 값을 실제 Claude API 키로 변경" -ForegroundColor White
    Write-Host "2. Supabase 설정도 필요하면 변경" -ForegroundColor White
    Write-Host ""
    Write-Host "파일을 여는 중..." -ForegroundColor Gray
    
    # VS Code가 있으면 VS Code로, 없으면 메모장으로 열기
    if (Get-Command code -ErrorAction SilentlyContinue) {
        code $envFile
    } else {
        notepad $envFile
    }
} else {
    Write-Host ""
    Write-Host ".env 파일을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host ".env.example 파일을 .env로 복사하세요." -ForegroundColor Yellow
    Write-Host ""
}
