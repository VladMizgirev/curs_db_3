import telebot
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Word, New_word, Client, Client_words
from random import choice
from random import shuffle

login = str(input('Введите логин:'))
password = str(input('Введите пароль:'))
name_bd = str(input('Введите название базы данных:'))
DSN = f'postgresql+psycopg2://{login}:{password}@localhost:5432/{name_bd}'
engine = sqlalchemy.create_engine(DSN)

Session = sessionmaker(bind=engine)
session = Session()

state_storage = StateMemoryStorage()
token_bot = input('Введите токен:')
bot = telebot.TeleBot(token_bot)
bot = TeleBot(token_bot, state_storage=state_storage)

def show_hint(*lines):
    return '\n'.join(lines)

def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()
            
@bot.message_handler(commands=['start', 'cards'])
def cards_bot(message):
    user_id = message.chat.id
    data = session.query(Word.id).select_from(Word)
    data_client = session.query(Client).filter(Client.id_client == user_id).all()
    if data_client == []:
        session.add(Client(id_client=user_id))
        session.commit()
        data_client_speshial = session.query(Client.id).filter(Client.id_client == user_id)
        for i in data_client_speshial:
            for e in i:
                need_id = e
        for id_word in data:
            for id_word_need in id_word:
                print(id_word_need)
                session.add(Client_words(id_clients=need_id, id_word_start=id_word_need))
        session.commit()
        bot.send_message(user_id, 'Привет 👋 Давай попрактикуемся в английском языке.'
                         'Тренировки можешь проходить в удобном для себя темпе.'
                          'У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу для обучения.'
                          'Для этого воспрользуйся инструментами:'
                          'добавить слово ➕' 
                          'удалить слово 🔙'
                          'Ну что, начнём ⬇️')
    else:
        marcup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        data_client = session.query(Client.id).filter(Client.id_client == user_id)
        for i in data_client:
            for e in i:
                client_id = e
        data_speshial = session.query(Client_words.id_word_start, Client_words.id_word_new).filter(Client_words.id_clients == client_id)
        data = session.query(Word.rus, Word.en, Word.w_en_1, Word.w_en_2, Word.w_en_3).select_from(Word)
        data_new_word = session.query(New_word.rus, New_word.en, New_word.w_en_1, New_word.w_en_2, New_word.w_en_3).select_from(New_word)
        start_words = []
        new_words = []
        global id_target
        for id_word, id_new_word in data_speshial:
            if id_word is not None:
                start_words.append(id_word)
            if id_new_word is not None:
                new_words.append(id_new_word)
        if new_words != []:
            random_choice = [1, 2]
            random_list = choice(random_choice)
            if random_list == 1:
                id_target = choice(start_words)
            if random_list == 2:
                id_target = choice(new_words)
        else:
            id_target = choice(start_words)
        print(id_target)
        if 1 <= id_target <= 15:
            pub = data.filter(Word.id == id_target).all()
        else:
            pub = data_new_word.filter(New_word.id == id_target).all()
        for rus, en, w_en_1, w_en_2, w_en_3 in pub:
            rus_word = rus
            print(rus_word)
            target_word = en        
            other_word = [w_en_1, w_en_2, w_en_3]
        global buttons
        buttons = []
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)
        other_words_btns = [types.KeyboardButton(word) for word in other_word]
        buttons.extend(other_words_btns)
        shuffle(buttons)
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        buttons.extend([next_btn, add_word_btn, delete_word_btn])
        
        marcup.add(*buttons)
        
        greeting = f"Выбери перевод слова:\n🇷🇺 {rus_word}"
        bot.send_message(message.chat.id, greeting, reply_markup=marcup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = target_word
            data['translate_word'] = rus_word
            data['other_words'] = other_word

@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    cards_bot(message)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    user_id = message.chat.id
    data_client = session.query(Client.id).filter(Client.id_client == user_id)
    for i in data_client:
        for e in i:
            client_id = e
    if 1 <= id_target <= 15:
        session.query(Client_words).filter(Client_words.id_clients == client_id, Client_words.id_word_start == id_target).delete()
        session.commit()
    if 16 <= id_target <= 30:
        session.query(Client_words).filter(Client_words.id_clients == client_id, Client_words.id_word_new == id_target).delete()
        session.commit()
    cards_bot(message)

@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    user_id = message.chat.id
    data_client = session.query(Client.id).filter(Client.id_client == user_id)
    for i in data_client:
        for e in i:
            client_id = e
    data_speshial = session.query(Client_words.id_word_new).filter(Client_words.id_clients == client_id).all()
    list_new_word = []
    for i in data_speshial:
        for e in i:
            if e is not None:
                list_new_word.append(e)
    print(list_new_word)
    if list_new_word == []:
        session.add(Client_words(id_clients=client_id, id_word_new = 16))
        session.commit()
    else:
        new_list_new_word = sorted(list_new_word, reverse=True)
        need_id = new_list_new_word[0]
        new_id_word = need_id + 1
        session.add(Client_words(id_clients=client_id, id_word_new = new_id_word))
        session.commit()
    cards_bot(message)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")

    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)
    if text == target_word:
        cards_bot(message)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    print('Работаем')
    bot.polling()




