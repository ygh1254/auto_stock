from real_function import *
from datetime import datetime

start_time = datetime.strptime("09:00:00", "%H:%M:%S").time()
auction_time = datetime.strptime("15:20:00", "%H:%M:%S").time()
end_time = datetime.strptime("15:29:59", "%H:%M:%S").time()

Open_price, Target_buy_price = OpenPrice(Stock_list, Open_price, Target_buy_price)
CheckStock()

# 9:00 ~ 15:20 반복 실행
while(start_time <= datetime.now().time() < auction_time):
    LivePrice(Stock_list, Target_buy_price, mode='normal')

# 15:20 일회 실행
if auction_time <= datetime.now().time() < end_time :
    LivePrice(Stock_list, Target_buy_price, mode='auction')

# 15:30 일회 실행
if end_time <= datetime.now().time() < start_time:
    EndMarket()