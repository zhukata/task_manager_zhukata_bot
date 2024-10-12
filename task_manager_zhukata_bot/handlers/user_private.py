from aiogram import Bot, Router, types
from aiogram.filters import CommandStart, Command


user_private_router = Router




@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Привет я твой помощник')

@user_private_router.message(Command('tasks'))
async def echo(message: types.Message):
    await message.answer('Вот ваш список дел на сегодня')