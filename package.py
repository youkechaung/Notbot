#!/usr/bin/env python
import os
import shutil
import datetime

def create_package():
    # 创建打包目录
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f'notbot_package_{timestamp}'
    package_dir = os.path.join(os.path.expanduser('~'), 'Desktop', package_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 需要包含的文件和目录
    files_to_include = [
        'app.py',
        'models.py',
        'start.py',
        'stop.py',
        'init_db.py',
        'requirements.txt',
        'deploy.md',
        'wx_easy.py',
        'templates',
        'static'
    ]

    # 复制文件
    for file_name in files_to_include:
        src_path = os.path.join(current_dir, file_name)
        dst_path = os.path.join(package_dir, file_name)
        
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dst_path)
        elif os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)

    # 创建示例 .env 文件
    with open(os.path.join(package_dir, '.env.example'), 'w', encoding='utf-8') as f:
        f.write('''MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password
SECRET_KEY=your_secret_key
''')

    # 创建zip文件
    zip_path = os.path.join(os.path.expanduser('~'), 'Desktop', package_name)
    shutil.make_archive(zip_path, 'zip', package_dir)
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    print(f'打包完成：{zip_path}.zip')

if __name__ == '__main__':
    create_package()
