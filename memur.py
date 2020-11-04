#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot

from auth import BOT_AUTH

import time
import threading

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Memurunuzu selamlayınız.')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

konusanlar = {}
messagecount = {}
susma_suresi_saniye = 60
short_period = 4.1
bot = Bot(BOT_AUTH)
def processMessage(update, context):
    """Process message."""
    
    userid = update.effective_user.id
    limit = 5
    if( userid in messagecount ):
        messagecount[userid] += 1
    else:
        messagecount[userid] = 1

    if( messagecount[userid] == limit and (userid != 32408209) ):
        update.message.reply_text("çok konuştun. şimdi susma vakti. " + str(susma_suresi_saniye) + "sn sonra görüşmek üzere.")
        konusanlar[userid] = time.time()
        periodic_checks(update)
    else:
        threading.Timer(short_period * messagecount[userid], balancer,  args=[userid]).start()
        
    if( messagecount[userid] > limit and (userid != 32408209)  ):
        bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        
    logger.info(str(userid) + " " + update.message.text)

def balancer(userid):
    if(userid not in konusanlar or konusanlar[userid] == 0):
        messagecount[userid] -= 1

def periodic_checks(update):
    a = False
    for userid in konusanlar:
        if(userid in messagecount and userid in konusanlar):
            if(konusanlar[userid] > 0 and time.time() - konusanlar[userid] > susma_suresi_saniye):
                a = True
                messagecount[userid] = 0
                konusanlar[userid] = 0
                name = update.message.from_user.first_name
                mention = "["+ name+"](tg://user?id="+str(userid)+")"
                logger.info("?")
                bot.send_message(update.message.chat_id, "Konuşabilirsin " + mention, parse_mode="Markdown")
                logger.info("??")
    if(a is False):        
        threading.Timer(1, periodic_checks,  args=[update]).start()

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_AUTH, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, start))
    dp.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command, processMessage))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()