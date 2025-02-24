import os
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
# from config import *
from config import OPEN_AI, SLACK_BOT_TOKEN, SLACK_APP_TOKEN
# from real_config import *
from openai import OpenAI

OpenAI.api_key = OPEN_AI

slack_client = WebClient(token=SLACK_BOT_TOKEN)
# openai_client = OpenAI(api_key=OPEN_AI)

def SendMessage(text):
    try:
        response = slack_client.chat_postMessage(
            channel = "C08CSPJ3TU1",
            text = text
        )
    except SlackApiError as e:
        assert e.response["error"]

# Install the Slack app and get xoxb- token in advance
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
    # stream = openai_client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[{"role": "user", "content": "Say this is a test"}],
    #     stream=True,
    # )
    # for chunk in stream:
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()

# 현재 등록된 주식 전송
# 주식 추가 등록
# 주식 삭제