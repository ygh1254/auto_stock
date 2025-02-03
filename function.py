import requests
import json
import time
from config import AUTH_TOKEN, APP_KEY, APP_SECRET, STOCK_LIST

# 리스트 사전 정의
Stock_list = STOCK_LIST
Open_price = {stock: 0 for stock in Stock_list}
Target_buy_price = {stock: 0 for stock in Stock_list}
Actual_buy_price = {stock: 0 for stock in Stock_list}
Target_sell_price = {stock: 0 for stock in Stock_list}
Actual_sell_price = {stock: 0 for stock in Stock_list}
Quantity = {stock: 0 for stock in Stock_list}
Log = []

# 시가 받아오기 - 09시 1회 실행
def OpenPrice(Stock_list, Open_price, Target_buy_price):
    for stock in Stock_list:
        print(f'Now loading stock {stock}')
        url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
        payload = ""
        headers = {
        'content-type': 'application/json',
        'authorization': AUTH_TOKEN,
        'appkey': APP_KEY,
        'appsecret': APP_SECRET,
        'tr_id': 'FHKST01010100'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        
        '''
        print(response.text)
        {
            "output": {
                "iscd_stat_cls_code": "55",
                "marg_rate": "60.00",
                "rprs_mrkt_kor_name": "KOSPI",
                "bstp_kor_isnm": "증권",
                "temp_stop_yn": "N",
                "oprc_rang_cont_yn": "N",
                "clpr_rang_cont_yn": "N",
                "crdt_able_yn": "Y",
                "stck_prpr": "75900",
                "prdy_vrss": "0",
                "stck_oprc": "75400", # 시가
                "stck_hgpr": "76500",
                "stck_lwpr": "75400",
                "stck_mxpr": "98600",
                "stck_llam": "53200",
                "stck_sdpr": "75900",
                "wghn_avrg_stck_prc": "76021.32",
                "hts_frgn_ehrt": "7.03",
                "per": "8.75",
                "pbr": "0.70",
                # ... 기타 응답 필드 생략 ...
            },
            "rt_cd": "0",
            "msg_cd": "MCA00000",
            "msg1": "정상처리 되었습니다."
        }
        '''
        
        open_price = int(json.loads(response.text)['output']['stck_oprc'])
        Open_price[stock] = open_price
        Target_buy_price[stock] = open_price * 0.95

        #초당 거래 횟수 제한 (2/sec?)
        time.sleep(0.5)
        
    return Open_price, Target_buy_price

# 매수
def BuyStock(stock, Target_buy_price, Actual_buy_price):
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

    payload = json.dumps({
    "CANO": "50124241", # 계좌번호?
    "ACNT_PRDT_CD": "01", #
    "PDNO": stock, # 종목 번호
    "ORD_DVSN": "00", #
    "ORD_QTY": "1", # 수량
    "ORD_UNPR": Target_buy_price[stock] # 매수 가격
    })
    
    headers = {
    'content-type': 'application/json',
    'authorization': AUTH_TOKEN,
    'appkey': APP_KEY,
    'appsecret': APP_SECRET,
    'tr_id': 'VTTC0802U'
    }
    '''
    
    [실전투자]
    TTTC0802U : 주식 현금 매수 주문
    TTTC0801U : 주식 현금 매도 주문

    [모의투자]
    VTTC0802U : 주식 현금 매수 주문
    VTTC0801U : 주식 현금 매도 주문
    '''
    response = requests.request("POST", url, headers=headers, data=payload)

    '''
    print(response.text)
    {
    "rt_cd": "1",
    "msg_cd": "40570000",
    "msg1": "모의투자 장시작전 입니다."
    }
    '''

# 매도
def SellStock(stock, Target_sell_price, Actual_sell_price):
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

    payload = json.dumps({
    "CANO": "50124241", # 계좌번호?
    "ACNT_PRDT_CD": "01", #
    "PDNO": stock, # 종목 번호
    "ORD_DVSN": "00", #
    "ORD_QTY": "1", # 수량
    "ORD_UNPR": Target_sell_price[stock] # 매수 가격
    })
    
    headers = {
    'content-type': 'application/json',
    'authorization': AUTH_TOKEN,
    'appkey': APP_KEY,
    'appsecret': APP_SECRET,
    'tr_id': 'VTTC0801U'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    '''
    print(response.text)
    '''