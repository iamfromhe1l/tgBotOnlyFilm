import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook
import os
import logging

TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

wh_host = f'https://{HEROKU_APP_NAME}.herokuapp.com'
wh_path = f'/webhook/{TOKEN}'
wh_url = f'{wh_host}{wh_path}'

user_data = {}
whapp_host = '0.0.0.0'
whapp_port = os.getenv('PORT', default=6666)

logging.basicConfig(level=logging.INFO)



# заполнять tariffs строго по модели tariffs = 'название тарифа': {'spec': ['1ая особенность', '2ая особенность', 'n-ая особенность'], 'price': цена}
tariffs = {
  'Обычный': {
    'spec': [
      'Приватная комната',
      'Экран (30 дюймов)',
      'Удобная кровать 🛏',
      'Фильм из каталога 🎬',
      'Вино Santo Stefano 🍷'
    ],
    'price': 1990
  },
  'Вип': {
    'spec': [
      'Приватная комната',
      'Экран(44 дюймов, FullHD)',
      'Удобная кровать 🛏',
      'Фильм из каталога 🎬',
      'Вино Santo Stefano 🍷',
      'Кальян на выбор 💨'
    ],
    'price': 2490
  },
  'Премиум': {
    'spec': [
      'Экран (44 дюйма4K HD) ',
      'Удобная кровать🛏',
      'Любой фильм 🍿 ',
      'Вино (Torres Caka Sargre de Toro) 🍷',
      'Кальян на выбор 💨',
      'Экзотические фрукты 🍓',
      'Роллы/суши 🍱',
    ],
    'price': 3290
  },
  'Премиум +': {
    'spec': [
      'Экран (48 дюйма4K HD) ',
      'Удобная кровать🛏',
      'Любой фильм 🍿 ',
      'Вино (Torres Caka Sargre de Toro) 🍷',
      'Кальян на выбор 💨',
      'Экзотические фрукты 🍓',
      'Роллы/суши 🍱',
      'Шампанское 🥂',
      'Пачка Durex',
    ],
    'price': 4990
  },

}

cities = {
  'moskow': 'Москва',
  'saint-petersburg': 'Санкт-Петербург',
  'kazan': 'Казань',
  'rostov': 'Ростов',
  'saratov': 'Саратов',
  'kaliningrad': 'Калининград',
  'samara': 'Самара',
  'ulyanovsk': 'Ульяновск',
  'omsk': 'Омск',
  'nizhniy-novgorod': 'Нижний Новгород',
  'krasnodar': 'Краснодар'
}

# ключи для фильма = любое число
films = {
  '1': "Касабланка / Casablanca (1942)",
  '2': "Амели / Le fabuleux destin d'Amélie Poulain (2001)",
  '3': "Девчата (1961)",
  '4': "Поющие под дождем / Singin' in the Rain (1952)",
  '5': "Форрест Гамп / Forrest Gump (1994)",
  '6': "Огни большого города / City Lights (1931)",
  '7': "Вечное сияние чистого разума / Eternal Sunshine of the Spotless Mind (2004)",
  '8': "Еще раз про любовь (1967)",
  '9': "В джазе только девушки / Some Like It Hot (1959)",
  '10': "Умница Уилл Хантинг / Good Will Hunting (1997)",
  '11': "Три идиота / 3 Idiots (2009)",
  '12': "Квартира / The Apartment (1960)",
  '13': "Земляничная поляна / Smultronstället (1957)",
  '14': "Манхэттен / Manhattan (1979)",
  '15': "Красные башмачки / The Red Shoes (1948)",
  '16': "Римские каникулы / Roman Holiday (1953)",
  '17': "Служебный роман (1977)",
  '18': "Москва слезам не верит (1980)",
  '19': "Любовное настроение / Fa yeung nin wah (2000)",
  '20': "Ирония судьбы, или С легким паром! (1975)",
  '21': "Укрощение строптивой / The Taming of the Shrew (1967)",
  '22': "Покровские ворота (1982)",
  '23': "Титаник / Titanic (1997)",
  '24': "Это случилось однажды ночью / It Happened One Night (1934)",
  '25': "Шоколад / Chocolat (2000)",
}

# для каждого ключа(времени) в times соответствует bool значение: True - занято, False - не занято
# inline keyboard с временем будет содержать только времена, которые не заняты
times = {
  '00:00': False,
  '02:00': False,
  '04:00': False,
  '06:00': False,
  '08:00': False,
  '10:00': False,
  '14:00': False,
  '18:00': False,
  '20:00': False,
  '22:00': False,
}

# bot config part
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
  tchoice = State()
  city_choice = State()
  film_choice = State()
  time_choice = State()

@dp.message_handler(Text(contains='/start'), state='*')
async def start_func(message: types.Message):
  await Form.tchoice.set()
  await message.answer('Здравствуйте, Вас приветствуюет бот *OnlyFilms!*', parse_mode='Markdown')
  await message.answer('Выберите желаемый тариф:')

  keys = list(tariffs.keys())
  keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

  for i in range(len(keys)):
    keyboard.add(types.KeyboardButton(keys[i]))

    text = f'-------------*{keys[i].upper()}*-------------' + '\n' + f'{keys[i]} тариф включает в себя:' + "".join("\n  -*"+e+"*" for e in tariffs[keys[i]]['spec']) + '\n' + f'Цена: *{tariffs[keys[i]]["price"]}* 💵'

    if i != len(keys)-1:
      await message.answer(text, parse_mode='Markdown')
    else:
      await message.answer(text, parse_mode='Markdown', reply_markup=keyboard)
    
@dp.message_handler(lambda message: message.text in list(tariffs.keys()), state=Form.tchoice)
async def end_of_choice(message: types.Message, state: FSMContext):
  await Form.city_choice.set()
  async with state.proxy() as data:
    data['total_price'] = tariffs[message.text]['price']
  await message.answer(f'Вы выбрали тариф: {message.text}', reply_markup=types.ReplyKeyboardRemove())
  inline_keyboard = types.InlineKeyboardMarkup()
  for city in cities.keys():
    inline_keyboard.add(types.InlineKeyboardButton(cities[city], callback_data=city))
  await message.answer('Выберите город:', reply_markup=inline_keyboard)

@dp.callback_query_handler(lambda c: c.data in list(cities.keys()), state=Form.city_choice)
async def citytofilm_clb(callback_query: types.CallbackQuery):
  await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
  await bot.send_message(callback_query.from_user.id, text=f'Вы выбрали город: *{cities[callback_query.data]}*', parse_mode='Markdown')
  await Form.film_choice.set()
  film_inline_keyboard = types.InlineKeyboardMarkup()
  for key in films.keys():
    film_inline_keyboard.add(types.InlineKeyboardButton(films[key], callback_data=key))
  await bot.send_message(callback_query.from_user.id, text='Выберите фильм: ', reply_markup=film_inline_keyboard)

@dp.callback_query_handler(lambda c: c.data in list(films.keys()), state=Form.film_choice)
async def filmtotime_clb(callback_query: types.CallbackQuery):
  await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
  await bot.send_message(callback_query.from_user.id, text=f'Вы выбрали фильм: *{films[callback_query.data]}*', parse_mode='Markdown')
  await Form.time_choice.set()
  time_inline_keyboard = types.InlineKeyboardMarkup()
  for key in times.keys():
    if not times[key]:
      time_inline_keyboard.add(types.InlineKeyboardButton(text=key, callback_data=key))
  await bot.send_message(callback_query.from_user.id, text='Выберите время: ', reply_markup=time_inline_keyboard)
  

@dp.callback_query_handler(lambda c: c.data in list(times.keys()), state=Form.time_choice)
async def filmtotime_clb(callback_query: types.CallbackQuery, state: FSMContext):
  await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
  cancel_reply_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).add(types.KeyboardButton(text='Отмена/Сброс корзины/Начать заполнение заказа /start',))
  await bot.send_message(callback_query.from_user.id, text=f'Вы выбрали время: *{callback_query.data}*', parse_mode='Markdown', reply_markup=cancel_reply_keyboard)
  cart_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)
  cart_inline_keyboard.add(types.InlineKeyboardButton(text='Оплтаить', url='google.com'))
  async with state.proxy() as data:
    await bot.send_message(callback_query.from_user.id, text=f'*К ОПЛАТЕ: {data["total_price"]}* руб. 💵' + '\nНЕ ЗАБУДЬТЕ НАПИСАТЬ НИК ТЕЛЕГРАМА В КОММЕНТАРИЯХ К ОПЛАТЕ!!', parse_mode='Markdown', reply_markup=cart_inline_keyboard)
  

# startup function
async def on_startup(dispatcher):
  await bot.set_webhook(wh_url, drop_pending_updates=True)

# shutdown function
async def on_shutdown(dispatcher):
  logging.warning('turning off')
  await bot.delete_webhook()
  await dispatcher.storage.close()
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