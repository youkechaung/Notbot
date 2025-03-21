from wxauto import WeChat
import time
import sys
import json
import os
import urllib.request

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'wechat_config.json')

def get_kimi_response(message):
    api_key = "sk-yIkBArpEqL1qpI3vj5p0vh0dR1Z6BI7YaBRnTmdVDvho3cYH"
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "moonshot-v1-8k",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    while True:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"API调用错误: {e}")
            print("等待30秒后重试...")
            time.sleep(30)

def load_listen_list():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取配置文件错误: {e}")
            return []
    return []

# 获取微信窗口对象
wx = WeChat()
print("初始化成功，获取到已登录窗口")

# 初始化监听列表
current_listen_list = set()

# 持续监听消息，并且收到消息后回复
wait = 1  # 设置1秒查看一次是否有新消息
config_check_interval = 5  # 每5秒检查一次配置更新
last_config_check = 0

while True:
    current_time = time.time()
    
    # 定期检查配置更新
    if current_time - last_config_check >= config_check_interval:
        new_listen_list = set(load_listen_list())
        
        # 如果列表有变化
        if new_listen_list != current_listen_list:
            print("检测到监听列表更新:")
            # 移除不再监听的对象
            for contact in current_listen_list - new_listen_list:
                wx.RemoveListenChat(contact)
                print(f"- 移除监听: {contact}")
            
            # 添加新的监听对象
            for contact in new_listen_list - current_listen_list:
                wx.AddListenChat(who=contact, savepic=True)
                print(f"+ 添加监听: {contact}")
            
            current_listen_list = new_listen_list
        
        last_config_check = current_time
    
    # 处理消息
    msgs = wx.GetListenMessage()
    for chat in msgs:
        who = chat.who              # 获取聊天窗口名（人或群名）
        one_msgs = msgs.get(chat)   # 获取消息内容
        # 回复收到
        for msg in one_msgs:
            if msg.type == 'friend':
                content = get_kimi_response(msg.content)   # 获取消息内容，字符串类型的消息内容
                print(f'【{who}】：{content}')
                chat.SendMsg(content)  # 回复收到
    
    time.sleep(wait)