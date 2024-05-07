







from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters
from datetime import datetime
import commands, messages
from dbhelper import DBHelper
from typing import Final
import os
# import bot_constants

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME: Final = '@denzyltestbot'

import logging

# Configure logging
logging.basicConfig(filename='bot.log', level=logging.INFO)


# Check if BOT_TOKEN starts with '668'
if BOT_TOKEN is not None and BOT_TOKEN.startswith('668'):
    logging.info("BOT_TOKEN starts with '668'")
else:
    logging.warning("BOT_TOKEN either is not set or does not start with '668'")

db = DBHelper()
 

def handle_updates(updates):
  for update in updates["result"]:
    try:
      text = update["message"]["text"]
      chat = update["message"]["chat"]["id"]
      items = db.get_items()
      if text in items:
        db.delete_item(text)
        items = db.get_items()
      else:
        db.add_item(text)
        items = db.get_items()
      message = "\n".join(items)
      send_message(message, chat)
    except KeyError:
      pass


A, B, C, D, E = range(5)

if __name__ == '__main__':
  db.setup()
  app = Application.builder().token(BOT_TOKEN).build()

  print(datetime.now())

  # commands
  app.add_handler(CommandHandler('start', commands.start))
  app.add_handler(CommandHandler('help', commands.help))
  app.add_handler(CommandHandler('mycals', commands.mycals))
  app.add_handler(CommandHandler('forgotmypassword', commands.forgot))
  app.add_handler(CommandHandler('cancel', commands.cancel))

  # dev
  app.add_handler(CommandHandler('listcals', commands.listcals))
  app.add_handler(CommandHandler('listpassword', commands.list_password))
  app.add_handler(CommandHandler('listaccess', commands.list_access))
  app.add_handler(CommandHandler('restart', commands.restart))

  # login
  login_handler = ConversationHandler(
      entry_points=[CommandHandler("login", commands.login)],
      states={
          A: [MessageHandler(filters.TEXT, commands.loginA)],
          B: [MessageHandler(filters.TEXT, commands.loginB)],
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(login_handler)

  # Add new calendar
  new_calendar_handler = ConversationHandler(
      entry_points=[CommandHandler("newcal", commands.new_cal)],
      states={
          A: [MessageHandler(filters.TEXT, commands.new_calA)],
          B: [MessageHandler(filters.TEXT, commands.new_calB)],
          C: [MessageHandler(filters.TEXT, commands.new_calC)],
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(new_calendar_handler)

  # remove calendar
  remove_calendar_handler = ConversationHandler(
      entry_points=[CommandHandler("remcal", commands.remove_cal)],
      states={
          A: [MessageHandler(filters.TEXT, commands.remove_calA)],
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(remove_calendar_handler)

  # Add new event
  new_event_handler = ConversationHandler(
      entry_points=[CommandHandler("newevent", commands.new_event)],
      states={
          A: [MessageHandler(filters.TEXT, commands.new_eventA)],
          B: [MessageHandler(filters.TEXT, commands.new_eventB)],
          C: [MessageHandler(filters.TEXT, commands.new_eventC)],
          D: [MessageHandler(filters.TEXT, commands.new_eventD)],
          E: [MessageHandler(filters.TEXT, commands.new_eventE)]
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(new_event_handler)

  # Add new event on multiple days
  multiple_days_handler = ConversationHandler(
      entry_points=[CommandHandler("multipledates", commands.new_event_multiple_dates)],
      states={
          A: [MessageHandler(filters.TEXT, commands.new_event_multiple_datesA)],
          B: [MessageHandler(filters.TEXT, commands.new_event_multiple_datesB)],
          C: [MessageHandler(filters.TEXT, commands.new_event_multiple_datesC)],
          D: [MessageHandler(filters.TEXT, commands.new_event_multiple_datesD)],
          E: [MessageHandler(filters.TEXT, commands.new_event_multiple_datesE)]
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(multiple_days_handler)
  
  # remove event
  remove_event_handler = ConversationHandler(
      entry_points=[CommandHandler("remevent", commands.remove_event)],
      states={
          A: [MessageHandler(filters.TEXT, commands.remove_eventA)],
          B: [MessageHandler(filters.TEXT, commands.remove_eventB)],
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(remove_event_handler)

  # View events in calendar
  view_events_handler = ConversationHandler(
      entry_points=[CommandHandler("viewevents", commands.view_events)],
      states={
          A: [MessageHandler(filters.TEXT, commands.view_eventsA)],
          B: [MessageHandler(filters.TEXT, commands.view_eventsB)]
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(view_events_handler)

  # presets
  presets_handler = ConversationHandler(
      entry_points=[CommandHandler("presets", commands.presets)],
      states={
          A: [MessageHandler(filters.TEXT, commands.presetsA)],
          B: [MessageHandler(filters.TEXT, commands.presetsB)],
          C: [MessageHandler(filters.TEXT, commands.presetsC)],
          D: [MessageHandler(filters.TEXT, commands.presetsD)],
          E: [MessageHandler(filters.TEXT, commands.presetsE)]
      },
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(presets_handler)

  def create_conversation_handler(preset_number, view):
    return ConversationHandler(
        entry_points=[CommandHandler(preset_number, view)],
        states={A: [MessageHandler(filters.TEXT, commands.view_presetA)]},
        fallbacks=[CommandHandler("cancel", commands.cancel)],
        allow_reentry=True)

  # Create ConversationHandlers for /1, /2, and /3
  view1_handler = create_conversation_handler("1", commands.view_preset1)
  view2_handler = create_conversation_handler("2", commands.view_preset2)
  view3_handler = create_conversation_handler("3", commands.view_preset3)

  # Add ConversationHandlers to your Application instance
  app.add_handler(view1_handler)
  app.add_handler(view2_handler)
  app.add_handler(view3_handler)

  # clear past events
  clear_past_events_handler = ConversationHandler(
      entry_points=[CommandHandler("clear", commands.clear_past_events)],
      states={A: [MessageHandler(filters.TEXT, commands.clear_past_events1)]},
      fallbacks=[CommandHandler("cancel", commands.cancel)],
      allow_reentry=True)

  app.add_handler(clear_past_events_handler)

  # messages
  app.add_handler(MessageHandler(filters.TEXT, messages.handle_message))

  # errors
  app.add_error_handler(commands.error)

  # polls
  print("polling...")
  app.run_polling(poll_interval=1)
