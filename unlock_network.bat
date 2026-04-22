@echo off
echo ====================================================
echo   DropShare Network Unlocker
echo ====================================================
echo.
echo This will allow your phone to connect to this PC via WiFi.
echo.
netsh advfirewall firewall add rule name="DropShare Port 8000" dir=in action=allow protocol=TCP localport=8000
echo.
echo SUCCESS: Port 8000 is now open!
echo.
echo Now, restart your server and try the "Mobile Link" again.
echo.
pause
