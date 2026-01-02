@echo off
cd /d "C:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"
call venv\Scripts\activate.bat
python jobs\compute_cvm_dfp_metrics_daily.py --year 2024 --max-rows 5000
pause
