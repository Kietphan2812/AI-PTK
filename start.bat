@echo off
cd /d "%~dp0"
title AI PTK Starter
echo ====================================================
echo               KHOI DONG AI PTK (O DIA D)
echo ====================================================

echo [1/2] Dang khoi dong Backend FastAPI tai http://localhost:8000 ...
start "AI PTK - Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Dang khoi dong Frontend Streamlit tai http://localhost:8501 ...
start "AI PTK - Frontend" cmd /k "cd /d "%~dp0frontend" && python -m streamlit run app.py --server.port 8501"

echo ====================================================
echo Da khoi chay thanh cong ca Backend va Frontend!
echo Trinh duyet se mo tai: http://localhost:8501
echo ====================================================
timeout /t 5
