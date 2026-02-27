import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7075322783
CHANNEL_ID = -1002055415694

DATA_FILE = "tests.json"
RESULT_FILE = "results.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

TESTS = load_json(DATA_FILE)
RESULTS = load_json(RESULT_FILE)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@dp.message(Command("start"))
async def start(message: Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Kanalga a'zo bo‘ling.")
        return
    await message.answer("Test kodi va javobni yuboring.\nMasalan: TEST1 AABBCC")

@dp.message(Command("addtest"))
async def add_test(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, code, answers = message.text.split()
        TESTS[code.upper()] = answers.upper()
        save_json(DATA_FILE, TESTS)
        await message.answer("✅ Test qo‘shildi")
    except:
        await message.answer("Format: /addtest TEST1 AABBCC")

@dp.message(Command("results"))
async def get_results(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, code = message.text.split()
        code = code.upper()
        if code not in RESULTS:
            await message.answer("Natija yo‘q")
            return

        file_name = f"{code}_results.pdf"
        doc = SimpleDocTemplate(file_name)
        styles = getSampleStyleSheet()
        elements = []

        for user in RESULTS[code]:
            elements.append(Paragraph(user, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        doc.build(elements)
        await message.answer_document(FSInputFile(file_name))
    except:
        await message.answer("Format: /results TEST1")

@dp.message()
async def check_test(message: Message):
    if not await check_subscription(message.from_user.id):
        await message.answer("❌ Kanalga a'zo bo‘ling.")
        return

    try:
        code, answers = message.text.split()
        code = code.upper()
        answers = answers.upper()
    except:
        return

    if code not in TESTS:
        await message.answer("❌ Test topilmadi")
        return

    correct = TESTS[code]
    score = sum(1 for a, b in zip(answers, correct) if a == b)
    percent = round(score / len(correct) * 100, 2)

    result_text = f"{message.from_user.full_name} - {score}/{len(correct)} ({percent}%)"

    if code not in RESULTS:
        RESULTS[code] = []

    RESULTS[code].append(result_text)
    save_json(RESULT_FILE, RESULTS)

    await message.answer(f"Natija: {score}/{len(correct)} ({percent}%)")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
