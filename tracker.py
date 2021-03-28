import requests
from glob import glob
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import json
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, keyboardbutton, replymarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import re
import os
from os import environ

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

a_val = 0 #variables to use as keys for amazon context
f_val = 0 #variables to use as keys for flipkart context

#enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
WEBSITE, AMAZON, FLIPKART = range(3)

def start(update: Update, context: CallbackContext) -> int:
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    reply_keyboard = [['amazon', 'flipkart']]
    update.message.reply_text(
        "Hi! I'm ezTracker. I can track prices of your products and let you know if they dip.(Currently only flipkart supported.)\n"
        "Select either Amazon or flipkart from the keyboard and type enter the product URL to start tracking its price.\n"
        'You can always send /help to get the full list of commands at your disposal.\n'
        'Send /cancel to stop tracking.\n',
        reply_markup = ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)
    )
    context.user_data[username] = update.message.from_user.first_name
    return WEBSITE

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", update.message.from_user.username)
    update.message.reply_text(
        'Bye! I hope we can cross paths again some day.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def help_command(update: Update, context: CallbackContext) -> None:
    logger.info("User %s used the help command.", update.message.from_user.first_name)
    reply_keyboard = [['amazon', 'flipkart']]
    update.message.reply_text(
        "Hi! I'm ezTracker. I can track prices of your products and let you know if they dip.(Currently only flipkart supported.)\n"
        "Select either Amazon or flipkart from the keyboard and type enter the product URL to start tracking its price.\n"
        'You can always send /help to get the full list of commands at your disposal.\n'
        'Send /cancel to stop tracking.\n',
        reply_markup = ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)
    )

def show_current(update: Update, context: CallbackContext) -> None:
    return

def track_flipkart(update: Update, context: CallbackContext) -> int:
    logger.info("User %s used the flipkart command.", update.message.from_user.first_name)
    update.message.reply_text("Please enter the URL of the product you want to track.")
    return FLIPKART

def get_f_url(update: Update, context: CallbackContext) -> int:
    logger.info("User %s entered an url for flipkart.", update.message.from_user.first_name)
    urlRegex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = update.message.text
    if not(re.match(urlRegex,url)):
        update.message.reply_text("Please enter a valid URL")
        return FLIPKART
    context.user_data[f_url] = url
    reply_keyboard = [['1 hour','2 hours']]
    update.message.reply_text(
        "In how many intervals per day would you like to track it ?\n"
        "(for example if you select 1 hour, youll be notified of the price of the product every hour)",
        reply_markup = ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)
    )
    return FLIPKART

def initiate_scrape_f_url(update: Update, context: CallbackContext) -> None:
    logger.info("User %s used the scrape_f command.", update.message.from_user.first_name)
    url = context.user_data[f_url]
    time_interval = int((update.message.text)[0:2].strip())*60 #using the first 2 characters to get the time interval
    counter = 0
    max_counter = 168/time_interval
    while counter < max_counter:
        product_details = scrape_f_url(url)
        update.message.reply_text( url+"\n[ Rating: " + product_details[0] + " ]\n" + product_details[1] + "\n[ Price: " + product_details[2] + " ]")
        counter = counter+1
        sleep(time_interval)
    return

def scrape_f_url(url):
    page = requests.get(url,headers=HEADERS)
    soup = BeautifulSoup(page.content, features="lxml")
    #Product Name section
    try:
        pName = soup.find_all(class_="B_NuCI")[0].get_text().replace(u'\xa0', u' ').strip()
    except:
        pName = ''
    # Product price section
    try:
        pPrice = soup.find_all(class_="_30jeq3")[0].get_text().strip()
    except:
        pPrice = ''    
    #Product rating
    try:
        pRating = soup.find_all(class_="_3LWZlK")[0].get_text()
    except:
        pRating = ''
    return [pName,pPrice,pRating]


def track_amazon(update: Update, context: CallbackContext) -> None:
    logger.info("User %s used the amazon command.", update.message.from_user.first_name)
    reply_keyboard = [['amazon', 'flipkart']]
    update.message.reply_text(
        "Sorry, there is no support for Amazon URLs yet. But its comming soon...!\n"
        "Try using the flipkart option if you have an alternate flipkart variant of the product you were looking for.",
        reply_markup = ReplyKeyboardMarkup(reply_keyboard,one_time_keyboard=True)
    )
    return WEBSITE


def main():
    updater = Updater(environ['TBOT_KEY'],use_context=True) 
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WEBSITE:[                
                MessageHandler(Filters.regex('^(flipkart)'),track_flipkart),                
                MessageHandler(Filters.regex('^(amazon)'),track_amazon)
            ],
            AMAZON:[
                # MessageHandler(Filters.text & ~Filters.command, scrape_a_url)
            ],
            FLIPKART:[
                MessageHandler(Filters.regex('^\d*\shour[s]*$'),initiate_scrape_f_url),
                MessageHandler(Filters.text & ~Filters.command, get_f_url)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(CommandHandler("current",show_current))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
