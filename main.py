import asyncio
import logging
import os
import time
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = 7075322783
CHANNEL_ID = -1002055415694

TESTS = {
    "TEST1": "AABBCC",
    "TEST2": "ABCABC",
    "TEST3": "CCBBAA"
}

TEST_TIME = 120  # sekund

user_start_time = {}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====== START ======
@dp.message(CommandStart())
async def start_handler(message: Message):
    member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)

    if member.status not in ["member", "administrator", "creator"]:
        await message.answer("❌ Test ishlash uchun kanalga a'zo bo‘ling.")
        return

    await message.answer("Test kodini va javoblaringizni yuboring.\nMasalan: TEST1 AABBCC")

# ====== TEST ISHLASH ======
@dp.message()
async def check_test(message: Message):
    text = message.text.strip().split()

    if len(text) != 2:
        return

    test_code = text[0].upper()
    user_answers = text[1].upper()

    if test_code not in TESTS:
        await message.answer("❌ Test kodi topilmadi.")
        return

    # Vaqtni tekshirish
    if message.from_user.id not in user_start_time:
        user_start_time[message.from_user.id] = time.time()

    if time.time() - user_start_time[message.from_user.id] > TEST_TIME:
        await message.answer("⏰ Vaqt tugadi!")
        return

    correct_answers = TESTS[test_code]

    correct = 0
    for i in range(min(len(user_answers), len(correct_answers))):
        if user_answers[i] == correct_answers[i]:
            correct += 1

    result_text = f"""
TEST KODI: {test_code}
ISM: {message.from_user.full_name}
TO‘G‘RI JAVOB: {correct}/{len(correct_answers)}
"""

    file_name = f"{message.from_user.id}_{test_code}.pdf"
    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("SERTIFIKAT", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(result_text, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)

    await message.answer_document(FSInputFile(file_name))

# ====== ADMIN BUYRUQLARI ======
@dp.message(lambda message: message.from_user.id == ADMIN_ID and message.text.startswith("/addtest"))
async def add_test(message: Message):
    try:
        _, code, answers = message.text.split()
        TESTS[code.upper()] = answers.upper()
        await message.answer(f"✅ {code} qo‘shildi.")
    except:
        await message.answer("Format: /addtest TEST4 ABCABC")

# ====== MAIN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
