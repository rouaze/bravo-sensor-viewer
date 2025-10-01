@echo off
setlocal EnableDelayedExpansion

REM Container testing script for Bravo Sensor Viewer v2.0.0 on Windows
REM Tests Docker setup without requiring physical devices

echo.
echo ^🧪 Bravo Sensor Viewer v2.0.0 - Container Testing
echo =======================================================

REM Test counters
set /a TESTS_PASSED=0
set /a TESTS_FAILED=0
set /a TOTAL_TESTS=0

REM Function to run test and report result (simulated with labels)
goto main

:run_test
set TEST_NAME=%~1
set TEST_COMMAND=%~2
echo 🔬 Testing: %TEST_NAME%
%TEST_COMMAND% >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: %TEST_NAME%
    set /a TESTS_PASSED+=1
    exit /b 0
) else (
    echo ❌ FAIL: %TEST_NAME%
    set /a TESTS_FAILED+=1
    exit /b 1
)

:main

echo.
echo === Phase 1: Prerequisites ===

REM Test 1: Docker availability
set /a TOTAL_TESTS+=1
docker --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Docker availability
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Docker availability
    echo ❌ Docker is required for container testing
    set /a TESTS_FAILED+=1
    pause
    exit /b 1
)

REM Determine Docker Compose command
docker compose version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set DOCKER_COMPOSE=docker compose
    echo ✅ Using Docker Compose: docker compose
) else (
    docker-compose --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set DOCKER_COMPOSE=docker-compose
        echo ✅ Using Docker Compose: docker-compose
    ) else (
        echo ❌ Docker Compose is required
        pause
        exit /b 1
    )
)

echo.
echo === Phase 2: Container Build ===

REM Test 2: Container build
set /a TOTAL_TESTS+=1
echo 🔬 Testing: Container build
%DOCKER_COMPOSE% build --no-cache
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Container build
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Container build
    set /a TESTS_FAILED+=1
)

echo.
echo === Phase 3: Python Environment ===

REM Test 3: Python version
set /a TOTAL_TESTS+=1
echo 🔬 Testing: Python version check
%DOCKER_COMPOSE% run --rm bravo-sensor-viewer python --version
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Python version check
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Python version check
    set /a TESTS_FAILED+=1
)

echo.
echo === Phase 4: Core Dependencies ===

REM Test 4: Core imports
set /a TOTAL_TESTS+=1
echo 🔬 Testing: Core imports

set IMPORT_TEST=^
try:^
    print('Testing core imports...')^
    import sys, os, time, logging^
    print('✅ Standard library imports OK')^
    import PyQt5.QtWidgets, PyQt5.QtCore, PyQt5.QtGui^
    print('✅ PyQt5 imports OK')^
    import matplotlib^
    matplotlib.use('Agg')^
    import matplotlib.pyplot as plt^
    print('✅ Matplotlib imports OK')^
    import numpy as np^
    print('✅ NumPy imports OK')^
    from pyhidpp.core.devices_manager import DevicesManager^
    from pyhidpp.security import SecurityManager^
    from pyhidpp.features.x9402 import X9402^
    from pyhidpp.features.x19c0 import X19C0^
    print('✅ pyhidpp imports OK')^
    print('🎉 All core imports successful!')^
except ImportError as e:^
    print(f'❌ Import error: {e}')^
    sys.exit(1)^
except Exception as e:^
    print(f'❌ Unexpected error: {e}')^
    sys.exit(1)

%DOCKER_COMPOSE% run --rm bravo-sensor-viewer python -c "%IMPORT_TEST%"
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Core imports
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Core imports
    set /a TESTS_FAILED+=1
)

echo.
echo === Phase 5: Version Information ===

REM Test 5: Version information
set /a TOTAL_TESTS+=1
echo 🔬 Testing: Version information

set VERSION_TEST=^
try:^
    from version import __version__, __build_date__, __author__^
    print(f'Version: {__version__}')^
    print(f'Build Date: {__build_date__}')^
    print(f'Author: {__author__}')^
    parts = __version__.split('.')^
    if len(parts) ^< 2:^
        raise ValueError('Invalid version format')^
    if __version__ != '2.0.0':^
        raise ValueError(f'Expected version 2.0.0, got {__version__}')^
    print('✅ Version information valid')^
except Exception as e:^
    print(f'❌ Version test error: {e}')^
    import sys^
    sys.exit(1)

%DOCKER_COMPOSE% run --rm bravo-sensor-viewer python -c "%VERSION_TEST%"
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Version information
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Version information
    set /a TESTS_FAILED+=1
)

echo.
echo === Phase 6: Service Configuration ===

REM Test 6: Docker Compose config
set /a TOTAL_TESTS+=1
echo 🔬 Testing: Docker Compose configuration
%DOCKER_COMPOSE% config --quiet
if %ERRORLEVEL% equ 0 (
    echo ✅ PASS: Docker Compose configuration
    set /a TESTS_PASSED+=1
) else (
    echo ❌ FAIL: Docker Compose configuration
    set /a TESTS_FAILED+=1
)

REM Calculate results
echo.
echo ========================================
echo 📊 TEST RESULTS SUMMARY
echo ========================================

echo ✅ Tests Passed: %TESTS_PASSED%
echo ❌ Tests Failed: %TESTS_FAILED%
echo 📈 Total Tests: %TOTAL_TESTS%

if %TESTS_FAILED% equ 0 (
    echo.
    echo 🎉 ALL TESTS PASSED! Container setup is working correctly.
    echo ✨ The containerization is ready for deployment!
    echo.
    echo 🚀 Quick start commands:
    echo    run.bat           - Start GUI application
    echo    run.bat --test    - Run device tests
    echo    run.bat --dev     - Development mode
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo ❌ TESTS FAILED! Please check the errors above.
    echo 💡 Try rebuilding: %DOCKER_COMPOSE% build --no-cache
    pause
    exit /b 1
)