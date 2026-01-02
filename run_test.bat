@echo off
cd "C:\Users\rafae\OneDrive\Desktop\Barsi Para Leigos\barsi01"
call venv\Scripts\activate.bat
python quick_test.py > dre_output.txt 2>&1
type dre_output.txt
