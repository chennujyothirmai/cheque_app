# 1. Update the Mobile IP to current IP
$currentIp = (ipconfig | Select-String "IPv4 Address" | ForEach-Object { $_ -replace '.*: ', '' }).Trim() | Select-Object -First 1

Write-Host "Current IP Detected: $currentIp" -ForegroundColor Cyan

# 2. Start Django in a NEW background window (so it doesn't get terminated easily)
Write-Host "Launching Django Backend in a separate window..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'c:\Users\HAI\Downloads\chequeproject33\chequeprojet'; python manage.py runserver 0.0.0.0:8000"

# 3. Start Expo in the Current Window
Write-Host "Starting Expo Frontend (This will provide Web and QR Code)..." -ForegroundColor Yellow
cd 'c:\Users\HAI\Downloads\chequeproject33\cheque_mobile'
npx expo start
