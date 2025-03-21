@echo off
echo 正在创建虚拟环境...
python -m venv venv

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
pip install -r requirements.txt

echo 初始化数据库...
python init_db.py

echo 安装完成！
echo 请配置 .env 文件后运行 start.bat 启动服务
pause
