from wxauto import WeChat
import time
import sys
import json
import os
import urllib.request
from chat import chatgpt  # 导入chat函数

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'wechat_config.json')

def load_listen_list():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 将监听列表转换为字典，key是名称，value是类型
            global listen_list
            listen_list = {item['name']: item['type'] for item in data}
            print("\n当前监听列表:")
            for name, type_ in listen_list.items():
                print(f"- {name} ({type_})")
            print()  # 空行
    except Exception as e:
        print("加载配置文件失败：", e)
        listen_list = {}

# 获取微信窗口对象
wx = WeChat()
print("初始化成功，获取到已登录窗口")

# 初始化监听列表
listen_list = {}

# 持续监听消息，并且收到消息后回复
wait = 1  # 设置1秒查看一次是否有新消息
config_check_interval = 5  # 每5秒检查一次配置更新
last_config_check = 0

while True:
    current_time = time.time()
    
    # 定期检查配置更新
    if current_time - last_config_check >= config_check_interval:
        load_listen_list()
        last_config_check = current_time
    
    # 处理消息
    msgs = wx.GetListenMessage()
    for chat in msgs:
        who = chat.who              # 获取聊天窗口名（人或群名）
        one_msgs = msgs.get(chat)   # 获取消息内容
        # 回复收到
        for msg in one_msgs:
            # 根据联系人类型判断处理方式
            contact_type = listen_list.get(who)
            print(f"收到消息 - 发送者: {who}, 类型: {contact_type}, 消息类型: {msg.type}, 内容: {msg.content}")  # 调试信息
            
            if contact_type == 'personal' and msg.type == 'friend':
                content = chatgpt(who, msg.content)   # 使用新的chat函数
                print(f'【{who}】：{content}')
                chat.SendMsg(content)  # 回复收到
            elif contact_type == 'group' and msg.type == 'friend' and msg.content.startswith('@'+wx.nickname):
                # 去掉@前缀后的内容
                pure_content = msg.content.replace('@'+wx.nickname, '').strip()
                content = chatgpt(who, pure_content)  # 使用新的chat函数
                print(f'【{who}】：{content}')
                chat.SendMsg(content)
    
    time.sleep(wait)