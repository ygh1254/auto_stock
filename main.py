from function import *

Open_price, Target_buy_price = OpenPrice(Stock_list, Open_price, Target_buy_price, Current_stock)

CheckStock()

while(True):

    LivePrice(Stock_list, Target_buy_price, Target_sell_price, Current_stock)

