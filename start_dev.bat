@echo off
chcp 65001 > nul
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && echo Installing backend dependencies (using proxy)... && echo Starting backend server (main.py)... && python main.py"

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd BillNote_frontend && echo Installing frontend dependencies... && pnpm install && echo Starting frontend dev server... && pnpm dev"

echo.
echo Startup script initiated. Please check the two new terminal windows for server status.
echo This window will close after you press any key.
pause > nul