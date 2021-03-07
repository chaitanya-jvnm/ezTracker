#works only for flipkart now

#TODO : figure out amazon api and use it for amazon urls

#%%
import requests
from glob import glob
from bs4 import BeautifulSoup
# import pandas
from datetime import datetime
from time import sleep
import json
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import requests
import re
import os
from os import environ

#%%
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

#%%
#enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

#%%
logger = logging.getLogger(__name__)

# GENDER, PHOTO, LOCATION, BIO = range(4)
prod = range(1)

# def echo(update: Update, context: CallbackContext) -> None:
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)

#%%
def start(update: Update, context: CallbackContext):
    logger.info("User %s started the conversation.", user.first_name)
    update.message.reply_text(
        "Hi! I'm ezTracker. I can track prices of your products and let you know if they dip.(Currently only flip[kart supported.)"
        "Type /url and enter an url to start tracking it"
        'You can always send /help to get the full list of commands at your disposal'
        'Send /cancel to stop tracking.\n\n'
        # reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

#%%
def scrapeURL(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    page = requests.get(url,headers=HEADERS)
    soup = BeautifulSoup(page.content, features="lxml")

    #Product Name section
    try:
        #pName = soup.find(id='productTitle').get_text().strip() --Amazon
        pName = soup.find_all(class_="B_NuCI")[0].get_text().replace(u'\xa0', u' ').strip()
    except:
        pName = ''

    # Product price section
    try:
        # pPrice = float(soup.find(id='priceblock_ourprice').get_text().replace('.', '').replace('₹', '').replace(',', '.').strip()) --Amazon
        pPrice = soup.find_all(class_="_30jeq3")[0].get_text().strip()
    except:
        pPrice = ''
    
    #Product rating
    try:
        pRating = soup.find_all(class_="_3LWZlK")[0].get_text()
    except:
        pRating = ''

    #try:
        # soup.select('#availability .a-color-state')[0].get_text().strip() --Amazon availability
        # stock = 'Out of Stock'
    # except:
    #     stock = 'Available'

    #print( "[ Rating: " + pRating + " ]\n" + pName + "\n[ Price: " + pPrice + " ]")
    # print ('{ "name": "' + pName + '", "rating":"' + pRating + '", "price":"' + pPrice + '" }')
    return '{ "name": "' + pName + '", "rating":"' + pRating + '", "price":"' + pPrice + '" }'
    update.message.reply_text( "[ Rating: " + product['rating'] + " ]\n" + product['name'] + "\n[ Price: " + product['price'] + " ]")

#%%
# def updateChat(update: Update, context: CallbackContext):
#     #get the recipients chat id
#     chat_id = update.message.chat_id
#     # bot.send_photo(chat_id=chat_id, photo=url)
#     bot.send_message(chat_id=chat_id, text=scrapeURL)

#%%
def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can cross paths again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

#%%
def main():
    updater = Updater('1590128551:AAFZO4q13bx_s4K8cZ3zr9io3HZasw1_vuY')
    # updater = Updater(environ['TBOT-KEY'])
    dispatcher = updater.dispatcher
    urlRegex = 'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            prod: [MessageHandler(Filters.regex(urlRegex), scrapeURL)]
            # GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            # PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, scrapeURL))

    # dp.add_handler(CommandHandler('bop',updateChat))
    updater.start_polling()
    updater.idle()

#%%
if __name__ == '__main__':
    main()




#%%
# item = "https://www.amazon.in/Logitech-Lightspeed-Suspension-LIGHTSYNC-Technology/dp/B08HNCG8WQ/ref=sr_1_10_sspa?crid=3QA8S7TAU8UXS&dchild=1"
link = str('https://www.flipkart.com/ambrane-aqc-56-18-w-3-mobile-charger-detachable-cable/p/itm053fe47c4f26c?pid=ACCFNACQPFAQBHTE&lid=LSTACCFNACQPFAQBHTE7AIBOQ&marketplace=FLIPKART&srno=b_1_5&otracker=hp_omu_Deals%2Bof%2Bthe%2BDay_4_3.dealCard.OMU_NW53DUEZOI54_3&otracker1=hp_omu_SECTIONED_neo%2Fmerchandising_Deals%2Bof%2Bthe%2BDay_NA_dealCard_cc_4_NA_view-all_3&fm=neo%2Fmerchandising&iid=acf14168-0de3-4f65-af60-7cc22381d7d2.ACCFNACQPFAQBHTE.SEARCH&ppt=browse&ppn=browse&ssid=4dkfw756u34qbsow1613827233912')

#%%
product = json.loads(main(link))
print ( "[ Rating: " + product['rating'] + " ]\n" + product['name'] + "\n[ Price: " + product['price'] + " ]")
    
# %%
#testing block
