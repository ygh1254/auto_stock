from function import *

while(True):
    
    Open_price, Target_buy_price = OpenPrice(Stock_list, Open_price, Target_buy_price)

    LivePrice(Stock_list, Target_buy_price, Actual_buy_price, Target_sell_price, Actual_sell_price)

    print(f'Open_price:{Open_price}')
    print(f'Target_buy_price:{Target_buy_price}')
    print(f'Target_sell_price:{Target_sell_price}')
    print(f'Actual_buy_price:{Actual_buy_price}')
    print(f'Actual_sell_price:{Actual_sell_price}')
    print(f'Quantity:{Quantity}')
    print(f'Log:{Log}')