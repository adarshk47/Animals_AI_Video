@echo off
REM One-time setup. Needs Python 3.10-3.12 (3.13 may lack some wheels). ffmpeg is bundled via imageio-ffmpeg.
cd /d "%~dp0"
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip

REM Install the CUDA build of PyTorch FIRST, so other packages do not pull the CPU build.
pip uninstall -y torch torchvision torchaudio
pip install torch --index-url https://download.pytorch.org/whl/cu124
if errorlevel 1 (
  echo.
  echo PyTorch CUDA install FAILED. Run "python --version" and send the output.
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
