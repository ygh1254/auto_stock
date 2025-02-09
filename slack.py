from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = ""
client = WebClient(token=slack_token)

def SendMessage(text):
    try:
        response = client.chat_postMessage(
            channel = "C08CSPJ3TU1",
            text = text
        )
    except SlackApiError as e:
        assert e.response["error"]