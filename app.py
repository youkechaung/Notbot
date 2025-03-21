from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
import json
import os
import socket
import random
import string
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 用于session加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 邮件配置
app.config['MAIL_SERVER'] = 'smtp.qq.com'  # 使用QQ邮箱
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1453137592@qq.com'
app.config['MAIL_PASSWORD'] = 'pzdylfzssqjfjiid'

# 初始化插件
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'wechat_config.json')
WXEASY_FILE = os.path.join(BASE_DIR, 'wx_easy.py')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(user):
    code = generate_verification_code()
    user.set_verification_code(code)
    db.session.commit()
    
    msg = Message('验证你的邮箱',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'你的验证码是: {code}\n该验证码10分钟内有效。'
    mail.send(msg)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_config(listen_list):
    # Save to config file
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(listen_list, f, ensure_ascii=False, indent=2)
    
    # Update wx_easy.py
    try:
        with open(WXEASY_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if 'listen_list = ' in line:
                lines[i] = f"listen_list = {repr(listen_list)}\n"
                break
        
        with open(WXEASY_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', contacts=load_config())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('请先验证你的邮箱')
                return redirect(url_for('verify_email', user_id=user.id))
        flash('邮箱或密码错误')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册')
            return redirect(url_for('register'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        send_verification_email(user)
        return redirect(url_for('verify_email', user_id=user.id))
    
    return render_template('register.html')

@app.route('/verify_email/<int:user_id>', methods=['GET', 'POST'])
def verify_email(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('用户不存在', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        if user.check_verification_code(code):
            user.is_active = True
            db.session.commit()
            login_user(user)
            flash('邮箱验证成功！', 'success')
            return redirect(url_for('index'))
        flash('验证码无效或已过期', 'error')
    
    return render_template('verify_email.html', user=user)

@app.route('/resend_code/<int:user_id>')
def resend_code(user_id):
    user = User.query.get(user_id)
    if user:
        send_verification_email(user)
        flash('新的验证码已发送到你的邮箱')
    return redirect(url_for('verify_email', user_id=user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    return jsonify(load_config())

@app.route('/api/contacts', methods=['POST'])
@login_required
def add_contact():
    data = request.get_json()
    contact = data.get('contact', '').strip()
    if not contact:
        return jsonify({'error': '联系人名称不能为空'}), 400
    
    contacts = load_config()
    if contact in contacts:
        return jsonify({'error': '联系人已存在'}), 400
    
    contacts.append(contact)
    error = save_config(contacts)
    if error is True:
        return jsonify({'message': '联系人添加成功'})
    else:
        return jsonify({'error': str(error)}), 500

@app.route('/api/contacts', methods=['DELETE'])
@login_required
def delete_contacts():
    data = request.get_json()
    contacts_to_delete = data.get('contacts', [])
    if not contacts_to_delete:
        return jsonify({'error': '未指定要删除的联系人'}), 400
    
    current_contacts = load_config()
    new_contacts = [c for c in current_contacts if c not in contacts_to_delete]
    
    error = save_config(new_contacts)
    if error is True:
        return jsonify({'message': '联系人删除成功'})
    else:
        return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # 获取本机IP地址
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    port = 5001
    
    print(f"\n本地访问地址: http://localhost:{port}")
    print(f"局域网访问地址: http://{local_ip}:{port}\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)
