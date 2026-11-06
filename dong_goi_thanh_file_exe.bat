@echo off
cd /d "%~dp0"
title Dong Goi AI PTK thanh file .EXE
echo ====================================================
echo        DONG GOI AI PTK THANH FILE .EXE CHO WINDOWS
echo ====================================================
echo Dang tien hanh bien dich desktop_agent.py thanh file AI_PTK.exe...
echo Qua trinh nay co the mat 1-2 phut, vui long cho...
echo ====================================================

python -m PyInstaller --onefile --noconsole --name "AI_PTK" --add-data "backend;backend" desktop_agent.py

if exist "dist\AI_PTK.exe" (
    echo.
    echo ====================================================
    echo THANH CONG! File chay da duoc tao tai:
    echo D:\AI PTK\dist\AI_PTK.exe
    echo.
    echo Ban co the copy file AI_PTK.exe nay gui cho bat ky ai
    echo de ho mo len va ra lenh cho AI dieu khien may tinh!
    echo ====================================================
) else (
    echo.
    echo Co loi xay ra trong qua trinh dong goi file .exe!
)

pause
