import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
# from config import *
from config import OPEN_AI, SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SYSTEM_COMMAND
from real_config import *
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

@app.event("app_mention")
def open_ai_event(say, event):
    # 'text': '<@~~> Hello'
    text = re.sub(r'<@[^>]+>', '', event["text"]).strip()

    say(f"{text} 요청을 수행합니다")
    
    tools = [
    {
        "type": "function",
        "function": {
            "name": "CurrentStock",
            "description": "Check current status of stock account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Request user entered."
                    },
                },
                "required": ["request"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "CurrentAccount",
            "description": "Check current status of account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Request user entered."
                    },
                },
                "required": ["request"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "RegisterStock",
            "description": "Register a stock using product name of the stock as a input. properties are automatically matched by you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdno": {
                        "type": "string",
                        "description": "Product number of the stock."
                    },
                    "prdt_abrv_name": {
                        "type": "string",
                        "description": "Product name of the stock."
                    },
                },
                "required": [
                    "pdno",
                    "prdt_abrv_name",
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "RemoveStock",
            "description": "Remove a stock using product name of the stock as a input. properties are automatically matched by you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdno": {
                        "type": "string",
                        "description": "Product number of the stock."
                    },
                    "prdt_abrv_name": {
                        "type": "string",
                        "description": "Product name of the stock."
                    },
                },
                "required": [
                    "pdno",
                    "prdt_abrv_name",
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    },
        {
        "type": "function",
        "function": {
            "name": "StockList",
            "description": "Check list of stock in stock_list user interested in.",
            "parameters": {
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Request user entered."
                    },
                },
                "required": ["request"],
                "additionalProperties": False
            },
            "strict": True
        }
    }]

    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "developer", "content": SYSTEM_COMMAND},
                  {"role": "user", "content": text}],
        tools=tools
    )
    
    print(completion.choices[0])
    
    if completion.choices[0].message.content is None:
        function_name = completion.choices[0].message.tool_calls[0].function.name
        arguments = json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
        
        if function_name == 'CurrentStock':
            say(PrintCurrentStock())
        if function_name == 'CurrentAccount':
            say(PrintCurrentAccount())
        if function_name == 'RegisterStock':
            say(RegisterStock(arguments['pdno']))
        if function_name == 'RemoveStock':
            say(RemoveStock(arguments['pdno']))
        if function_name == 'StockList':
            say(f'현재 등록된 주식 목록입니다.')
            for item in ReadStockList():
                say(item)
        
    else :
        say(completion.choices[0].message.content)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()