# NotBot 部署指南

## 1. 环境要求
- Python 3.8+
- pip (Python包管理器)

## 2. 安装步骤

### 2.1 安装 Python 依赖
```bash
# 建议使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置环境变量
创建 `.env` 文件并设置以下变量：
```
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

### 2.3 初始化数据库
```bash
python init_db.py
```

## 3. 运行服务

### 3.1 开发环境运行
```bash
python start.py
```

### 3.2 生产环境运行
建议使用 supervisor 或 systemd 管理服务。

#### 使用 supervisor (推荐)
1. 安装 supervisor:
```bash
pip install supervisor
```

2. 创建配置文件 `/etc/supervisor/conf.d/notbot.conf`:
```ini
[program:notbot]
directory=/path/to/notbot
command=/path/to/notbot/venv/bin/python start.py
autostart=true
autorestart=true
stderr_logfile=/var/log/notbot/err.log
stdout_logfile=/var/log/notbot/out.log
user=your_username
```

3. 创建日志目录：
```bash
mkdir -p /var/log/notbot
```

4. 重启 supervisor：
```bash
supervisorctl reread
supervisorctl update
supervisorctl start notbot
```

## 4. 常见问题

### 4.1 权限问题
确保程序有权限访问以下目录和文件：
- 程序目录
- 数据库文件 (users.db)
- 日志目录

### 4.2 端口占用
如果端口被占用，可以在 `start.py` 中修改端口号。

### 4.3 日志查看
- 程序日志：`/var/log/notbot/out.log`
- 错误日志：`/var/log/notbot/err.log`

## 5. 维护命令

### 5.1 启动服务
```bash
supervisorctl start notbot
```

### 5.2 停止服务
```bash
supervisorctl stop notbot
```

### 5.3 重启服务
```bash
supervisorctl restart notbot
```

### 5.4 查看状态
```bash
supervisorctl status notbot
```
