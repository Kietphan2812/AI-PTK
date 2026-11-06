@echo off
cd /d "%~dp0"
title Day code AI PTK len GitHub
echo ====================================================
echo        DANG DAY CODE AI PTK LEN GITHUB
echo ====================================================
echo.
git push -u origin main
echo.
echo ====================================================
if %errorlevel% equ 0 (
    echo [THANH CONG] Toan bo code da duoc day len GitHub!
    echo Ban co the vao: https://github.com/Kietphan2812/AI-PTK de kiem tra.
) else (
    echo [THONG BAO] Neu GitHub yeu cau dang nhap, hay nhap hoac chon "Sign in with browser".
)
echo ====================================================
pause
