import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
# from config import *
from config import OPEN_AI, SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SYSTEM_COMMAND
# from real_config import *
from openai import OpenAI

OpenAI.api_key = OPEN_AI

slack_client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI(api_key=OPEN_AI)

def SendMessage(text):
    try:
        response = slack_client.chat_postMessage(
            channel = "C08CSPJ3TU1",
            text = text
        )
    except SlackApiError as e:
        assert e.response["error"]

app = App(token=SLACK_BOT_TOKEN)

@app.command("/request")
def request_command(ack, body):
    text = body["text"]
    user_id = body["user_id"]
    ack(f"Hi, <@{user_id}>!")

@app.event("app_mention")
def open_ai_event(say, event):
    # 'text': '<@~~> Hello'
    text = re.sub(r'<@[^>]+>', '', event["text"]).strip()

    say(f"{text} 요청을 수행합니다")
    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "developer", "content": SYSTEM_COMMAND},
                  {"role": "user", "content": text}],
    )
    
    say(stream.choices[0].message.content)
    
    # ChatCompletionMessage(content='삼성전자(005390)가 주식 목록에 등록되었습니다.', refusal=None, role='assistant', audio=None, function_call=None, tool_calls=None)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()