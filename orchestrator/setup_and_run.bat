@echo off
cls
echo ========================================
echo   Provider Directory AI Setup
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo [2/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [3/4] Running tests...
python test_orchestrator.py
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo   Choose an option:
echo ========================================
echo   1. Launch Dashboard (Streamlit)
echo   2. Start API Server (FastAPI)
echo   3. Run Demo
echo   4. Exit
echo ========================================
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting dashboard...
    streamlit run dashboard.py
) else if "%choice%"=="2" (
    echo.
    echo Starting API server...
    python api_server.py
) else if "%choice%"=="3" (
    echo.
    echo Running demo...
    python demo.py
) else (
    echo.
    echo Goodbye!
)

pause
