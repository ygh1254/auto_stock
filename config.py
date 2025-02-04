import json
import requests

def AuthToken():
    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    payload = json.dumps({
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
    })
    
    headers = {
    'content-type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    '''
    print(response.text)
    {"access_token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjBkODA0NjIxLTc5MTQtNDgyZS04Njg2LTQzMjhkNDcwZDYxOSIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTczODczMDM0MCwiaWF0IjoxNzM4NjQzOTQwLCJqdGkiOiJQU3ptVWFIa0c2WWphVUxSUGx0NGd4dVpva0h5SXVUeXRvZkQifQ.d4kXToN2VfayMB0hnn9VKbHURYFWPTVN-TjK-6uDc--PqdvX6yeomJ9QYLTqpHz-rf_Hh9vkBbWPdWPZUceq0g",
    "access_token_token_expired":"2025-02-05 13:39:00",
    "token_type":"Bearer",
    "expires_in":86400}
    '''
    
    token = f"{json.loads(response.text)['token_type']} {json.loads(response.text)['access_token']}"
    
    return token

# API 인증 정보
AUTH_TOKEN = AuthToken()
APP_KEY = ''
APP_SECRET = ''
STOCK_LIST = []