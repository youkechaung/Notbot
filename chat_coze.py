import os  # noqa
import time
import os
import time


from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa



coze_api_token = "pat_ZAFMqFvKzXvHdklRxv06v3x0h33AtLCCfiztguB0Mn4HD2GvWpKdgAz905LyWlKC"
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url= COZE_COM_BASE_URL)
user_id = "1111" 
bot_id="7484017939638124563"
chat = coze.chat.create(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            Message.build_user_question_text("今日AI新闻")
        ],
    )
start = int(time.time())
timeout = 600
while chat.status == ChatStatus.IN_PROGRESS:
    if int(time.time()) - start > timeout:
        # too long, cancel chat
        coze.chat.cancel(conversation_id=chat.conversation_id, chat_id=chat.id)
        break

    time.sleep(1)
    chat = coze.chat.retrieve(conversation_id=chat.conversation_id, chat_id=chat.id)

messages = coze.chat.messages.list(conversation_id=chat.conversation_id, chat_id=chat.id)
for message in messages:
    print(f"role={message.role}, content={message.content}")