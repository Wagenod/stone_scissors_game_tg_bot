import os
import logging
import pickle
import random
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import STATS_DB, UNICODE_MAPPING, BEATS_DICT

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ.get("BOT_TOKEN"))
bot.scores = dict()
bot.game_state = dict()

dp = Dispatcher(bot, storage=MemoryStorage())
stats_info = {"wins": 0, "defeats": 0}

gif_fiele_id = {'victory': None, 'defeat': None}


@dp.message_handler(commands="start")
async def open_main_menu(message: types.Message):
    kb = [
      [
        types.KeyboardButton(text="Новая игра"),
        types.KeyboardButton(text="Статистика")
      ],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                         input_field_placeholder="Выбираем ....", is_persistent = True)
    await message.answer("Выбери действие:", reply_markup=keyboard)
    logging.info("Bot started")


@dp.message_handler(filters.Text(equals="Новая игра"))
async def new_game(message: types.Message):

    logging.info("New game started")
    bot.scores[message.from_user.username] = {"player": 0, "bot": 0}
    bot.game_state[message.from_user.username] = None

    buttons = [
        [types.InlineKeyboardButton(text="Камень", callback_data="stone_step"),
        types.InlineKeyboardButton(text="Ножницы", callback_data="scissors_step"),
        types.InlineKeyboardButton(text="Бумага", callback_data="paper_step")]
    ]
    await message.answer("Сделай шаг навстречу мне ....", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))


@dp.callback_query_handler(filters.Text(endswith="_step"))
async def do_game_step(call: types.CallbackQuery):
    answer_msg_pattern = "You - Bot \n {} - {} \n    {} - {}"
    player_choice = call.data.split("_")[0]
    username = call.from_user.username
    bot_choice = random.choice(["stone", "paper", "scissors"])

    global stats_info, gif_fiele_id

    if player_choice != bot_choice:
        if BEATS_DICT[player_choice] == bot_choice:
            bot.scores[username]['player'] += 1
        else:
            bot.scores[username]['bot'] += 1
    logging.info(f"Player: {player_choice} - Bot: {bot_choice}")
    await call.message.answer(answer_msg_pattern.format(UNICODE_MAPPING[player_choice],
                                                        UNICODE_MAPPING[bot_choice],
                                                        bot.scores[username]['player'],
                                                        bot.scores[username]['bot']))
    if bot.scores[username]['player'] == 3:
        bot.game_state[username] = 'victory'
        stats_info['wins'] += 1
    elif bot.scores[username]['bot'] == 3:
        bot.game_state[username] = 'defeat'
        stats_info['defeats'] += 1
    print(bot.game_state)
    if bot.game_state[username]:
        logging.info(bot.game_state[username])
        if gif_fiele_id[bot.game_state[username]] is None:
            logging.info("Read gif from local")
            sent_message = await call.message.answer_animation(animation=open(f"static/{bot.game_state[username]}.gif", 'rb'))
            gif_fiele_id[bot.game_state[username]] = sent_message.animation.file_id
        else:
            logging.info("Read gif from tg server")
            await call.message.answer_animation(gif_fiele_id[bot.game_state[username]])

    with open(STATS_DB, "wb") as file:
        pickle.dump(stats_info, file)


@dp.message_handler(filters.Text(equals="Статистика"))
async def get_stats(message: types.Message):
    with open(STATS_DB, 'rb') as f:
        stats = pickle.load(f)

    await message.answer(f"---------------\nWins     : <b>{stats['wins']}</b> \nDefeats: <b>{stats['defeats']}</b>\n--------------",
                         parse_mode=types.ParseMode.HTML)
    logging.info("Stats printed")


if __name__ == "__main__":
    if not os.path.exists(STATS_DB):
        logging.info("New pickle stats file created")
        with open(STATS_DB, 'wb') as f:
            pickle.dump(stats_info, f)
    else:
        with open(STATS_DB, 'rb') as f:
            stats_info = pickle.load(f)

    executor.start_polling(dp, skip_updates=True)

