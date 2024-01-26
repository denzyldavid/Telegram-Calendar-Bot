from time import sleep
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from dbhelper import DBHelper
import datetime
import utils
import re
import logging

A, B, C, D, E = range(5)

db = DBHelper()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# display text
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Hello!')
  await update.message.reply_text(
      'Create a new calendar with /newcal, then add events to it with /newevent!'
  )
  await update.message.reply_text(
      'Or if you want to access an existing calendar, login with /login!')
  sleep(1)
  await update.message.reply_text(
      'Try not to poop your pants while you do this though 😷')
  logger.info("User: %s", context._user_id)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "/start, /help, /listall, /mycals, /newcal, /login, /forgotmypassword, /newevent, /viewevents, /presets, /1, /2, /3, /clear"
  )
  await update.message.reply_text("/start: Start the bot.")
  await update.message.reply_text("/help: troll.")
  await update.message.reply_text(
      "/listall: lists all calendars in the system, but does not give away any personal and calendar information."
  )
  await update.message.reply_text(
      "/mycals: lists only calendars that you have access to.")
  await update.message.reply_text(
      "/newcal: create a new calendar. You'll need to give it a name, password, and emoji. Password is there so that I can share this with people outside of our family without compromising on our privacy. The calendar you create automatically grants you access."
  )
  await update.message.reply_text(
      "/login: for security. Needs calendar name (open for all to see) and password. Keep your password private, only for those you trust with your life. Or your calendar."
  )
  await update.message.reply_text("/forgotmypassword: troll.")
  await update.message.reply_text(
      "/newevent: requires access to at least one calendar. This adds an event to the calendar."
  )
  await update.message.reply_text(
      "/viewevents: requires access to at least one calendar. This allows you to see all the events in one or more calendars, in chronological order."
  )
  await update.message.reply_text(
      "/presets: manage up to 3 presets, which can be viewed quickly. There is also an option to reset, meaning you remove all your calendars from the preset."
  )
  await update.message.reply_text(
      "/1, /2, /3: these presets must have at least one calendar added to be used. This allows quick access to those calendars, without the need to choose which calendars to see."
  )
async def forgot(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text('Too bad hehe 🐒')
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  await update.message.reply_text('Okay 😒', reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
  chat_id = update.message.chat_id if update.message else "Unknown"
  logger.error("Error in chat %s: %s", chat_id, str(context.error), exc_info=True)
  
# display calendars
async def listcals(update: Update, context: ContextTypes.DEFAULT_TYPE):
  cals = db.get_all_calendars_emoji()
  string = "All calendars:\n"
  for cal in cals:
    string += cal[0] + " " + cal[1] + "\n"
  await update.message.reply_text(string)
async def mycals(update: Update, context: ContextTypes.DEFAULT_TYPE):
  cals = db.get_my_calendars_emoji(context._user_id)
  if len(cals) == 0:
    await update.message.reply_text(
        "You don't have any calendars. Create a new one with /newcal!")
  else:
    string = "Your calendars:\n"
    for cal in cals:
      string += cal[0] + " " + cal[1] + "\n"
    await update.message.reply_text(string)

# login to calendar
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("Which calendar do you want to login to?")
  cals = utils.show_all_calendars()
  if cals is not None:
    await update.message.reply_text("All calendars:\n" + cals)
  return A
# ask which calendar to login to
async def loginA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['calendar'] = response
  # check if calendar exists
  if response not in db.get_all_calendars():
    await update.message.reply_text("This calendar does not exist",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  await update.message.reply_text("What is the password?")
  context.user_data['attempts'] = 0
  return B
# handle calendar name, ask for password
async def loginB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['password'] = response

  # check password
  if response == db.get_password(context.user_data['calendar']):
    db.grant_access(context._user_id, context.user_data['calendar'])
    await update.message.reply_text("Access granted!",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  context.user_data['attempts'] += 1
  if context.user_data['attempts'] < 3:
    await update.message.reply_text("Wrong password! Try again?")
    return B

  await update.message.reply_text("Hey, no hacking!",
                                  reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END
# check password, grant access

# new_cal
async def new_cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      'What name do you want for your new calendar?')
  return A
# ask for calendar name
async def new_calA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['calendarname'] = response
  await update.message.reply_text("What is the password?")
  return B
# handle calendar name, ask for password
async def new_calB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['password'] = response
  await update.message.reply_text(
      "Choose an emoji to represent your calendar! 🍄")
  return C
# handle password, ask for emoji
async def new_calC(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['emoji'] = response

  db.add_calendar(context.user_data['calendarname'],
                  context.user_data['password'], context.user_data['emoji'],
                  context._user_id)
  await update.message.reply_text(
      "Calendar created! Add an event to it with /newevent or add it to your presets with /presets!",
      reply_markup=ReplyKeyboardRemove())

  return ConversationHandler.END
# add calendar

# remove_cal
async def remove_cal(update: Update, context: ContextTypes.DEFAULT_TYPE):  # add options
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['I am done'])

  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  await update.message.reply_text(
      "Which calendar do you want to remove? (you can log in again to regain access to these calendars)",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar to remove"))
  return A
async def remove_calA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  if response == 'I am done':
    await update.message.reply_text("View your remaining calendars with /mycals", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
  
  # one calendar
  if response in db.get_my_calendars(context._user_id):
    db.remove_access(response, context._user_id)
    context.user_data['reply_keyboard'].remove([response])
  else:
    await update.message.reply_text("You do not have access to this calendar")
  await update.message.reply_text(
      "Any more calendars?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A

# new_event
async def new_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # add calendar options to keyboard
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['I am done'])

  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  await update.message.reply_text(
      "Which calendar do you want to add to?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A
# ask for which calendar to add to
async def new_eventA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['calendar'] = response
  
  # check access
  if response not in db.get_my_calendars(context._user_id):
    await update.message.reply_text("You do not have access to this calendar",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  # initialise other stuff
  context.user_data['time'] = ""
  context.user_data['notes'] = ""
  
  await update.message.reply_text("What is the name of the event?",
                                  reply_markup=ReplyKeyboardRemove())
  return B
# handle calendar name, ask for event name
async def new_eventB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['event_name'] = response
  await update.message.reply_text("What date is this happening?")
  return C
# handle event name, ask for date
async def new_eventC(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  context.user_data['date'] = response

  context.user_data['reply_keyboard2'] = [["I am done"], ["Set time"],
                                          ["Add notes"]]
  await update.message.reply_text("Anything else?",
                                  reply_markup=ReplyKeyboardMarkup(
                                      context.user_data['reply_keyboard2'],
                                      one_time_keyboard=True))
  return D
# handle date, ask if want to set time or notes
async def new_eventD(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['reply_keyboard2'].remove([response])

  if response == "I am done":
    date_formatted = utils.format_date(context.user_data['date'],
                                       context.user_data['time'])
    db.add_event(context.user_data['calendar'],
                 context.user_data['event_name'], date_formatted,
                 context.user_data['notes'])
    await update.message.reply_text(
        "Event saved! Add another event with /newevent, or view your events with /viewevents!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  elif response == "Set time":
    context.user_data['option'] = "time"
    await update.message.reply_text("What time is this event?",
                                    reply_markup=ReplyKeyboardRemove())
    return E

  elif response == "Add notes":
    context.user_data['option'] = "notes"
    await update.message.reply_text("What notes do you want to add?",
                                    reply_markup=ReplyKeyboardRemove())
    return E
# create event, or ask for time or notes
async def new_eventE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  option = context.user_data['option']
  context.user_data[option] = response
  await update.message.reply_text("Anything else?",
                                  reply_markup=ReplyKeyboardMarkup(
                                      context.user_data['reply_keyboard2'],
                                      one_time_keyboard=True))
  return D
# handle input, then ask again (D)

# multiple_dates
async def new_event_multiple_dates(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # add calendar options to keyboard
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['I am done'])

  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  await update.message.reply_text(
      "Which calendar do you want to add to?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A
# ask for which calendar to add to
async def new_event_multiple_datesA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['calendar'] = response

  # check access
  if response not in db.get_my_calendars(context._user_id):
    await update.message.reply_text("You do not have access to this calendar",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  # initialise other stuff
  context.user_data['time'] = ""
  context.user_data['notes'] = ""

  await update.message.reply_text("What is the name of the event?",
                                  reply_markup=ReplyKeyboardRemove())
  return B
# handle calendar name, ask for event name
async def new_event_multiple_datesB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['event_name'] = response
  await update.message.reply_text("What dates will this happen?")
  context.user_data['date'] = []
  return C
# handle event name, ask for date
async def new_event_multiple_datesC(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  if response.lower() == 'no':
    context.user_data['reply_keyboard2'] = [["I am done"], ["Set time"],
                                            ["Add notes"]]
    await update.message.reply_text("Anything else?",
                                    reply_markup=ReplyKeyboardMarkup(
                                        context.user_data['reply_keyboard2'],
                                        one_time_keyboard=True))
    return D

  context.user_data['date'].append(response)
  await update.message.reply_text("Any other dates?")
  await update.message.reply_text("Say no if you're done")
  return C
# handle date, ask if want to set time or notes
async def new_event_multiple_datesD(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  context.user_data['reply_keyboard2'].remove([response])

  if response == "I am done":
    for date in context.user_data['date']:
      date_formatted = utils.format_date(date,
                                         context.user_data['time'])
      db.add_event(context.user_data['calendar'],
                   context.user_data['event_name'], date_formatted,
                   context.user_data['notes'])
    await update.message.reply_text(
        "Events saved! Add another event with /newevent, or view your events with /viewevents!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  elif response == "Set time":
    context.user_data['option'] = "time"
    await update.message.reply_text("What time is this event?",
                                    reply_markup=ReplyKeyboardRemove())
    return E

  elif response == "Add notes":
    context.user_data['option'] = "notes"
    await update.message.reply_text("What notes do you want to add?",
                                    reply_markup=ReplyKeyboardRemove())
    return E
# create event, or ask for time or notes
async def new_event_multiple_datesE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  option = context.user_data['option']
  context.user_data[option] = response
  await update.message.reply_text("Anything else?",
                                  reply_markup=ReplyKeyboardMarkup(
                                      context.user_data['reply_keyboard2'],
                                      one_time_keyboard=True))
  return D
# handle input, then ask again (D)

# remove_event
async def remove_event(update: Update, context: ContextTypes.DEFAULT_TYPE):  
  # add calendar options
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['I am done'])

  # check if no calendars
  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  # ask for calendar to remove from
  await update.message.reply_text(
      "Which calendar do you want to remove from?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar to remove"))
  return A
# ask for calendar to remove from
async def remove_eventA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  # have not provided a calendar
  if response == 'I am done':
    await update.message.reply_text("You never tell me :(", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  # response is a calendar
  elif response in db.get_my_calendars(context._user_id):
    # check if calendar is empty
    if len(db.get_events(response)) == 0:
      await update.message.reply_text(
          "This calendar does not have any events. Create some with /newevent!",
          reply_markup=ReplyKeyboardRemove())
      return ConversationHandler.END

    # add events to keyboard, format date for readability
    context.user_data['calendar'] = response
    context.user_data['reply_keyboard2'] = []
    for event in db.get_events(response):
      date_time = event[0].split(" ")
      date = date_time[0].split("-")
      formatted_date = ""
      if len(date_time) == 1:
        formatted_date = f"{date[2]}/{date[1]}/{date[0]}"
      elif len(date_time) == 2: # has time
        formatted_date = f"{date[2]}/{date[1]}/{date[0]} {date_time[1]}"
      context.user_data['reply_keyboard2'].append([f"{event[2]}, {formatted_date}"])
    context.user_data['reply_keyboard2'].append(['I am done'])

    # ask user
    await update.message.reply_text(
        "Which event do you want to remove?",
        reply_markup=ReplyKeyboardMarkup(
            context.user_data['reply_keyboard2'],
            one_time_keyboard=True,
            input_field_placeholder="Select an event to remove"))
    return B
  else:
    await update.message.reply_text("You do not have access to this calendar")
# ask for event to remove
async def remove_eventB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  
  if response == 'I am done':
    await update.message.reply_text("Removed! View remaining events with /viewevents.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  context.user_data['reply_keyboard2'].remove([response])
  event_name_date = response.split(", ")
  event_name = event_name_date[0]
  date_time = event_name_date[1].split(" ")
  date = date_time[0].split("/")
  formatted_date = f"{date[2]}-{date[1]}-{date[0]}"
  if len(date_time) == 2:
    formatted_date += f" {date_time[1]}"
  db.delete_event(context.user_data['calendar'], event_name, formatted_date)
  await update.message.reply_text("Any more events to remove?",
    reply_markup=ReplyKeyboardMarkup(
        context.user_data['reply_keyboard2'],
        one_time_keyboard=True,
        input_field_placeholder="Select an event to remove"))
  return B
# remove event, ask if want to remove more

# view events
async def view_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # add calendar options to keyboard
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['All'])
  context.user_data['reply_keyboard'].append(['I am done'])

  # prompt user
  cals = utils.show_my_calendars(context._user_id)
  if cals is not None:
    context.user_data['calendars'] = []
    await update.message.reply_text(
        "Which calendar do you want to view?",
        reply_markup=ReplyKeyboardMarkup(
            context.user_data['reply_keyboard'],
            one_time_keyboard=True,
            input_field_placeholder="Select a calendar"))
    return A
  else:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END
# ask user which calendar to view
async def view_eventsA(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # save response
  response = update.message.text

  # done
  if response == "I am done":
    # check if user has chosen calendars
    if len(context.user_data['calendars']) == 0:
      await update.message.reply_text("You have not chosen any calendars.",
                                      reply_markup=ReplyKeyboardRemove())
      return ConversationHandler.END

    # check if calendars have events
    if utils.have_events(context.user_data['calendars']) == False:
      await update.message.reply_text(
          "There are no events in these calendars. Create a new event with /newevent!"
      )
      return ConversationHandler.END
    await update.message.reply_text("See notes?",
                                    reply_markup=ReplyKeyboardMarkup(
                                        [["Yes", "No"]],
                                        one_time_keyboard=True))
    return B
    
  # all
  elif response == "All":
    if utils.user_has_events(context._user_id) is False:
      await update.message.reply_text(
          "There are no events in these calendars. Create a new event with /newevent!"
      )
      return ConversationHandler.END

    for cal in db.get_my_calendars(context._user_id):
      context.user_data['calendars'].append(cal)
    await update.message.reply_text("See notes?",
                                    reply_markup=ReplyKeyboardMarkup(
                                        [["Yes", "No"]],
                                        one_time_keyboard=True))
    return B

  # one calendar
  if response in db.get_my_calendars(context._user_id):
    context.user_data['calendars'].append(response)
    context.user_data['reply_keyboard'].remove([response])
  else:
    await update.message.reply_text("You do not have access to this calendar")
  await update.message.reply_text(
      "Any more calendars?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A
# ask user if want to see more calendars, or notes if all or done
async def view_eventsB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text
  if response == "Yes":
    events = utils.show_events(context.user_data['calendars'], notes=True)
  if response == "No":
    events = utils.show_events(context.user_data['calendars'], notes=False)
  if events == None:
    await update.message.reply_text(
        "There are no events in these calendars. Create a new event with /newevent!"
    )
    return ConversationHandler.END
  await update.message.reply_text(events,
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END
  
# manage presets
async def presets(update: Update, context: ContextTypes.DEFAULT_TYPE):

  # if user has no calendars
  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!")
    return ConversationHandler.END

  # if user has calendars
  context.user_data['presets'] = [['1'], ['2'], ['3']]
  await update.message.reply_text(
      "Which preset would you like to manage?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['presets'],
          one_time_keyboard=True,
          input_field_placeholder="Select preset"
      )
  )
  
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['All'])
  context.user_data['reply_keyboard'].append(['I am done'])
  
  return A
# choose presets, stop if no calendars
async def presetsA(update: Update, context: ContextTypes.DEFAULT_TYPE):
  response = update.message.text
  context.user_data['preset'] = response
  
  # add calendars to keyboard
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['All'])
  context.user_data['reply_keyboard'].append(['I am done'])

  # if preset is empty
  if len(db.get_preset(context._user_id, context.user_data['preset'])) == 0:
    # context.user_data['calendars'] = [] # to be populated
    await update.message.reply_text(
        f"Which calendars would you like to add to preset {context.user_data['preset']}?",
        reply_markup=ReplyKeyboardMarkup(
            context.user_data['reply_keyboard'],
            one_time_keyboard=True,
            input_field_placeholder="Select a calendar"))
    return C
  else:
    await update.message.reply_text(
        "Would you like to clear this preset, add to it, or change notes preferences?"
    )
    string = "Current preset calendars:\n"
    cals_and_notes = db.get_preset(context._user_id, context.user_data['preset'])
    for cal_note in cals_and_notes:
      string += cal_note[0] + " " + db.get_emoji(cal_note[0]) + "\n"
    await update.message.reply_text(
        string,
        reply_markup=ReplyKeyboardMarkup(
            [['Clear', 'Add', "Notes preferences"]], one_time_keyboard=True))
    return B
# choose to clear, add or change notes preferences. if empty preset, add by default
async def presetsB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  # clear
  if response == "Clear":
    db.clear_preset(context._user_id, context.user_data['preset'])
    await update.message.reply_text(
        f"Preset {context.user_data['preset']} has been cleared. Which calendar do you want to add?",
        reply_markup=ReplyKeyboardMarkup(
            context.user_data['reply_keyboard'],
            one_time_keyboard=True,
            input_field_placeholder="Select a calendar"))
    return C

  # add
  elif response == "Add":
    cals_and_notes = db.get_preset(context._user_id, context.user_data['preset'])
    cals_in_preset = []
    for tuple in cals_and_notes:
      cals_in_preset.append(tuple[0])

    # add calendars not in preset
    for cal in cals_in_preset:
      context.user_data['reply_keyboard'].remove([cal])

    # no calendars remaining
    if len(context.user_data['reply_keyboard']) == 1:
      await update.message.reply_text(
          'All your calendars are already in this preset. Clear your preset with /presets, then choose "Clear".',
          reply_markup=ReplyKeyboardRemove())
      return ConversationHandler.END
    await update.message.reply_text(
        "Which calendar do you want to add?",
        reply_markup=ReplyKeyboardMarkup(
            context.user_data['reply_keyboard'],
            one_time_keyboard=True,
            input_field_placeholder="Select a calendar"))
    return C

  # notes preferences
  elif response == "Notes preferences":
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No', 'Always ask']],
                                         one_time_keyboard=True))
    return E
# clear, add, notes preferences
async def presetsC(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # process response
  response = update.message.text

  # done before choosing any calendars
  if response == "I am done":
    await update.message.reply_text(
        "You have not chosen any calendars. Choose again with /presets!",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  # all
  elif response == "All":
    # clear preset, then add all calendars
    db.clear_preset(context._user_id, context.user_data['preset'])

    for cal in db.get_my_calendars(context._user_id):
      db.add_to_preset(context._user_id, context.user_data['preset'], cal)
    await update.message.reply_text(f"Added to preset {context.user_data['preset']}.")
    string = f"Preset {context.user_data['preset']}:\n"
    cals_and_notes = db.get_preset(context._user_id, context.user_data['preset'])
    for cal_note in cals_and_notes:
      string += cal_note[0] + " " + db.get_emoji(cal_note[0]) + "\n"
    await update.message.reply_text(string)
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No', 'Always ask']],
                                         one_time_keyboard=True))
    return E

  # one calendar
  if response in db.get_my_calendars(context._user_id):
    db.add_to_preset(context._user_id, context.user_data['preset'], response)
    context.user_data['reply_keyboard'].remove([response])
  else:
    await update.message.reply_text("You do not have access to this calendar")
  await update.message.reply_text(
      "Any more calendars?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return D
# add first calendar (or all) to preset
async def presetsD(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  response = update.message.text

  # done
  if response == "I am done":
    if len(db.get_preset(context._user_id, context.user_data['preset'])) == 0:
      await update.message.reply_text(f"There are no calendars in preset {context.user_data['preset']}.",
                                      reply_markup=ReplyKeyboardRemove())
      return ConversationHandler.END
    string = f"Preset {context.user_data['preset']}:\n"
    cals_and_notes = db.get_preset(context._user_id, context.user_data['preset'])
    for cal_note in cals_and_notes:
      string += cal_note[0] + " " + db.get_emoji(cal_note[0]) + "\n"
    await update.message.reply_text(string)
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No', 'Always ask']],
                                         one_time_keyboard=True))
    return E
    
  # all
  elif response == "All":
    # clear preset, then add all calendars
    db.clear_preset(context._user_id, context.user_data['preset'])

    for cal in db.get_my_calendars(context._user_id):
      db.add_to_preset(context._user_id, context.user_data['preset'], cal)
    await update.message.reply_text(f"Added to preset {context.user_data['preset']}.")
    string = f"Preset {context.user_data['preset']}:\n"
    cals_and_notes = db.get_preset(context._user_id, context.user_data['preset'])
    for cal_note in cals_and_notes:
      string += cal_note[0] + " " + db.get_emoji(cal_note[0]) + "\n"
    await update.message.reply_text(string)
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No', 'Always ask']],
                                         one_time_keyboard=True))
    return E

  # one calendar
  elif response in db.get_my_calendars(context._user_id):
    db.add_to_preset(context._user_id, context.user_data['preset'], response)
    context.user_data['reply_keyboard'].remove([response])
  else:
    await update.message.reply_text("You do not have access to this calendar")
  await update.message.reply_text(
      "Any more calendars?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return D
# more calendars
async def presetsE(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
  # process response
  response = update.message.text
  db.set_notes_for_preset(context._user_id, context.user_data['preset'], response)
  await update.message.reply_text(
      f"Preset updated. View your events quickly with /{context.user_data['preset']}!",
      reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END
# manage notes preferences

# view presets
async def view_preset1(update: Update, context: ContextTypes.DEFAULT_TYPE):
  preset = 1
  cals_and_notes = db.get_preset(context._user_id, preset)

  if len(cals_and_notes) == 0:
    await update.message.reply_text(
        "You don't have any calendars in this preset. Add a few with /presets!")
    return

  cals_in_preset = []
  notes = cals_and_notes[0][1]
  for tuple in cals_and_notes:
    cals_in_preset.append(tuple[0])

  if notes == "Always ask":
    # save cals in context for later
    context.user_data['calendars'] = cals_in_preset
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']],
                                         one_time_keyboard=True))
    return A

  # notes
  elif notes == "Yes":
    events = utils.show_events(cals_in_preset, notes=True)
  elif notes == "No":
    events = utils.show_events(cals_in_preset, notes=False)

  if events == None:
    await update.message.reply_text(
        "There are no events in these calendars. Create a new event with /newevent!"
    )
  else:
    await update.message.reply_text(events, parse_mode=ParseMode.MARKDOWN)
  return ConversationHandler.END
async def view_preset2(update: Update, context: ContextTypes.DEFAULT_TYPE):
  preset = 2
  cals_and_notes = db.get_preset(context._user_id, preset)

  if len(cals_and_notes) == 0:
    await update.message.reply_text(
        "You don't have any calendars in this preset. Add a few with /presets!")
    return

  cals_in_preset = []
  notes = cals_and_notes[0][1]
  for tuple in cals_and_notes:
    cals_in_preset.append(tuple[0])

  if notes == "Always ask":
    # save cals in context for later
    context.user_data['calendars'] = cals_in_preset
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']],
                                         one_time_keyboard=True))
    return A

  # notes
  elif notes == "Yes":
    events = utils.show_events(cals_in_preset, notes=True)
  elif notes == "No":
    events = utils.show_events(cals_in_preset, notes=False)

  if events == None:
    await update.message.reply_text(
        "There are no events in these calendars. Create a new event with /newevent!"
    )
  else:
    await update.message.reply_text(events, parse_mode=ParseMode.MARKDOWN)
  return ConversationHandler.END
async def view_preset3(update: Update, context: ContextTypes.DEFAULT_TYPE):
  preset = 3
  cals_and_notes = db.get_preset(context._user_id, preset)

  if len(cals_and_notes) == 0:
    await update.message.reply_text(
        "You don't have any calendars in this preset. Add a few with /presets!")
    return

  cals_in_preset = []
  notes = cals_and_notes[0][1]
  for tuple in cals_and_notes:
    cals_in_preset.append(tuple[0])

  if notes == "Always ask":
    # save cals in context for later
    context.user_data['calendars'] = cals_in_preset
    await update.message.reply_text(
        "Would you like to see notes from these calendars?",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']],
                                         one_time_keyboard=True))
    return A

  # notes
  elif notes == "Yes":
    events = utils.show_events(cals_in_preset, notes=True)
  elif notes == "No":
    events = utils.show_events(cals_in_preset, notes=False)

  if events == None:
    await update.message.reply_text(
        "There are no events in these calendars. Create a new event with /newevent!"
    )
  else:
    await update.message.reply_text(events, parse_mode=ParseMode.MARKDOWN)
  return ConversationHandler.END
# send events, or ask about notes
async def view_presetA(update: Update, context: ContextTypes.DEFAULT_TYPE):
  response = update.message.text

  if response == "Yes":
    events = utils.show_events(context.user_data['calendars'], notes=True)
  elif response == "No":
    events = utils.show_events(context.user_data['calendars'], notes=False)

  if events == None:
    await update.message.reply_text(
        "There are no events in these calendars. Create a new event with /newevent!",
        reply_markup=ReplyKeyboardRemove())
  else:
    await update.message.reply_text(events,
                                    parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=ReplyKeyboardRemove())
  return ConversationHandler.END
# send events with/without notes

# clear past events
async def clear_past_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if len(db.get_my_calendars(context._user_id)) == 0:
    await update.message.reply_text(
        "You do not have any calendars. Create one with /newcal!")
    return ConversationHandler.END
    
  context.user_data['reply_keyboard'] = []
  for cal in db.get_my_calendars(context._user_id):
    context.user_data['reply_keyboard'].append([cal])
  context.user_data['reply_keyboard'].append(['I am done'])
  context.user_data['reply_keyboard'].append(['All'])

  context.user_data['calendars'] = []

  await update.message.reply_text(
      "Which calendar would you like to clear?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A
async def clear_past_events1(update: Update, context: ContextTypes.DEFAULT_TYPE):
  response = update.message.text

  if response == "I am done":
    if len(context.user_data['calendars']) == 0:
      await update.message.reply_text("You have not chosen any calendars.",
                                      reply_markup=ReplyKeyboardRemove())
      return ConversationHandler.END
    for cal in context.user_data['calendars']:
      for event in db.get_events(cal):
        # manage date and datetime variations
        datetime_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        have_time = bool(datetime_pattern.match(event[0]))
        if have_time:
          date = datetime.datetime.strptime(event[0],
                                            '%Y-%m-%d %H:%M:%S').date()
        else:
          date = datetime.datetime.strptime(event[0], '%Y-%m-%d').date()

        if date < datetime.date.today():
          db.delete_event(event[1], event[2], event[0])
    # remove events
    await update.message.reply_text("Removed events up until yesterday",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


  if response == "All":
    for cal in db.get_my_calendars(context._user_id):
      for event in db.get_events(cal):
        # manage date and datetime variations
        datetime_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        have_time = bool(datetime_pattern.match(event[0]))
        if have_time:
          date = datetime.datetime.strptime(event[0],
                                            '%Y-%m-%d %H:%M:%S').date()
        else:
          date = datetime.datetime.strptime(event[0], '%Y-%m-%d').date()

        if date < datetime.date.today():
          db.delete_event(event[1], event[2], event[0])
    # remove events
    await update.message.reply_text("Removed events up until yesterday",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

  context.user_data['reply_keyboard'].remove([response])
  context.user_data['calendars'].append(response)
  await update.message.reply_text(
      "Any more calendars to clear?",
      reply_markup=ReplyKeyboardMarkup(
          context.user_data['reply_keyboard'],
          one_time_keyboard=True,
          input_field_placeholder="Select a calendar"))
  return A

# dev
async def list_access(update: Update, context: ContextTypes.DEFAULT_TYPE):
  users = db.get_access('demo')
  for user in users:
    await update.message.reply_text(user)
async def list_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
  password = db.get_password('demo')
  await update.message.reply_text(password)
# async def list_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
#   events = db.get_events('demo')
#   await update.message.reply_text(events)
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
  db.drop_table()
  db.setup()
  db.add_calendar('demo', 'password', '🌝', 5)
  db.add_event('demo', 'christmas', datetime.date(2023, 12, 25),
               'This is a demo event')
  db.add_event('demo', 'dinner with mom', datetime.date(2023, 6, 25),
               'This is a demo event')
  await update.message.reply_text("restarted")

