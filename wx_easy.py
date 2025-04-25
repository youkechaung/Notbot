from wxauto import WeChat
import time
import sys
import json
import os
import requests
from chat import chatgpt  # 导入chat函数
from chat_coze import chat_coze  # 修正导入名称

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'wechat_config.json')


def load_listen_list():
    """加载并更新监听列表"""
    global listen_list  # 添加 global 声明
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        new_listen_list= {item['name']: item['type'] for item in data}
        listen_list_names , new_listen_list_names = set(listen_list.keys()),set(new_listen_list.keys())

        for contact in listen_list_names - new_listen_list_names:
            wx.RemoveListenChat(contact)
            print(f"- 移除监听: {contact}")
        
        # 添加新的监听对象
        for contact in new_listen_list_names - listen_list_names:
            wx.AddListenChat(who=contact, savepic=True)
            print(f"+ 添加监听: {contact}")
        
        listen_list = new_listen_list
# 获取微信窗口对象
wx = WeChat()
print("初始化成功，获取到已登录窗口")
listen_list = {}
load_listen_list()  # 启动时立即加载一次

# 持续监听消息，并且收到消息后回复
wait = 0.1  # 减少主循环等待时间
config_check_interval = 60  # 每60秒检查一次配置
last_config_check = time.time()  # 初始化为当前时间

def download_image(url, save_path):
    """使用requests下载图片"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"下载图片失败: {e}")
        return False

def send_file_with_retry(chat, file_path, max_retries=3, delay=1):
    """带重试机制的文件发送函数"""
    for attempt in range(max_retries):
        try:
            # 检查文件是否存在且可读
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return False

            # 尝试发送文件
            chat.SendFiles([file_path])
            return True
        except Exception as e:
            print(f"发送文件失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    return False

while True:
    current_time = time.time()
    
    # 定期检查配置更新
    if current_time - last_config_check >= config_check_interval:
        load_listen_list()
        last_config_check = current_time
    
    try:
        # 处理消息
        msgs = wx.GetListenMessage()
        for chat in msgs:
            who = chat.who
            one_msgs = msgs.get(chat)
            # 回复收到
            for msg in one_msgs:
                contact_type = listen_list.get(who)
                print(f"收到消息 - 发送者: {who}, 类型: {contact_type}, 消息类型: {msg.type}, 内容: {msg.content}")
                
                # 忽略系统消息
                if contact_type == 'personal' and msg.type == 'friend':
                    content = chat_coze(who, msg.content)
                    print(f'【{who}】：{content}')
                    # 检查是否是图片链接
                    image_base_url = "https://lf-bot-studio-plugin-resource.coze.cn/obj/bot-studio-platform-plugin-tos/artist/image/"
                    if content.startswith(image_base_url):
                        # 创建临时图片目录
                        img_dir = os.path.join(BASE_DIR, 'temp_images')
                        os.makedirs(img_dir, exist_ok=True)
                        # 生成图片文件路径
                        img_name = content.split('/')[-1]
                        img_path = os.path.join(img_dir, img_name)
                        # 下载图片
                        if download_image(content, img_path):
                            # 发送图片（带重试）
                            if not send_file_with_retry(chat, img_path):
                                chat.SendMsg("图片发送失败，请稍后重试")
                        else:
                            chat.SendMsg("图片下载失败，请稍后重试")
                    else:
                        chat.SendMsg(content)
                    break
                elif contact_type == 'group' and msg.type == 'friend' and (msg.content.startswith('@尤闯') or msg.content.startswith('@小尤克隆人')):
                    pure_content = msg.content.replace('@'+wx.nickname, '').strip()
                    content = chat_coze(who, pure_content)
                    print(f'【{who}】：{content}')
                    # 检查是否是图片链接
                    image_base_url = "https://lf-bot-studio-plugin-resource.coze.cn/obj/bot-studio-platform-plugin-tos/artist/image/"
                    if content.startswith(image_base_url):
                        # 创建临时图片目录
                        img_dir = os.path.join(BASE_DIR, 'temp_images')
                        os.makedirs(img_dir, exist_ok=True)
                        # 生成图片文件路径
                        img_name = content.split('/')[-1]
                        img_path = os.path.join(img_dir, img_name)
                        # 下载图片
                        if download_image(content, img_path):
                            # 发送图片（带重试）
                            if not send_file_with_retry(chat, img_path):
                                chat.SendMsg("图片发送失败，请稍后重试")
                        else:
                            chat.SendMsg("图片下载失败，请稍后重试")
                    else:
                        chat.SendMsg(content)
                    break
    except Exception as e:
        print(f"处理消息时出错: {e}")
    
    time.sleep(wait)