from vantage_api import get_stock_price
from datetime import datetime

def process_message(db, api, message_obj):
    msg = message_obj.text.lower().split(' ')
    if (("show" in msg[0]) and (len(msg) == 2)):
        if (msg[1] == 'portfolio'):
            stocks = db.get_all_stocks_for_user(message_obj.personEmail)
            if (stocks != None):
                msg_to_user = 'Here are the details of the portfolio for {}\n'.format(message_obj.personEmail)
                for stock in stocks:
                    price, change = get_stock_price(stock['ticker'])
                    stock_value = price*float(stock['quantity'])
                    up_down = 'up' if change > 0 else 'down'
                    msg_to_user += '{} - qty. {} added on {}, worth {:.2f}, {} {:.2f}% today.\n'.format(
                        stock['ticker'].upper(), stock['quantity'], stock['formatted_date'], stock_value, up_down,
                        change
                    )
            else:
                msg_to_user = "An error occurred. The stocks could not be feteched. Try again later.\n"
        else:
            price, change = get_stock_price(msg[1])
            up_down = 'up' if change > 0 else 'down'
            msg_to_user = "The current price for {} is {:.2f}, {} {:.2f}% today.\n".format(
                msg[1], price, up_down, change
            )
    elif (("add" in msg[0]) and (len(msg) == 3)):
        timestamp = datetime.now()
        db.create_user(message_obj.personEmail)
        result = db.add_stock_to_portfolio(message_obj.personEmail, msg[1], msg[2], timestamp)
        if (result != None):
            msg_to_user = "Added to portfolio {} of {}\n".format(msg[2], msg[1].upper())
        else:
            msg_to_user = "An error occurred. The stock could not be added to your portfolio. Try again later.\n"
    else:
        msg_to_user = "This operation is not supported. Refer to the docs on how to use this bot.\n"
    return api.messages.create(toPersonEmail=message_obj.personEmail, markdown=msg_to_user)
