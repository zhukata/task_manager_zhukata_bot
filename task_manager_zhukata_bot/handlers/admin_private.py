from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from task_manager_zhukata_bot.filters.chat_types import ChatTypeFilter, IsAdmin
from task_manager_zhukata_bot.keyboards.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Добавить задачу",
    "Изменить задачу",
    "Удалить задачу",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2, 1, 1),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_Task(message: types.Message):
    await message.answer("ОК, вот список задач")


@admin_router.message(F.text == "Изменить задачу")
async def change_Task(message: types.Message):
    await message.answer("ОК, вот список задач")


@admin_router.message(F.text == "Удалить задачу")
async def delete_Task(message: types.Message):
    await message.answer("Выберите задачу(и) для удаления")


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
async def add_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer("задача добавлена", reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()