import os  # noqa
import time
import json
from datetime import datetime

from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType,COZE_CN_BASE_URL # noqa

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, 'chat_history.json')

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
        # 使用临时文件写入，然后重命名，避免文件损坏
        temp_file = HISTORY_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False)
        os.replace(temp_file, HISTORY_FILE)
    except Exception as e:
        print(f"保存聊天记录失败: {e}")

def cleanup_old_messages(messages, max_messages=6):
    """清理旧消息，只保留最近的max_messages条对话（不包括system消息）"""
    # 分离system消息和其他消息
    system_messages = [msg for msg in messages if msg['role'] == 'system']
    other_messages = [msg for msg in messages if msg['role'] != 'system'][-max_messages:]
    return system_messages + other_messages

def clean_response(response):
    """清理响应文本，如果包含图片链接则只返回链接"""
    import re
    
    # 查找 Coze 图片链接
    image_base_url = "https://lf-bot-studio-plugin-resource.coze.cn/obj/bot-studio-platform-plugin-tos/artist/image/"
    if image_base_url in response:
        # 提取完整的图片URL
        pattern = f"{image_base_url}[a-zA-Z0-9]+\.png"
        matches = re.findall(pattern, response)
        if matches:
            return matches[0]  # 返回第一个匹配的完整URL
    
    return response.strip()

# 初始化 Coze 客户端
coze = Coze(auth=TokenAuth('pat_JJQZ6rSiGyZvVOoSZqtD4Q8HjC5zZ2vRK8hxAxVNMAyGc6WG7o0R9p2UvXBQI88t'), base_url=COZE_CN_BASE_URL)

# 初始加载历史记录
load_history()

def chat_coze(user_id, query):
    if user_id not in conversations:
        conversations[user_id] = {
            'messages': [
                {"role": "system", "content": "你是现实世界的一个正常人，礼貌、友善、理智.用普通文本回答，不要用markdown"}
            ],
            'last_interaction': datetime.now().isoformat()
        }
    
    # 更新最后交互时间
    conversations[user_id]['last_interaction'] = datetime.now().isoformat()
    
    # 清理旧消息，减少历史消息数量
    conversations[user_id]['messages'] = cleanup_old_messages(conversations[user_id]['messages'])
    
    try:
        # 构建历史消息列表，直接在列表推导中构建Message对象
        history_messages = [
            Message.build_user_question_text(msg['content']) if msg['role'] == 'user'
            else Message.build_assistant_answer(msg['content'])
            for msg in conversations[user_id]['messages']
            if msg['role'] != 'system'
        ][-6:]
        
        # 添加当前问题
        history_messages.append(Message.build_user_question_text(query))
        conversations[user_id]['messages'].append({"role": "user", "content": query})

        # 创建新的对话并获取回复
        chat_poll = coze.chat.create_and_poll(
            bot_id='7485175251215941682',
            user_id=user_id,
            additional_messages=history_messages,
        )

        # 处理回复
        for message in chat_poll.messages:
            if not (message.content.startswith('{"') or message.content.endswith("}")):
                response = clean_response(message.content)
                conversations[user_id]['messages'].append({"role": "assistant", "content": response})
                # 异步保存历史记录
                save_history()
                return response

        return "抱歉，我现在无法回答，请稍后再试。"

    except Exception as e:
        print(f"API调用错误: {e}")
        return "抱歉，我现在无法回答，请稍后再试。"