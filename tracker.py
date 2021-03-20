import requests
from glob import glob
from bs4 import BeautifulSoup
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
import re
import os
from os import environ

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

#enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    logger.info("User %s started the conversation.", update.message.from_user.username)
    update.message.reply_text(
        "Hi! I'm ezTracker. I can track prices of your products and let you know if they dip.(Currently only flipkart supported.)\n"
        "Type /url and enter an url to start tracking it\n"
        'You can always send /help to get the full list of commands at your disposal\n'
        'Send /cancel to stop tracking.\n'
    )

def scrapeURL(update: Update, context: CallbackContext) -> None:
    urlRegex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = update.message.text
    if not(re.match(urlRegex,url)):
        update.message.reply_text("Please enter a valid URL")
        return

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

    update.message.reply_text( "[ Rating: " + pRating + " ]\n" + pName + "\n[ Price: " + pPrice + " ]")

    return

def cancel(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", update.message.from_user.username)
    update.message.reply_text(
        'Bye! I hope we can cross paths again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def help_command(update: Update, context: CallbackContext) -> None:
    logger.info("User %s used the help command.", update.message.from_user.username)
    update.message.reply_text(
        "Hi! I'm ezTracker. I can track prices of your products and let you know if they dip.(Currently only flipkart supported.)\n"
        "Type /url and enter an url to start tracking it\n"
        'You can always send /help to get the full list of commands at your disposal\n'
        'Send /cancel to stop tracking.\n'
    )

def main():
    updater = Updater(environ['TBOT_KEY'])
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("cancel", cancel))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, scrapeURL))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
