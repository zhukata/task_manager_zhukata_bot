from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Список задач'),
            KeyboardButton(text='Добавить задачу'), 
        ],
        [
            KeyboardButton(text='О боте'),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Че?"
)

del_kbd = ReplyKeyboardRemove()