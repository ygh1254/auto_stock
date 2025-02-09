from function import *
from datetime import datetime

start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
end_time = datetime.strptime("15:59:59", "%H:%M:%S").time()

Open_price, Target_buy_price = OpenPrice(Stock_list, Open_price, Target_buy_price, Current_stock)

CheckStock(Current_stock, Current_account)

while(True):
    current_time = datetime.now().time()
    if start_time <= current_time <= end_time :
        LivePrice(Stock_list, Target_buy_price, Target_sell_price, Current_stock)
    
    else:
        print("개장 시간이 아닙니다.")
        exit()