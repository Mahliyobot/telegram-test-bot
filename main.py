import asyncio
import logging
import os
import json
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7075322783
CHANNEL_ID = -1002055415694
CHANNEL_LINK = "https://t.me/MAHLIYO_ODILBOYEVA1"

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
        json.dump(data, f, indent=4)

TESTS = load_json(DATA_FILE)
RESULTS = load_json(RESULT_FILE)

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# START
@dp.message(Command("start"))
async def start(message: Message):
    if not await check_subscription(message.from_user.id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)]
        ])
        await message.answer("❌ Kanalga a'zo bo‘ling.", reply_markup=keyboard)
        return
    await message.answer("Test kodi va javobni yuboring.\nMasalan: TEST1 AABBCC")

# ADD TEST
@dp.message(Command("addtest"))
async def add_test(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer("Format: /addtest TEST1 AABBCC [daqiqada]")
            return

        code = parts[1].upper()
        raw_answers = parts[2]
        answers = "".join(re.findall(r"[A-Da-d]", raw_answers)).upper()

        test_data = {
            "answers": answers,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None
        }

        if len(parts) == 4:
            minutes = int(parts[3])
            end_time = datetime.now() + timedelta(minutes=minutes)
            test_data["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")

        TESTS[code] = test_data
        save_json(DATA_FILE, TESTS)

        await message.answer(f"✅ Test qo‘shildi\n📊 Savollar: {len(answers)} ta")
    except:
        await message.answer("Format: /addtest TEST1 AABBCC [daqiqada]")

# TOP
@dp.message(Command("top"))
async def top_results(message: Message):
    try:
        _, code = message.text.split()
        code = code.upper()
    except:
        await message.answer("Format: /top TEST1")
        return

    if code not in RESULTS:
        await message.answer("Natija yo‘q")
        return

    sorted_results = sorted(
        RESULTS[code],
        key=lambda x: (-x["percent"], x["duration"])
    )

    text = "🏆 TOP 10\n\n"
    for i, user in enumerate(sorted_results[:10], start=1):
        medal = "🥇 " if i == 1 else "🥈 " if i == 2 else "🥉 " if i == 3 else ""
        text += f"{medal}{i}. {user['name']} - {user['score']} ({user['duration']}s)\n"

    await message.answer(text)

# CURRENT PDF
@dp.message(Command("current"))
async def current_results(message: Message):
    try:
        _, code = message.text.split()
        code = code.upper()
    except:
        await message.answer("Format: /current TEST1")
        return

    if code not in RESULTS:
        await message.answer("❌ Hali natija yo‘q")
        return

    sorted_results = sorted(
        RESULTS[code],
        key=lambda x: (-x["percent"], x["duration"])
    )

    file_name = f"{code}_current.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"{code} - JORIY HOLAT", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    for i, user in enumerate(sorted_results, start=1):
        text = f"{i}. {user['name']} - {user['score']} - {user['duration']}s"
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    await message.answer_document(FSInputFile(file_name))

# FINAL RESULTS PDF
@dp.message(Command("results"))
async def final_results(message: Message):
    try:
        _, code = message.text.split()
        code = code.upper()
    except:
        await message.answer("Format: /results TEST1")
        return

    if code not in TESTS:
        await message.answer("❌ Test topilmadi")
        return

    test_data = TESTS[code]

    if test_data["end_time"]:
        end_time = datetime.strptime(test_data["end_time"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < end_time:
            await message.answer("⏳ Test hali tugamagan.")
            return

    if code not in RESULTS:
        await message.answer("❌ Natija yo‘q")
        return

    sorted_results = sorted(
        RESULTS[code],
        key=lambda x: (-x["percent"], x["duration"])
    )

    file_name = f"{code}_FINAL_RESULTS.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"{code} - YAKUNIY NATIJA", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    for i, user in enumerate(sorted_results, start=1):
        medal = "🥇 " if i == 1 else "🥈 " if i == 2 else "🥉 " if i == 3 else ""
        text = f"{medal}{i}. {user['name']} - {user['score']} - {user['duration']}s"
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    await message.answer_document(FSInputFile(file_name))

# TEST TEKSHIRISH
@dp.message()
async def check_test(message: Message):

    if not await check_subscription(message.from_user.id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)]
        ])
        await message.answer("❌ Kanalga a'zo bo‘ling.", reply_markup=keyboard)
        return

    try:
        code, raw_answers = message.text.split()
        code = code.upper()
    except:
        return

    if code not in TESTS:
        await message.answer("❌ Test topilmadi")
        return

    test_data = TESTS[code]
    correct = test_data["answers"]

    if test_data["end_time"]:
        end_time = datetime.strptime(test_data["end_time"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > end_time:
            await message.answer("⛔ Test yopilgan.")
            return

    answers = "".join(re.findall(r"[A-Da-d]", raw_answers)).upper()

    if len(answers) != len(correct):
        await message.answer(f"❗ {len(correct)} ta javob yuboring.")
        return

    user_id = str(message.from_user.id)

    if code not in RESULTS:
        RESULTS[code] = []

    for entry in RESULTS[code]:
        if entry["user_id"] == user_id:
            await message.answer("❌ Siz allaqachon topshirgansiz.")
            return

    score = sum(1 for a, b in zip(answers, correct) if a == b)
    percent = round(score / len(correct) * 100, 2)

    start_time = datetime.strptime(test_data["start_time"], "%Y-%m-%d %H:%M:%S")
    duration = int((datetime.now() - start_time).total_seconds())

    RESULTS[code].append({
        "user_id": user_id,
        "name": message.from_user.full_name,
        "score": f"{score}/{len(correct)} ({percent}%)",
        "percent": percent,
        "duration": duration
    })

    save_json(RESULT_FILE, RESULTS)

    await message.answer(
        f"Natija: {score}/{len(correct)} ({percent}%)\n"
        f"⏱ Sarflangan vaqt: {duration} soniya"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
