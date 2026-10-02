@echo off
REM One-time setup. Needs Python 3.12 (64-bit). Newer Python (3.13/3.14) has no PyTorch CUDA packages.
REM ffmpeg is bundled via imageio-ffmpeg.
cd /d "%~dp0"

echo Your Python versions:
py -0p 2>nul
python --version

REM Start clean: the old .venv may be built on the wrong Python.
if exist .venv rmdir /s /q .venv

py -3.12 -m venv .venv 2>nul
if not exist .venv\Scripts\activate.bat (
  REM No py launcher: use plain "python" if it is 3.12.
  python --version 2>&1 | findstr /C:"3.12" >nul && python -m venv .venv
)
if not exist .venv\Scripts\activate.bat (
  echo.
  echo Python 3.12 was not found.
  echo 1. Download "Windows installer (64-bit)" for Python 3.12 from https://www.python.org/downloads/windows/
  echo 2. In the installer tick "Add python.exe to PATH" and keep "py launcher" ticked.
  echo 3. Run setup.bat again.
  pause
  exit /b 1
)
call .venv\Scripts\activate
python --version
python -m pip install --upgrade pip

REM Install the CUDA build of PyTorch FIRST, so other packages do not pull the CPU build.
pip install torch --index-url https://download.pytorch.org/whl/cu124
if errorlevel 1 (
  echo.
  echo PyTorch CUDA install FAILED. Send a screenshot of this window.
  pause
  exit /b 1
)
pip install -r requirements.txt

echo.
echo Checking GPU support:
python -c "import torch; print('torch', torch.__version__, '| CUDA available:', torch.cuda.is_available())"
echo If it says CUDA available: False, update the NVIDIA driver and restart the PC.
echo Then double-click run.bat
pause
