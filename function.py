import requests
import json
import time
import math
import logging
from slack import *
from config import AUTH_TOKEN, APP_KEY, APP_SECRET, STOCK_LIST

logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %p %I:%M:%S')
logger = logging.getLogger('function')
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log')
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.debug('DEBUG')
logger.info('INFO')
logger.warning('WARNING')
logger.error('ERROR')
logger.critical('CRITICAL')

# 리스트 사전 정의
Stock_list = STOCK_LIST
Open_price = {stock: 0 for stock in Stock_list}
Target_buy_price = {stock: 0 for stock in Stock_list}
Target_sell_price = {stock: 0 for stock in Stock_list}
Current_stock = {stock: {'pdno': {stock}, # 종목 번호
                        'prdt_name': {stock}, # 종목 이름
                        'hldg_qty': '0', # 보유 수량
                        'ord_psbl_qty': '0', # 주문 가능 수량
                        'pchs_avg_pric': '0', # 매입 평균 가격
                        'prpr': '0', # 현재가
                        'evlu_amt': '0', # 평가금액
                        'evlu_pfls_amt': '0', # 수익
                        'evlu_pfls_rt': '0' # 수익률
                        } for stock in Stock_list}
Current_account = {'dnca_tot_amt': '', # 예수금 총 금액
                    'nxdy_excc_amt': '', # 익일 정산 금액
                    'prvs_rcdl_excc_amt': '', # 가수도 정산 금액
                    'thdt_buy_amt': '', # 금일 매수 금액
                    'thdt_sll_amt': '', # 금일 매도 금액
                    'tot_evlu_amt': '', # 총 평가 금액
                    'nass_amt': '', # 순 자산 금액
                    'asst_icdc_amt': '', # 자산 증감액
                    'asst_icdc_erng_rt': '', # 자산 증감 수익률
                    }

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

def CatchError(response):
    try:
        response.raise_for_status()
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"연결 오류 발생: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"타임아웃 오류 발생: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"요청 오류 발생: {req_err}")

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
def OpenPrice(Stock_list, Open_price, Target_buy_price, Current_stock):
    
    SendMessage("프로그램을 시작합니다.")
    
    for stock in Stock_list:
        print(f'{Current_stock[stock]['prdt_name']}  정보를 가져옵니다')
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
def LivePrice(Stock_list, Target_buy_price, Target_sell_price, Current_stock):
    for stock in Stock_list:
        url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
    
        payload = ""

        headers = Headers('FHKST01010100')

        response = requests.request("GET", url, headers=headers, data=payload)
        CatchError(response)
        
        live_price = int(json.loads(response.text)['output']['stck_prpr'])
        target_buy_price = Target_buy_price[stock]
        target_sell_price = Target_sell_price[stock]
        
        print(f"{Current_stock[stock]['prdt_name']} 목표구매가격 {target_buy_price}원, 시가 {live_price}원")
        print(f"{Current_stock[stock]['prdt_name']} 목표판매가격 {target_sell_price}원, 시가 {live_price}원")
        print("-----------------------------------------------------------")
        
        # Current_stock[stock]['ord_psbl_qty']가 0인 경우 구매 조건식 확인
        if Current_stock[stock]['ord_psbl_qty'] == 0:
            # 시가가 목표 매수가 이하
            if (live_price <= target_buy_price):
                time.sleep(0.5)
                BuyStock(stock, target_buy_price)
                CheckStock()
                
                Target_sell_price[stock] = RoundNumber(Current_stock[stock]['pchs_avg_pric'] * 1.03)
        
        # Current_stock[stock]['ord_psbl_qty']가 0이 아닌 경우 판매 조건식 확인
        else :
            # target_sell_price가 0인 경우 초기화 값이므로 실행하지 않음
            if (target_sell_price != 0) & (live_price >= target_sell_price):
                time.sleep(0.5)
                SellStock(stock, target_sell_price)
                CheckStock()
        
        time.sleep(0.5)

    print(Current_account)

# 매수
def BuyStock(stock, target_buy_price):
    
    if CheckBuyStock(stock, target_buy_price):
        
        url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

        payload = json.dumps({
        "CANO": "50124241", # 계좌번호?
        "ACNT_PRDT_CD": "01", #
        "PDNO": stock, # 종목 번호
        "ORD_DVSN": "00", #
        "ORD_QTY": "1", # 수량
        "ORD_UNPR": str(target_buy_price) # 매수 가격
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
        CatchError(response)
        
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
 
        text = f"{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime)} | {stock}을 {target_buy_price}원에 구매합니다"
        SendMessage(text)
        
        return print(f"{stock}을 구매합니다")
    
# 매도
def SellStock(stock, target_sell_price):
        
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/order-cash"

    payload = json.dumps({
    "CANO": "50124241", # 계좌번호?
    "ACNT_PRDT_CD": "01", #
    "PDNO": stock, # 종목 번호
    "ORD_DVSN": "00", #
    "ORD_QTY": "1", # 수량
    "ORD_UNPR": str(target_sell_price) # 매수 가격
    })
    
    headers = Headers('VTTC0801U')

    response = requests.request("POST", url, headers=headers, data=payload)
    CatchError(response)

    text = f"{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime)} | {stock}을 {target_sell_price}원에 판매합니다"
    SendMessage(text)
    
    return print(f"{stock}을 판매합니다")
    
# 주식 잔고 조회
def CheckStock(Current_stock, Current_account):
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/inquire-balance?CANO=50124241&ACNT_PRDT_CD=01&AFHR_FLPR_YN=N&OFL_YN=&INQR_DVSN=01&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00&CTX_AREA_FK100=&CTX_AREA_NK100="

    payload = ""
    headers = Headers('VTTC8434R')

    response = requests.request("GET", url, headers=headers, data=payload)
    CatchError(response)
    
    current_stock = json.loads(response.text)['output1']

    # {'pdno': '005930', 'prdt_name': '삼성전자', 'trad_dvsn_name': '현금', 'bfdy_buy_qty': '0', 'bfdy_sll_qty': '0', 'thdt_buyqty': '0', 'thdt_sll_qty': '0', 'hldg_qty': '1', 'ord_psbl_qty': '1', 'pchs_avg_pric': '51000.0000', 'pchs_amt': '51000', 'prpr': '53800', 'evlu_amt': '53800', 'evlu_pfls_amt': '2800', 'evlu_pfls_rt': '5.49', 'evlu_erng_rt': '5.49019608', 'loan_dt': '', 'loan_amt': '0', 'stln_slng_chgs': '0', 'expd_dt': '', 'fltt_rt': '-0.37000000', 'bfdy_cprs_icdc': '200', 'item_mgna_rt_name': '20%', 'grta_rt_name': '', 'sbst_pric': '0', 'stck_loan_unpr': '0.0000'}
    # {'pdno': '010955', 'prdt_name': 'S-Oil우', 'trad_dvsn_name': '현금', 'bfdy_buy_qty': '7', 'bfdy_sll_qty': '0', 'thdt_buyqty': '0', 'thdt_sll_qty': '0', 'hldg_qty': '7', 'ord_psbl_qty': '7', 'pchs_avg_pric': '39550.0000', 'pchs_amt': '276850', 'prpr': '39100', 'evlu_amt': '273700', 'evlu_pfls_amt': '-3150', 'evlu_pfls_rt': '-1.14', 'evlu_erng_rt': '-1.13780025', 'loan_dt': '', 'loan_amt': '0', 'stln_slng_chgs': '0', 'expd_dt': '', 'fltt_rt': '-1.14000000', 'bfdy_cprs_icdc': '450', 'item_mgna_rt_name': '50%', 'grta_rt_name': '', 'sbst_pric': '0', 'stck_loan_unpr': '0.0000'}

    current_account = json.loads(response.text)['output2']

    # [{'dnca_tot_amt': '9949000', 'nxdy_excc_amt': '9672120', 'prvs_rcdl_excc_amt': '9672120', 'cma_evlu_amt': '0', 'bfdy_buy_amt': '276850', 'thdt_buy_amt': '0', 'nxdy_auto_rdpt_amt': '0', 'bfdy_sll_amt': '0', 'thdt_sll_amt': '0', 'd2_auto_rdpt_amt': '0', 'bfdy_tlex_amt': '30', 'thdt_tlex_amt': '0', 'tot_loan_amt': '0', 'scts_evlu_amt': '327500', 'tot_evlu_amt': '9999620', 'nass_amt': '9999620', 'fncg_gld_auto_rdpt_yn': '', 'pchs_amt_smtl_amt': '327850', 'evlu_amt_smtl_amt': '327500', 'evlu_pfls_smtl_amt': '-350', 'tot_stln_slng_chgs': '0', 'bfdy_tot_asst_evlu_amt': '10002970', 'asst_icdc_amt': '-3350', 'asst_icdc_erng_rt': '-0.03349005'}]
    
    for item in current_stock:
        Current_stock[item['pdno']] = {'pdno': item['pdno'], # 종목 번호
                                 'prdt_name': item['prdt_name'], # 종목 이름
                                 'hldg_qty': item['hldg_qty'], # 보유 수량
                                 'ord_psbl_qty': item['ord_psbl_qty'], # 주문 가능 수량
                                 'pchs_avg_pric': item['pchs_avg_pric'], # 매입 평균 가격
                                 'prpr': item['prpr'], # 현재가
                                 'evlu_amt': item['evlu_amt'], # 평가금액
                                 'evlu_pfls_amt': item['evlu_pfls_amt'], # 수익
                                 'evlu_pfls_rt': item['evlu_pfls_rt'] # 수익률
                                 }
        
        text = (f"------------------------\n종목번호: {item['pdno']},\n 종목이름: {item['prdt_name']},\n 보유수량:{item['hldg_qty']},\n 주문가능수량:{item['ord_psbl_qty']},\n 매입평균가격:{item['pchs_avg_pric']},\n 현재가:{item['prpr']},\n 평가금액:{item['evlu_amt']},\n 수익:{item['evlu_pfls_amt']},\n 수익률:{item['evlu_pfls_rt']}%")
        SendMessage(text)
        
    for item in current_account:
        Current_account = {'dnca_tot_amt': item['dnca_tot_amt'], # 예수금 총 금액
                        'nxdy_excc_amt':item['nxdy_excc_amt'], # 익일 정산 금액
                        'prvs_rcdl_excc_amt':item['prvs_rcdl_excc_amt'], # 가수도 정산 금액
                        'thdt_buy_amt':item['thdt_buy_amt'], # 금일 매수 금액
                        'thdt_sll_amt':item['thdt_sll_amt'], # 금일 매도 금액
                        'tot_evlu_amt':item['tot_evlu_amt'], # 총 평가 금액
                        'nass_amt':item['nass_amt'], # 순 자산 금액
                        'asst_icdc_amt':item['asst_icdc_amt'], # 자산 증감액
                        'asst_icdc_erng_rt':item['asst_icdc_erng_rt'], # 자산 증감 수익률
                        }
        
        text = (f"------------------------\n예수금총금액:{item['dnca_tot_amt']},\n 금일매수금액:{item['thdt_buy_amt']},\n 금일매도금액:{item['thdt_sll_amt']},\n 총평가금액:{item['tot_evlu_amt']},\n 자산증감액:{item['asst_icdc_amt']},\n 자산증감수익률:{item['asst_icdc_erng_rt']}%")
        SendMessage(text)
        
    time.sleep(0.5)
    
    return Current_stock, Current_account

# 주식 매수 가능 여부 조회
def CheckBuyStock(stock, target_buy_price):
    url = f"https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/trading/inquire-psbl-order?CANO=50124241&ACNT_PRDT_CD=01&PDNO={stock}&ORD_UNPR={target_buy_price}&ORD_DVSN=01&OVRS_ICLD_YN=N&CMA_EVLU_AMT_ICLD_YN=N"

    payload = ""
    headers = {
    'content-type': 'application/json',
    'authorization': AUTH_TOKEN,
    'appkey': APP_KEY,
    'appsecret': APP_SECRET,
    'tr_id': 'VTTC8908R'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    CatchError(response)
    
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
    
    return True