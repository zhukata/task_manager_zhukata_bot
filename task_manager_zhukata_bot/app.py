import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from task_manager_zhukata_bot.handlers.user_private import user_private_router
from task_manager_zhukata_bot.handlers.admin_private import admin_router
from task_manager_zhukata_bot.common.bot_cmd_list import private

load_dotenv()

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=os.getenv('TOKEN'),default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [678677474, ]

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(admin_router)

 


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    

asyncio.run(main())