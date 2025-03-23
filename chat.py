from openai import OpenAI
import json
import os
import time
from datetime import datetime

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, 'chat_history.json')

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-yIkBArpEqL1qpI3vj5p0vh0dR1Z6BI7YaBRnTmdVDvho3cYH",  # 替换为你的 Kimi API Key
    base_url="https://api.moonshot.cn/v1",
)

# 存储每个用户的对话历史
conversations = {}

def load_history():
    """从文件加载聊天历史"""
    global conversations
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            print(f"已加载{len(conversations)}个用户的聊天记录")
        except Exception as e:
            print(f"加载聊天记录失败: {e}")
            conversations = {}

def save_history():
    """保存聊天历史到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存聊天记录失败: {e}")

def cleanup_old_messages(messages, max_messages=50):
    """清理旧消息，只保留最近的max_messages条"""
    if len(messages) > max_messages:
        # 保留system消息和最近的消息
        system_messages = [msg for msg in messages if msg['role'] == 'system']
        recent_messages = messages[-max_messages:]
        return system_messages + recent_messages
    return messages

# 初始加载历史记录
load_history()

def chatgpt(user_id, query):
    # 如果用户第一次对话，初始化其对话历史
    if user_id not in conversations:
        conversations[user_id] = {
            'messages': [
                {"role": "system", "content": "你是现实世界的一个正常人，礼貌、友善、理智。"}
            ],
            'last_interaction': datetime.now().isoformat()
        }
    
    # 更新最后交互时间
    conversations[user_id]['last_interaction'] = datetime.now().isoformat()
    
    # 将用户的问题添加到对话历史中
    conversations[user_id]['messages'].append({"role": "user", "content": query})
    
    # 清理旧消息
    conversations[user_id]['messages'] = cleanup_old_messages(conversations[user_id]['messages'])
    
    try:
        # 调用 Kimi API 获取回复
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=conversations[user_id]['messages'],
            temperature=0.3,
        )
        
        # 获取模型的回复
        response = completion.choices[0].message.content
        
        # 将模型的回复添加到对话历史中
        conversations[user_id]['messages'].append({"role": "assistant", "content": response})
        
        # 保存更新后的历史记录
        save_history()
        
        return response
    except Exception as e:
        print(f"API调用错误: {e}")
        return "抱歉，我现在无法回答，请稍后再试。"
