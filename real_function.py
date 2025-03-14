import requests
import json
import time
import math
import logging
from datetime import date
from slack import *
from real_config import *

logging.basicConfig(filename=f'{date.today()}.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d/ %p %I:%M:%S')
logger = logging.getLogger('function')
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f'{date.today()}.log')
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 리스트 사전 정의
Stock_list = STOCK_LIST
Open_price = {stock: 0 for stock in Stock_list}
Target_buy_price = {stock: 0 for stock in Stock_list}
Target_sell_price = {stock: 0 for stock in Stock_list}

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
        logger.error(f"HTTP 오류 발생: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"연결 오류 발생: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"타임아웃 오류 발생: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"요청 오류 발생: {req_err}")

# 호가 간격에 맞게 반올림
def RoundNumber(number):
    number = float(number)
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
    
    SendMessage("실전투자 프로그램을 시작합니다.")
    logging.debug("실전투자 프로그램을 시작합니다")
    
    stock_list = {}
    
    for stock in Stock_list:
        logging.debug(f'{stock} 정보를 가져옵니다')
        url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
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
        
        stock_list[stock] = CheckStockInfo(stock)
        
    SaveJson(stock_list, 'stock_list.json')
        
    return Open_price, Target_buy_price

# 현재가 받아오기
def LivePrice(Stock_list, Target_buy_price, mode):
    logger.debug(f"{mode} 모드 동작 중")
    
    current_stock = LoadJson('current_stock.json')
    stock_list = LoadJson('stock_list.json')
    for stock in Stock_list:
        url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/inquire-price?fid_cond_mrkt_div_code=J&fid_input_iscd={stock}"
    
        payload = ""

        headers = Headers('FHKST01010100')

        response = requests.request("GET", url, headers=headers, data=payload)
        CatchError(response)
        
        live_price = int(json.loads(response.text)['output']['stck_prpr'])
        target_buy_price = Target_buy_price[stock]
        
        logger.debug("-----------------------------------------------------------")
        logger.debug(f"{stock_list[stock]['prdt_name']} 목표구매가격 {target_buy_price}원, 시가 {live_price}원")
        logger.debug("-----------------------------------------------------------")
        
        time.sleep(0.5)
        
        # current_stock에 stock이 없는 경우 = 보유 주식이 없는 경우
        if stock not in current_stock:
            logger.debug(f'{stock} is not in currnet stock')
            if (mode == 'normal') & BuyCondition(live_price, target_buy_price):
                time.sleep(0.5)
                BuyStock(stock, target_buy_price)
                CheckStock()
                current_stock = LoadJson('current_stock.json')
            
            # 동시호가 진행 시 매수 주문
            if (mode == 'auction'):
                time.sleep(0.5)
                BuyStock(stock, RoundNumber(live_price * 0.95))
                CheckStock()
                current_stock = LoadJson('current_stock.json')
        
        # current_stock에 stock이 없는 경우 and 주문 가능 수량이 존재하는 경우
        elif current_stock[stock]['ord_psbl_qty'] != '0':
            avarage_price = float(current_stock[stock]['pchs_avg_pric'])
            # 매수 가격 기준 3% 수익률
            SellStock(stock, RoundNumber(avarage_price * 1.03))
            CheckStock()
            current_stock = LoadJson('current_stock.json')
# 매수
def BuyStock(stock, target_buy_price):
    
    if CheckBuyStock(stock, target_buy_price):
        
        url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash"

        payload = json.dumps({
        "CANO": "68579062", # 계좌번호
        "ACNT_PRDT_CD": "01", #
        "PDNO": stock, # 종목 번호
        "ORD_DVSN": "00", #
        "ORD_QTY": "1", # 수량
        "ORD_UNPR": str(target_buy_price) # 매수 가격
        })
        
        headers = Headers('TTTC0012U')
        
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
 
        text = f"{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} | {stock}을 {target_buy_price}원에 구매합니다"
        SendMessage(text)
        
        logger.debug(f"{stock}을 구매합니다")
        logger.debug(f'--------------BuyStock--------------')
        logger.debug(response.text)
    
# 매도
def SellStock(stock, target_sell_price):
        
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash"

    payload = json.dumps({
    "CANO": "68579062", # 계좌번호?
    "ACNT_PRDT_CD": "01", #
    "PDNO": stock, # 종목 번호
    "ORD_DVSN": "00", #
    "ORD_QTY": "1", # 수량
    "ORD_UNPR": str(target_sell_price) # 매수 가격
    })
    
    headers = Headers('TTTC0011U')

    response = requests.request("POST", url, headers=headers, data=payload)
    CatchError(response)

    text = f"{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} | {stock}을 {target_sell_price}원에 판매합니다"
    SendMessage(text)
    
    logger.debug(f"{stock}을 판매합니다")
    
# 주식 잔고 조회
def CheckStock():
    time.sleep(0.5)
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-balance?CANO=68579062&ACNT_PRDT_CD=01&AFHR_FLPR_YN=N&OFL_YN=&INQR_DVSN=01&UNPR_DVSN=01&FUND_STTL_ICLD_YN=N&FNCG_AMT_AUTO_RDPT_YN=N&PRCS_DVSN=00&CTX_AREA_FK100&CTX_AREA_NK100="
    
    payload = ""
    headers = Headers('TTTC8434R')

    response = requests.request("GET", url, headers=headers, data=payload)
    CatchError(response)
    
    current_stock = json.loads(response.text)['output1']
    # {'pdno': '005930', 'prdt_name': '삼성전자', 'trad_dvsn_name': '현금', 'bfdy_buy_qty': '0', 'bfdy_sll_qty': '0', 'thdt_buyqty': '0', 'thdt_sll_qty': '0', 'hldg_qty': '1', 'ord_psbl_qty': '1', 'pchs_avg_pric': '51000.0000', 'pchs_amt': '51000', 'prpr': '53800', 'evlu_amt': '53800', 'evlu_pfls_amt': '2800', 'evlu_pfls_rt': '5.49', 'evlu_erng_rt': '5.49019608', 'loan_dt': '', 'loan_amt': '0', 'stln_slng_chgs': '0', 'expd_dt': '', 'fltt_rt': '-0.37000000', 'bfdy_cprs_icdc': '200', 'item_mgna_rt_name': '20%', 'grta_rt_name': '', 'sbst_pric': '0', 'stck_loan_unpr': '0.0000'}
    # {'pdno': '010955', 'prdt_name': 'S-Oil우', 'trad_dvsn_name': '현금', 'bfdy_buy_qty': '7', 'bfdy_sll_qty': '0', 'thdt_buyqty': '0', 'thdt_sll_qty': '0', 'hldg_qty': '7', 'ord_psbl_qty': '7', 'pchs_avg_pric': '39550.0000', 'pchs_amt': '276850', 'prpr': '39100', 'evlu_amt': '273700', 'evlu_pfls_amt': '-3150', 'evlu_pfls_rt': '-1.14', 'evlu_erng_rt': '-1.13780025', 'loan_dt': '', 'loan_amt': '0', 'stln_slng_chgs': '0', 'expd_dt': '', 'fltt_rt': '-1.14000000', 'bfdy_cprs_icdc': '450', 'item_mgna_rt_name': '50%', 'grta_rt_name': '', 'sbst_pric': '0', 'stck_loan_unpr': '0.0000'}

    current_account = json.loads(response.text)['output2']
    # [{'dnca_tot_amt': '9949000', 'nxdy_excc_amt': '9672120', 'prvs_rcdl_excc_amt': '9672120', 'cma_evlu_amt': '0', 'bfdy_buy_amt': '276850', 'thdt_buy_amt': '0', 'nxdy_auto_rdpt_amt': '0', 'bfdy_sll_amt': '0', 'thdt_sll_amt': '0', 'd2_auto_rdpt_amt': '0', 'bfdy_tlex_amt': '30', 'thdt_tlex_amt': '0', 'tot_loan_amt': '0', 'scts_evlu_amt': '327500', 'tot_evlu_amt': '9999620', 'nass_amt': '9999620', 'fncg_gld_auto_rdpt_yn': '', 'pchs_amt_smtl_amt': '327850', 'evlu_amt_smtl_amt': '327500', 'evlu_pfls_smtl_amt': '-350', 'tot_stln_slng_chgs': '0', 'bfdy_tot_asst_evlu_amt': '10002970', 'asst_icdc_amt': '-3350', 'asst_icdc_erng_rt': '-0.03349005'}]
    
    SaveJson(current_stock, 'current_stock.json')
    SaveJson(current_account, 'current_account.json')

    text = PrintCurrentAccount()
    logger.debug(text)
    SendMessage(text)
        
    time.sleep(0.5)

def EndMarket():
    time.sleep(0.5)
    SendMessage("장이 종료되었습니다.\n주식잔고와 계좌정보를 출력합니다.")
    
    SendMessage("-------------주식잔고-----------")
    text = PrintCurrentStock()
    logger.debug(text)
    SendMessage(text)
        
    SendMessage("-------------계좌정보-----------")
    text = PrintCurrentAccount()
    logger.debug(text)
    SendMessage(text)
        
def CheckStockInfo(stock):
    
    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/quotations/search-stock-info?PDNO={str(stock)}&PRDT_TYPE_CD=300"

    payload = ""
    headers = Headers('CTPF1002R')

    response = requests.request("GET", url, headers=headers, data=payload)
    
    return json.loads(response.text)['output']

    '''
    print(response.text)
    {
    "output": {
        "pdno": "00000A005930",
        "prdt_type_cd": "300",
        "mket_id_cd": "STK",
        "scty_grp_id_cd": "ST",
        "excg_dvsn_cd": "02",
        "setl_mmdd": "12",
        "lstg_stqt": "5969782550",
        "lstg_cptl_amt": "0",
        "cpta": "778046685000",
        "papr": "100",
        "issu_pric": "0",
        "kospi200_item_yn": "Y",
        "scts_mket_lstg_dt": "19750611",
        "scts_mket_lstg_abol_dt": "",
        "kosdaq_mket_lstg_dt": "",
        "kosdaq_mket_lstg_abol_dt": "",
        "frbd_mket_lstg_dt": "19750611",
        "frbd_mket_lstg_abol_dt": "",
        "reits_kind_cd": "",
        "etf_dvsn_cd": "0",
        "oilf_fund_yn": "N",
        "idx_bztp_lcls_cd": "002",
        "idx_bztp_mcls_cd": "013",
        "idx_bztp_scls_cd": "013",
        "stck_kind_cd": "101",
        "mfnd_opng_dt": "",
        "mfnd_end_dt": "",
        "dpsi_erlm_cncl_dt": "",
        "etf_cu_qty": "0",
        "prdt_name": "삼성전자보통주",
        "prdt_name120": "삼성전자보통주",
        "prdt_abrv_name": "삼성전자",
        "std_pdno": "KR7005930003",
        "prdt_eng_name": "SamsungElectronics",
        "prdt_eng_name120": "SamsungElectronics",
        "prdt_eng_abrv_name": "SamsungElec",
        "dpsi_aptm_erlm_yn": "Y",
        "etf_txtn_type_cd": "00",
        "etf_type_cd": "",
        "lstg_abol_dt": "",
        "nwst_odst_dvsn_cd": "1",
        "sbst_pric": "42320",
        "thco_sbst_pric": "42320",
        "thco_sbst_pric_chng_dt": "20250225",
        "tr_stop_yn": "N",
        "admn_item_yn": "N",
        "thdt_clpr": "56600",
        "bfdy_clpr": "57200",
        "clpr_chng_dt": "20250226",
        "std_idst_clsf_cd": "032604",
        "std_idst_clsf_cd_name": "통신 및 방송 장비 제조업",
        "idx_bztp_lcls_cd_name": "시가총액규모대",
        "idx_bztp_mcls_cd_name": "전기,전자",
        "idx_bztp_scls_cd_name": "전기,전자",
        "ocr_no": "0121",
        "crfd_item_yn": "",
        "elec_scty_yn": "Y",
        "issu_istt_cd": "00593",
        "etf_chas_erng_rt_dbnb": "0",
        "etf_etn_ivst_heed_item_yn": "N",
        "stln_int_rt_dvsn_cd": "01",
        "frnr_psnl_lmt_rt": "0.00000000",
        "lstg_rqsr_issu_istt_cd": "",
        "lstg_rqsr_item_cd": "",
        "trst_istt_issu_istt_cd": ""
    },
    "rt_cd": "0",
    "msg_cd": "KIOK0530",
    "msg1": "조회되었습니다                                                                  "
}
    '''

# 주식 매수 가능 여부 조회
def CheckBuyStock(stock, target_buy_price):

    url = f"https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-psbl-order?CANO=68579062&ACNT_PRDT_CD=01&PDNO={str(stock)}&ORD_UNPR={str(target_buy_price)}&ORD_DVSN=01&OVRS_ICLD_YN=N&CMA_EVLU_AMT_ICLD_YN=N"

    payload = ""
    headers = Headers('TTTC8908R')
    response = requests.request("GET", url, headers=headers, data=payload)
    CatchError(response)
    logger.debug(f'--------------CheckBuyStock--------------')
    logger.debug(response.text)
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

def BuyCondition(Live_price, target_buy_price):
    if (target_buy_price >= Live_price):
        return True
    
    else :
        return False