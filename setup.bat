@echo off
REM One-time setup. Needs Python 3.10+ and ffmpeg is bundled via imageio-ffmpeg.
cd /d "%~dp0"
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
REM PyTorch with CUDA 12.1 (for NVIDIA GPUs). Change cu121 if your driver needs another build.
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
echo Setup done. Now double-click run.bat
pause
