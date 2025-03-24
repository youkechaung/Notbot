from wxauto import WeChat
import time
import sys
import json
import os
import urllib.request
from chat import chatgpt  # 导入chat函数
# from chat_coze import chatcoze

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
wait = 1  # 设置1秒查看一次是否有新消息
config_check_interval = 3  # 每5秒检查一次配置更新
last_config_check = time.time()  # 初始化为当前时间

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
            who = chat.who              # 获取聊天窗口名（人或群名）
            one_msgs = msgs.get(chat)   # 获取消息内容
            # 回复收到
            for msg in one_msgs:
                # 根据联系人类型判断处理方式
                contact_type = listen_list.get(who)
                print(f"收到消息 - 发送者: {who}, 类型: {contact_type}, 消息类型: {msg.type}, 内容: {msg.content}")  # 调试信息
                print(f"当前监听列表: {listen_list}")  # 添加这行来显示监听列表的内容
                
                # 忽略系统消息
                if contact_type == 'personal' and msg.type == 'friend':
                    content = chatgpt(who, msg.content)   # 使用新的chat函数
                    print(f'【{who}】：{content}')
                    chat.SendMsg(content)  # 回复收到
                    break
                elif contact_type == 'group' and msg.type == 'friend' and (msg.content.startswith('@尤闯') or msg.content.startswith('@小尤克隆人')):
                    # 去掉@前缀后的内
                    pure_content = msg.content.replace('@'+wx.nickname, '').strip()
                    content = chatgpt(who, pure_content)  # 使用新的chat函数
                    print(f'【{who}】：{content}')
                    chat.SendMsg(content)
                    break
    except Exception as e:
        print(f"处理消息时出错: {e}")
    
    time.sleep(wait)