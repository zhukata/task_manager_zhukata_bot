from aiogram import F, Bot, Router, types
from aiogram.filters import CommandStart, Command, or_f

from task_manager_zhukata_bot.filters.chat_types import ChatTypeFilter
from task_manager_zhukata_bot.keyboards import reply

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))



@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Привет, я твой помощник", reply_markup=reply.start_kb2.as_markup())

@user_private_router.message(or_f(Command('tasks'), F.text.contains("Список задач")))
async def tasks(message: types.Message):
    await message.answer("Вот ваш список задач на сегодня", reply_markup=reply.del_kbd)

# @user_private_router.message(or_f(Command('add'), F.text.lower().contains('задачу')))
# async def add_task(message: types.Message):
#     await message.answer("Добавить задачу")

@user_private_router.message(F.text.lower().contains('опрос'))
async def add_task(message: types.Message):
    await message.answer('опрос', reply_markup=reply.test_kb)

@user_private_router.message(or_f(Command('about'), F.text.contains("О боте")))
async def add_task(message: types.Message):
    await message.answer("Я бот менеджер задач")

@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f"номер получен")
    await message.answer(str(message.contact))

@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f"локация получена")
    await message.answer(str(message.location))

# @user_private_router.message(F.text)
# async def echo(message: types.Message):
#     await message.answer("Не понял...")