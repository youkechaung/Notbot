# 导入
from wxauto import WeChat
import time
import sys
import time
import urllib.request
import json

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

# 获取微信窗口对象
wx = WeChat()
# 输出 > 初始化成功，获取到已登录窗口：xxxx

# 设置监听列表
listen_list = ['Rafael','You','Chloe李李💫','火星前夜','教授们','事事如意']
# 循环添加监听对象
for i in listen_list:
    wx.AddListenChat(who=i, savepic=True)

# 持续监听消息，并且收到消息后回复“收到”
wait = 1  # 设置1秒查看一次是否有新消息
while True:
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