@echo off
REM Double-click to start Animal Studio (after running setup once, see README).
cd /d "%~dp0"
call .venv\Scripts\activate
streamlit run app.py
pause
