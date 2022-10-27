import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
import os
import logging

TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

wh_host = f'https://{HEROKU_APP_NAME}.heroku.com'
wh_path = f'/webhook/{TOKEN}'
wh_url = f'{wh_host}{wh_path}'

user_data = {}
whapp_host = '0.0.0.0'
whapp_port = os.getenv('PORT', default=6666)

logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher(bot)

# main bot handlers
@dp.message_handler(commands='start')
async def start_func(message: types.Message):
  await message.reply('Hi, bro!')


# startup function
async def on_startup(dispatcher):
  await bot.set_webhook(wh_url, drop_pending_updates=True)

# shutdown function
async def on_shutdown(dispatcher):
  logging.warning('turning off')
  await bot.delete_webhook()
  await dp.storage.close()
  logging.warning('bye ;)')

if __name__ == '__main__':
  print(whapp_host, whapp_port)
  start_webhook(
    dispatcher=dp,
    webhook_path=wh_path,
    skip_updates=True,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
    host=whapp_host,
    port=whapp_port
  )