from chat import direct_chat

print("欢迎使用AI聊天！输入 'exit' 退出对话")

while True:
    # 获取用户输入
    user_input = input("\n你: ").strip()
    
    # 检查是否退出
    if user_input.lower() == 'exit':
        print("再见！")
        break
    
    # 如果输入不为空，获取AI回复
    if user_input:
        response = direct_chat(user_input)
        print(f"\nAI: {response}")
