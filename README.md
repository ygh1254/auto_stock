# auto_stock

본 프로그램은 한국투자증권 API 기반 주식 자동매매 거래 시스템입니다.

config.py  
    
    AUTH_TOKEN, APP_KEY, APP_SECRET, STOCK_LIST 등의 항목을 저장하는 파일입니다.  

    ```
    # config.py  
    AUTH_TOKEN = 'str'  
    APP_KEY = 'str'  
    APP_SECRET = 'str'  
    STOCK_LIST = ['str']  
    ```

function.py
    - main.py에서 사용할 다양한 함수들을 정의하는 파일입니다.  

    - OpenPrice(list: Stock_list, dict: Open_price, dict: Target_buy_price):  
        return dict: Open_price, dict: Target_buy_price  

    - 추가 예정

main.py