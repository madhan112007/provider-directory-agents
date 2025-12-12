@echo off
echo ========================================
echo   Provider Directory AI Dashboard
echo ========================================
echo.
echo Starting dashboard server...
echo.
streamlit run dashboard.py --server.port 8501 --server.headless true
pause
