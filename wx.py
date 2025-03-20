# -*- coding: utf-8 -*-
import sys
from wxauto import WeChat
import time
import urllib.request
import json

# 设置控制台输出编码
sys.stdout.reconfigure(encoding='utf-8')

def get_kimi_response(message, api_key):
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
        return None

def auto_reply(api_key):
    print("自动回复程序已启动...")
    wx = WeChat()
    last_msg = {}
    
    while True:
        try:
            # 获取所有会话
            sessions = wx.GetSessionList()
            if not sessions:
                time.sleep(1)
                continue
                
            # 遍历每个会话
            for session in sessions:
                try:
                    # 切换到会话
                    wx.ChatWith(session)
                    time.sleep(0.5)  # 等待切换
                    
                    # 获取最新消息
                    current_msg = wx.GetLastMessage()
                    if not current_msg:
                        continue
                        
                    # 转换成字符串并清理
                    msg_text = str(current_msg).strip()
                    if not msg_text:
                        continue
                        
                    # 如果是新消息且不是自己发的
                    if (session not in last_msg or msg_text != last_msg[session]) and not msg_text.startswith("我："):
                        print(f"收到新消息 - {session}: {msg_text}")
                        
                        # 获取回复
                        reply = get_kimi_response(f"请回复这条消息：{msg_text}", api_key)
                        if reply:
                            # 发送回复
                            wx.SendMsg(reply)
                            print(f"已回复 - {session}: {reply}")
                            last_msg[session] = msg_text  # 更新最后一条消息
                            time.sleep(1)  # 等待发送完成
                
                except Exception as e:
                    print(f"处理会话 {session} 时出错: {e}")
                    continue
                    
            time.sleep(1)  # 主循环暂停
            
        except Exception as e:
            print(f"程序错误: {e}")
            time.sleep(3)

if __name__ == "__main__":
    print("微信自动回复程序 v1.0")
    print("请输入你的 Kimi API Key：")
    api_key = input().strip()
    
    if not api_key:
        print("错误：API Key 不能为空")
        sys.exit(1)
        
    print("\n程序启动中...")
    print("提示：按 Ctrl+C 可以停止程序")
    
    try:
        auto_reply(api_key)
    except KeyboardInterrupt:
        print("\n程序已停止")