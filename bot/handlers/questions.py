from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards.for_questions import get_yes_no_kb

router = Router()

@router.message(Command("/review"))
async def get_review(message: Message):
    await message.answer(
        "Спасибо за отзыв!"
    )

@router.message(Command("/survey"))
async def survey(message: Message):
    await message.answer(
        "Вы довольны результатом предсказания модели?",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.lower() == "да")
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "нет")
async def answer_no(message: Message):
    await message.answer(
        "Жаль",
        reply_markup=ReplyKeyboardRemove()
    )