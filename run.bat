@echo off
title NotBot Service
setlocal enabledelayedexpansion

:: 设置颜色代码
set "GREEN=[32m"
set "YELLOW=[33m"
set "RED=[31m"
set "RESET=[0m"

echo %GREEN%NotBot 服务管理脚本%RESET%
echo ============================

:: 检查是否已经安装
if not exist "venv\Scripts\activate.bat" (
    echo %YELLOW%首次运行，正在进行安装...%RESET%
    echo.
    
    :: 创建虚拟环境
    echo %GREEN%[1/4] 创建 Python 虚拟环境...%RESET%
    python -m venv venv
    if !ERRORLEVEL! neq 0 (
        echo %RED%错误：创建虚拟环境失败！请确保已安装 Python 3.8+%RESET%
        pause
        exit /b 1
    )
    
    :: 激活虚拟环境并安装依赖
    echo %GREEN%[2/4] 安装依赖...%RESET%
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if !ERRORLEVEL! neq 0 (
        echo %RED%错误：安装依赖失败！%RESET%
        pause
        exit /b 1
    )
    
    :: 创建环境变量文件
    if not exist ".env" (
        echo %GREEN%[3/4] 创建环境变量配置...%RESET%
        (
            echo MAIL_SERVER=smtp.example.com
            echo MAIL_PORT=587
            echo MAIL_USE_TLS=True
            echo MAIL_USERNAME=your_email@example.com
            echo MAIL_PASSWORD=your_password
            echo SECRET_KEY=your_secret_key
        ) > .env
        echo %YELLOW%请修改 .env 文件中的邮箱配置！%RESET%
        notepad .env
    )
    
    :: 初始化数据库
    echo %GREEN%[4/4] 初始化数据库...%RESET%
    python init_db.py
    if !ERRORLEVEL! neq 0 (
        echo %RED%错误：初始化数据库失败！%RESET%
        pause
        exit /b 1
    )
    
    echo.
    echo %GREEN%安装完成！%RESET%
    echo.
) else (
    :: 如果已经安装，直接激活虚拟环境
    call venv\Scripts\activate.bat
)

:: 启动服务
echo %GREEN%正在启动 NotBot 服务...%RESET%
echo 按 Ctrl+C 可以停止服务
echo.

python start.py

:: 如果程序异常退出，等待用户确认
if !ERRORLEVEL! neq 0 (
    echo %RED%服务异常退出，错误代码：!ERRORLEVEL!%RESET%
    pause
)
