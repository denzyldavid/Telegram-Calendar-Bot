import datetime
import re

from dbhelper import DBHelper

db = DBHelper()


def numToMonth(num):
  return {
      1: '*January*',
      2: '*February*',
      3: '*March*',
      4: '*April*',
      5: '*May*',
      6: '*June*',
      7: '*July*',
      8: '*August*',
      9: '*September*',
      10: '*October*',
      11: '*November*',
      12: '*December*'
  }[num]


def monthToNum(shortMonth):
  return {
      'jan': 1,
      'feb': 2,
      'mar': 3,
      'apr': 4,
      'may': 5,
      'jun': 6,
      'jul': 7,
      'aug': 8,
      'sep': 9,
      'oct': 10,
      'nov': 11,
      'dec': 12
  }[shortMonth]


def show_my_calendars(userid):
  """Show user's calendars"""
  cals = db.get_my_calendars_emoji(userid)
  if len(cals) == 0:
    return None

  string = ""
  for cal in cals:
    string += cal[0] + " " + cal[1] + "\n"
  return string


def show_all_calendars():
  """Shows all calendars in the database"""
  cals = db.get_all_calendars_emoji()
  if len(cals) == 0:
    return None

  string = ""
  for cal in cals:
    string += cal[0] + " " + cal[1] + "\n"
  return string


def show_events(list_of_cals, notes):
  # store events in a list
  # show user the selected cals
  events = []
  string = "Calendars:\n"
  for cal in list_of_cals:
    events.extend(db.get_events(cal))
    emoji = db.get_emoji(cal)
    string += emoji + " " + cal + "\n"

  if len(events) == 0:
    return None
  # sort events by datetime
  events.sort(key=lambda x: x[0])

  string += f"\n\n*This month:* {numToMonth(datetime.date.today().month)}\n"
  string2 = string
  string3 = ""
  last = datetime.date.today()
  first = True
  for event in events:
    # event is a tuple
    event_list = list(event)
    datetime_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    have_time = bool(datetime_pattern.match(event[0]))
    if have_time:
      event_list[0] = datetime.datetime.strptime(event[0], '%Y-%m-%d %H:%M:%S')
    else:
      event_list[0] = datetime.datetime.strptime(event[0], '%Y-%m-%d')
    event = tuple(event_list)

    # check for past events
    if event[0].date() < datetime.date.today():
      if string3 == "":
        string3 = "\n\n\nPast events:\n"

      formatted_date = event[0].strftime("%d/%m/%Y")
      string3 += f"{formatted_date} : {db.get_emoji(event[1])} -- {event[2]}\n"
      if notes and event[3] != "":
        string3 += f"    _{event[3]}_\n"
      continue

    # signposting years, months and days
    if event[0].year != last.year:
      if first:
        string2 += "No events.\n"
      day_name = event[0].strftime("%A")
      string2 += "\n==========*" + str(
          event[0].year) + "*==========\n\n" + numToMonth(
              event[0].month) + "\n\n*" + str(
                  event[0].day) + "* " + day_name + "\n"
      last = event[0]
    elif event[0].month != last.month:
      if first:
        string2 += "No events.\n"
      day_name = event[0].strftime("%A")
      string2 += "\n\n" + numToMonth(event[0].month) + "\n\n*" + str(
          event[0].day) + "* " + day_name + "\n"
      last = event[0]
    elif event[0].day != last.day:
      day_name = event[0].strftime("%A")
      string2 += "\n*" + str(event[0].day) + "* " + day_name + "\n"
      last = event[0]
    elif event[0].day == last.day and first:
      day_name = event[0].strftime("%A")
      string2 += f"\n*TODAY, {str(event[0].day)} {day_name}*\n"
    first = False

    # events
    if have_time:
      if event[0].hour > 12:
        string2 += "    " + str(event[0].hour - 12) + ":" + str(
            event[0].minute).zfill(2) + " pm\n"
      elif event[0].hour == 12:
        string2 += "    " + str(event[0].hour) + ":" + str(
            event[0].minute).zfill(2) + " pm\n"
      elif event[0].hour == 0:
        string2 += "    " + str(event[0].hour + 12) + ":" + str(
            event[0].minute).zfill(2) + " am\n"
      else:
        string2 += "    " + str(event[0].hour) + ":" + str(
            event[0].minute).zfill(2) + " am\n"
    event_emoji = db.get_emoji(event[1])
    string2 += "        " + event_emoji
    string2 += " -- " + event[2] + "\n"
    if notes and event[3] != "":
      string2 += "              _" + event[3] + "_\n"
  if len(string) == len(string2):
    string2 += "No events.\n"
  return string2 + string3


def format_date(date_str, time_str):
  """formats date for events table"""
  if date_str.lower() == 'today':
    date_str = datetime.datetime.today().strftime('%d-%m-%Y')
    date_str_list = date_str.split('-')
    date = [int(item) for item in date_str_list]
  elif date_str.lower() in ['tmr', 'tomorrow']:
    date_str = (datetime.datetime.today() +
                datetime.timedelta(days=1)).strftime('%d-%m-%Y')
    date_str_list = date_str.split('-')
    date = [int(item) for item in date_str_list]
  else:
    date = date_str.split(' ')
    date[0] = int(date[0])
    date[1] = monthToNum(date[1][0:3].lower())
    if len(date) == 2:
      date.append(datetime.date.today().year)
    else:
      date[2] = int(date[2])

  if time_str == "":
    date_without_time = datetime.date(date[2], date[1], date[0])
    return date_without_time

  pm = 0
  splitchar = None
  if "pm" in time_str.lower() and time_str[0:2] != "12":
    pm = 12
  elif "am" in time_str.lower() and time_str[0:2] == "12":
    pm = -12
  time_str = re.sub(r'[a-zA-Z]', '', time_str)
  if "." in time_str:
    splitchar = "."
  elif ":" in time_str:
    splitchar = ":"
  else:
    # only hour (needs logic for 12am and 12pm))
    date_without_time = datetime.datetime(date[2], date[1], date[0],
                                          int(time_str) + pm, 0, 0)
    return date_without_time

  # has : or .
  time = []
  time_str = time_str.split(splitchar)
  for string in time_str:
    time.append(''.join(filter(str.isdigit, string)))
  date_with_time = datetime.datetime(date[2], date[1], date[0],
                                     int(time[0]) + pm, int(time[1]), 0)
  return date_with_time


def have_events(cals):
  """Checks if calendars have events"""
  return bool(db.has_events(cals))


def user_has_events(userid):
  """Checks if user has events in all their calendars"""
  cals = db.get_my_calendars(userid)
  return bool(db.has_events(cals))

