# auto_stock

본 프로그램은 한국투자증권 API 기반 주식 자동매매 거래 시스템입니다.

config.py  
    
    AUTH_TOKEN, APP_KEY, APP_SECRET, STOCK_LIST 등의 항목을 저장하는 파일입니다.  

    # config.py  
    AUTH_TOKEN = 'str'  
    APP_KEY = 'str'  
    APP_SECRET = 'str'  
    STOCK_LIST = ['str']  

function.py
    - main.py에서 사용할 다양한 함수들을 정의하는 파일입니다.  

    - AuthToken():
        return str: token

    - Headers(str: tr_id):
        return dict: headers

    - RoundNumber(int: number):
        return int: number

    - OpenPrice(list: Stock_list, dict: Open_price, dict: Target_buy_price):  
        return dict: Open_price, dict: Target_buy_price  

    - Liveprice(list: Stock_list, dict: Target_buy_price, dict: Actual_buy_price, dict: Target_sell_price, dict: Actual_sell_price)

    - BuyStock(str: stock, int: target_buy_price)
        return int: actual_buy_price
    
    - SellStock(str: stock, int: target_sell_price)
        return int: actual_sell_price

    - CheckStock(str: stock)
        return True
    
    - CheckBuyStock(str: stock, int: target_buy_price)
        return True

    - 추가 예정

main.py