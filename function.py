import requests
import json
import time
import math
from config import APP_KEY, APP_SECRET, STOCK_LIST

# 리스트 사전 정의
Stock_list = STOCK_LIST
Open_price = {stock: 0 for stock in Stock_list}
Target_buy_price = {stock: 0 for stock in Stock_list}
Actual_buy_price = {stock: 0 for stock in Stock_list}
Target_sell_price = {stock: 0 for stock in Stock_list}
Actual_sell_price = {stock: 0 for stock in Stock_list}
Quantity = {stock: 0 for stock in Stock_list}
Log = []

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

# 추후 자동화하여 1일 1회 발급 받는 방향으로 수정
# 1분에 1회 발급 가능
AUTH_TOKEN = AuthToken()

# Header 양식 출력
def Headers(tr_id):
    headers = {
        'content-type': 'application/json',
        'authorization': AUTH_TOKEN,
        'appkey': APP_KEY,
        'appsecret': APP_SECRET,
        'tr_id': tr_id
    }
    return headers

# 호가 간격에 맞게 반올림
def RoundNumber(number):
    if number < 2000:
        return math.floor(number)
    elif number < 5000:
        return 5 * math.floor(number / 5)
    elif number < 20000:
        return 10 * math.floor(number / 10)
    elif number < 50000:
        return 50 * math.floor(number / 50)
    elif number < 200000:
        return 100 * math.floor(number / 100)
    elif number < 500000:
       return 500 * math.floor(number / 500)
    else:
       return 1000 * math.floor(number / 1000)

# 시가 받아오기 - 09시 1회 실행
def OpenPrice(Stock_list, Open_price, Target_buy_price):
    for stock in Stock_list:
        print(f'Now loading stock {stock}')
        url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
        payload = ""
        headers = Headers('FHKST01010100')

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
        target_buy_price = RoundNumber(open_price * 0.95)
        Open_price[stock] = open_price
        Target_buy_price[stock] = target_buy_price

        #초당 거래 횟수 제한 (2/sec?)
        time.sleep(0.5)
        
    return Open_price, Target_buy_price

# 현재가 받아오기
def LivePrice(Stock_List, Target_buy_price, Actual_buy_price, Target_sell_price, Actual_sell_price):
    for stock in Stock_List:
        url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
    
        payload = ""
        
        headers = Headers('FHKST01010100')

        response = requests.request("GET", url, headers=headers, data=payload)

        live_price = int(json.loads(response.text)['output']['stck_prpr'])
        print(live_price, Target_buy_price[stock])
        # 현재가가 목표 매수 가격 이하인 경우 & 주식 수량이 0인 경우
        # 현재 잔고 확인하는 기능 추가할 것
        if (live_price <= Target_buy_price[stock]) & (Quantity[stock] == 0):
            BuyStock(stock, Target_buy_price, Actual_buy_price, Target_sell_price)
        
        # 현재가가 목표 매도 가격 이상인 경우 & 주식 수량이 0이 아닌 경우
        # 현재 잔고 확인하는 기능 추가할 것
        elif (live_price >= Target_sell_price[stock]) & (Quantity[stock] != 0):
            SellStock(stock, Target_sell_price, Actual_sell_price)
        
        time.sleep(0.5)

# 매수
def BuyStock(stock, Target_buy_price, Actual_buy_price, Target_sell_price):
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

    payload = json.dumps({
    "CANO": "50124241", # 계좌번호?
    "ACNT_PRDT_CD": "01", #
    "PDNO": stock, # 종목 번호
    "ORD_DVSN": "00", #
    "ORD_QTY": "1", # 수량
    "ORD_UNPR": Target_buy_price[stock] # 매수 가격
    })
    
    headers = Headers('VTTC0802U')
    
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
    {
    "rt_cd": "0",
    "msg_cd": "40600000",
    "msg1": "모의투자 매수주문이 완료 되었습니다.",
    "output": {
        "KRX_FWDG_ORD_ORGNO": "00950",
        "ODNO": "51378",
        "ORD_TMD": "110840"
        }
    }
    '''
    Actual_buy_price[stock] = Target_buy_price[stock]
    Target_sell_price[stock] = RoundNumber(Actual_buy_price[stock] * 1.03)
    
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
    
    headers = Headers('VTTC0801U')

    response = requests.request("POST", url, headers=headers, data=payload)
    
    '''
    print(response.text)
    '''
    
# 주식 잔고 조회
def CheckStock():
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/inquire-balance?CANO=50124241&ACNT_PRDT_CD=01&AFHR_FLPR_YN=N&OFL_YN=&INQR_DVSN=01&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00&CTX_AREA_FK100=&CTX_AREA_NK100="

    payload = ""
    headers = Headers('VTTC8434R')

    response = requests.request("GET", url, headers=headers, data=payload)
    '''
    {
    "ctx_area_fk100": "                                                                                                    ",
    "ctx_area_nk100": "                                                                                                    ",
    "output1": [
        {
            "pdno": "005930",
            "prdt_name": "삼성전자",
            "trad_dvsn_name": "현금",
            "bfdy_buy_qty": "0",
            "bfdy_sll_qty": "0",
            "thdt_buyqty": "1",
            "thdt_sll_qty": "0",
            "hldg_qty": "1",
            "ord_psbl_qty": "1",
            "pchs_avg_pric": "51000.0000",
            "pchs_amt": "51000",
            "prpr": "51000",
            "evlu_amt": "51000",
            "evlu_pfls_amt": "0",
            "evlu_pfls_rt": "0.00",
            "evlu_erng_rt": "0.00000000",
            "loan_dt": "",
            "loan_amt": "0",
            "stln_slng_chgs": "0",
            "expd_dt": "",
            "fltt_rt": "-2.67000000",
            "bfdy_cprs_icdc": "1400",
            "item_mgna_rt_name": "20%",
            "grta_rt_name": "",
            "sbst_pric": "0",
            "stck_loan_unpr": "0.0000"
        }
    ],
    "output2": [
        {
            "dnca_tot_amt": "10000000",
            "nxdy_excc_amt": "10000000",
            "prvs_rcdl_excc_amt": "9949000",
            "cma_evlu_amt": "0",
            "bfdy_buy_amt": "0",
            "thdt_buy_amt": "51000",
            "nxdy_auto_rdpt_amt": "0",
            "bfdy_sll_amt": "0",
            "thdt_sll_amt": "0",
            "d2_auto_rdpt_amt": "0",
            "bfdy_tlex_amt": "0",
            "thdt_tlex_amt": "0",
            "tot_loan_amt": "0",
            "scts_evlu_amt": "51000",
            "tot_evlu_amt": "10000000",
            "nass_amt": "10000000",
            "fncg_gld_auto_rdpt_yn": "",
            "pchs_amt_smtl_amt": "51000",
            "evlu_amt_smtl_amt": "51000",
            "evlu_pfls_smtl_amt": "0",
            "tot_stln_slng_chgs": "0",
            "bfdy_tot_asst_evlu_amt": "10000000",
            "asst_icdc_amt": "0",
            "asst_icdc_erng_rt": "0.00000000"
        }
    ],
    "rt_cd": "0",
    "msg_cd": "20310000",
    "msg1": "모의투자 조회가 완료되었습니다.                                                 "
    }
    '''
    print(response.text)
    
def CheckBuyStock():
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/inquire-psbl-order?CANO=50124241&ACNT_PRDT_CD=01&PDNO=005930&ORD_UNPR=55000&ORD_DVSN=01&OVRS_ICLD_YN=N&CMA_EVLU_AMT_ICLD_YN=N"

    payload = ""
    headers = {
    'content-type': 'application/json',
    'authorization': AUTH_TOKEN,
    'appkey': APP_KEY,
    'appsecret': APP_SECRET,
    'tr_id': 'VTTC8908R'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    
    '''
    {
    "output": {
        "ord_psbl_cash": "9950000",
        "ord_psbl_sbst": "0",
        "ruse_psbl_amt": "0",
        "fund_rpch_chgs": "0",
        "psbl_qty_calc_unpr": "68100",
        "nrcvb_buy_amt": "9998580",
        "nrcvb_buy_qty": "146",
        "max_buy_amt": "50000000",
        "max_buy_qty": "734",
        "cma_evlu_amt": "0",
        "ovrs_re_use_amt_wcrc": "0",
        "ord_psbl_frcr_amt_wcrc": "0"
    },
    "rt_cd": "0",
    "msg_cd": "20310000",
    "msg1": "모의투자 조회가 완료되었습니다.                                                 "
    }
    '''