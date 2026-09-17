import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery
)

# ============================================================
# ТОКЕН 
# ============================================================
BOT_TOKEN = "8849161496:AAGwF8HHPCPg5dHluTky1TIuqOYDdfJzDVY"

# ============================================================
# ТВОЙ ID — 8787012224
# ============================================================
ADMIN_ID =7572058322
# ============================================================
CHANNEL_LINK = "https://t.me/+xxxxxxxx"

PRODUCTS = {
    "access": {
        "name": "Доступ в закрытый канал",
        "desc": "Приватный канал на 30 дней",
        "price": 100,
        "type": "link",
        "value": CHANNEL_LINK,
    },
    "guide": {
        "name": "PDF-гайд",
        "desc": "Полезная инструкция в PDF",
        "price": 50,
        "type": "text",
        "value": "Вот твой гайд: https://example.com/guide.pdf",
    },
    "vip": {
        "name": "VIP-подписка",
        "desc": "Доступ на 90 дней + бонусы",
        "price": 250,
        "type": "link",
        "value": CHANNEL_LINK,
    },
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")],
    ])


def catalog_menu():
    rows = []
    for pid, p in PRODUCTS.items():
        rows.append([InlineKeyboardButton(
            text=f"{p['name']} — {p['price']} ⭐",
            callback_data=f"buy:{pid}"
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Это магазин. Выбери товар и оплати звёздами Telegram ⭐",
        reply_markup=main_menu()
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ Помощь\n\n/start — меню\n/help — справка\n\n"
        "Оплата через Telegram Stars. Товар выдаётся сразу."
    )


@dp.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery):
    await call.message.edit_text("🛒 Каталог товаров:", reply_markup=catalog_menu())
    await call.answer()


@dp.callback_query(F.data == "back")
async def back_to_menu(call: CallbackQuery):
    await call.message.edit_text("Главное меню:", reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "help")
async def help_cb(call: CallbackQuery):
    await call.message.edit_text(
        "ℹ️ Оплата звёздами Telegram. Товар выдаётся сразу после оплаты.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ])
    )
    await call.answer()


@dp.callback_query(F.data.startswith("buy:"))
async def buy_product(call: CallbackQuery):
    pid = call.data.split(":")[1]
    product = PRODUCTS.get(pid)
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return

    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title=product["name"],
        description=product["desc"],
        payload=f"product:{pid}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=product["name"], amount=product["price"])],
    )
    await call.answer()


@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def on_paid(message: Message):
    payload = message.successful_payment.invoice_payload
    pid = payload.split(":")[1]
    product = PRODUCTS.get(pid)

    if not product:
        await message.answer("✅ Оплата прошла, но товар не найден. Напиши админу.")
        return

    await message.answer(
        f"✅ Оплата прошла!\n\nТовар: {product['name']}\n\n{product['value']}"
    )

    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"💰 Новая продажа!\nТовар: {product['name']}\n"
                f"Цена: {product['price']} ⭐\n"
                f"Покупатель: {message.from_user.full_name} "
                f"(@{message.from_user.username}, id {message.from_user.id})"
            )
        except Exception as e:
            logging.warning(f"Не смог уведомить админа: {e}")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
