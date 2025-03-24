import os
from dotenv import load_dotenv
import time
from cozepy import COZE_COM_BASE_URL
from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType  # noqa

# Load environment variables
load_dotenv()

# Get token from environment variable
coze_token = os.getenv('COZE_TOKEN')
print(f"Loaded token: {coze_token}")  # Debug line to see what token is being loaded

if not coze_token:
    raise ValueError("COZE_TOKEN environment variable is not set")

coze = Coze(auth=TokenAuth(coze_token), base_url=COZE_COM_BASE_URL)
chat = coze.chat.create( bot_id='7485415968727121971',user_id="1296079334",additional_messages=[ Message.build_user_question_text("今日AI新闻")] )
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