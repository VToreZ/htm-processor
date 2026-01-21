@echo off
chcp 65001 >nul
echo ========================================
echo   Обработка отчётов HTM - .01
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo.
    echo Пожалуйста, установите Python 3.8+ с https://www.python.org/downloads/
    echo При установке поставьте галочку "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Проверка зависимостей...
python -c "import tkinterdnd2" >nul 2>&1
if %errorlevel% neq 0 (
    echo Устанавливаю необходимые библиотеки...
    pip install tkinterdnd2
    echo.
)

echo Запускаю программу...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ОШИБКА при запуске программы!
    pause
)
