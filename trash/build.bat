@ECHO OFF
rm -rf build
if exist *.c del /f /q *.c
cython ntcyg.pyx
python setup.py build
