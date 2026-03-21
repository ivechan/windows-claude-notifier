@echo off
echo Sending curl POST request to http://127.0.0.1:5000/notify ...
echo.

curl.exe -X POST http://127.0.0.1:5000/notify -H "Content-Type: application/json" -d "{\"title\":\"Test Notification\",\"body\":\"Hello from curl\",\"sound\":\"default\"}"

echo.
echo.
pause
