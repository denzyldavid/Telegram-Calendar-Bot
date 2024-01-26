from telegram import Update
from telegram.ext import ContextTypes


def handle_response(text: str):
  processed_text = text.lower()
  if 'hello' in processed_text:
    return 'Hello! :D'
  elif 'how are you' in processed_text:
    return 'I am doing great! :D'
  elif 'what is your name' in processed_text:
    return 'My name is FAM CAL BOT!'
  elif 'what is your purpose' in processed_text:
    return 'My purpose is to help you with your family calendar!'
  elif 'what is your favorite color' in processed_text:
    return 'My favorite color is green!'
  elif 'what is your favorite food' in processed_text:
    return 'My favorite food is pizza!'
  return 'I do not understand, please rephrase!'
  

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  message_type: str = update.message.chat.type
  text: str = update.message.text

  print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

  if message_type == 'group':
    if BOT_USERNAME in text:
      new_text: str = text.replace(BOT_USERNAME, '').strip()
      response: str = handle_response(new_text)
    else:
      return
  else:
    response: str = handle_response(text)

  print('Bot:', response)
  await update.message.reply_text(response)
