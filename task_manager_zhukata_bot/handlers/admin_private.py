from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from task_manager_zhukata_bot.database.orm_query import orm_add_product, orm_get_products
from task_manager_zhukata_bot.filters.chat_types import ChatTypeFilter, IsAdmin
from task_manager_zhukata_bot.keyboards.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Добавить задачу",
    "Список задач",
    placeholder="Выберите действие",
    sizes=(2,),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Список задач")
async def starring_at_product(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            # reply_markup=get_callback_btns(
            #     btns={
            #         "Удалить": f"delete_{product.id}",
            #         "Изменить": f"change_{product.id}",
            #     }
            # ),
        )
    await message.answer("ОК, вот список товаров ⏫")


#Код ниже для машины состояний (FSM)

class AddTask(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddTask:name': 'Введите название заново:',
        'AddTask:description': 'Введите описание заново:',
        'AddTask:price': 'Введите стоимость заново:',
        'AddTask:image': 'Этот стейт последний, поэтому...',
    }


@admin_router.message(StateFilter(None), F.text == "Добавить задачу")
async def add_task(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название задачи", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddTask.name)


@admin_router.message(StateFilter('*'), Command("отмена"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command("назад"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    
    current_state = await state.get_state()
    
    if current_state == AddTask.name:
        await message.answer('Предидущего шага нет, или введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddTask.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddTask.texts[previous.state]}")
            return
        previous = step
    
    await message.answer(f"ок, вы вернулись к прошлому шагу")

@admin_router.message(AddTask.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание задачи")
    await state.set_state(AddTask.description)

#Хендлер для отлова некорректных вводов для состояния name
# @admin_router.message(AddTask.name)
# async def add_name2(message: types.Message, state: FSMContext):
#     await message.answer("Вы ввели не допустимые данные, введите текст названия товара")


@admin_router.message(AddTask.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость задачу")
    await state.set_state(AddTask.price)


@admin_router.message(AddTask.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение задачи")
    await state.set_state(AddTask.image)


@admin_router.message(AddTask.image, F.photo)
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    try:
        await orm_add_product(session, data)
        await message.answer("задача добавлена", reply_markup=ADMIN_KB)
        await state.clear()

    except:
        await message.answer(f"Error")
        await state.clear()