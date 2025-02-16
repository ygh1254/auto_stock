# auto_stock

본 프로그램은 한국투자증권 API 기반 주식 자동매매 거래 시스템입니다.

config.py  
    
    AUTH_TOKEN, APP_KEY, APP_SECRET, STOCK_LIST 등의 항목을 저장하는 파일입니다.  

    # config.py  
     - AuthToken():
        return str: token
    AUTH_TOKEN = 'str'
    APP_KEY = 'str'  
    APP_SECRET = 'str'  
    STOCK_LIST = ['str']  

real_function.py

    실계좌를 기반으로 main.py에서 사용할 다양한 함수들을 정의하는 파일입니다.

function.py

    모의계좌를 기반으로 main.py에서 사용할 다양한 함수들을 정의하는 파일입니다.  

    - Headers(str: tr_id):
        return dict: headers

    - CatchError(response)

    - RoundNumber(int: number):
        return int: number

    - OpenPrice(list: Stock_list, dict: Open_price, dict: Target_buy_price, dict: Current_Stock):  
        return dict: Open_price, dict: Target_buy_price  

    - Liveprice(list: Stock_list, dict: Target_buy_price, dict: Target_sell_price, dict: Current_Stock)

    - BuyStock(str: stock, int: target_buy_price)
    
    - SellStock(str: stock, int: target_sell_price)

    - CheckStock(dict: Current_stock, dict: Current_account)
        return Current_stock, Current_account
    
    - CheckBuyStock(str: stock, int: target_buy_price)
        return True

slack.py

    Slack의 Bot과 프로그램을 연결하는 파일입니다.

    - SendMessage(str: text)

main.py

    프로그램을 실행하는 파일입니다.