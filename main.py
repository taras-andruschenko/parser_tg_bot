import os

from aiogram import Bot, Dispatcher, executor, types
from config import NUM_PROD_ON_ONE_PAGE
from keyboards import inline_keyboard_search, inline_keyboard
from parse import parse

token = os.environ["TOKEN"]


def run_bot():
    bot = Bot(token=token)
    dp = Dispatcher(bot=bot)

    page = 0
    products_list = []

    async def on_startup(_):
        print("Started!")

    @dp.message_handler(commands=["start"])
    async def cmd_start(message: types.Message) -> None:
        nonlocal page, products_list
        page = 0
        products_list = []
        await message.answer(text="Введіть пошуковий запит..")

    async def send_page_products(message: types.Message) -> None:
        nonlocal products_list, page
        start_point = page * NUM_PROD_ON_ONE_PAGE
        end_point = start_point + NUM_PROD_ON_ONE_PAGE
        for i in range(start_point, end_point):
            try:
                await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=products_list[i].image,
                    caption=f"{products_list[i].title}\n"
                            f"арт. {products_list[i].id}\n"
                            f"ціна: {products_list[i].price} UAH"
                )
            except (IndexError, AttributeError):
                print("There are no more products")
                break

    @dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("btn"))
    async def send_next_page(callback: types.CallbackQuery) -> None:
        """
        This function handle inline keyboard buttons and
        send products from the next pages if any
        """
        nonlocal products_list, page
        if callback.data == "btn_next":
            page += 1
            cup = len(products_list) // 11
            await send_page_products(callback.message)
            if cup > page:
                await bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="Відобразити ще? натисни кнопку 'Так'!",
                    reply_markup=inline_keyboard,
                )
                await callback.answer(text="Завантажено..")
            elif cup == page:
                await bot.send_message(
                    chat_id=callback.message.chat.id,
                    text="Шукати інший товар?",
                    reply_markup=inline_keyboard_search,
                )
                await callback.answer(text="Завантажено..")
        elif callback.data == "btn_search":
            await cmd_start(callback.message)

    @dp.message_handler()
    async def send_products(message: types.Message = None) -> None:
        """
        This function validates the input data and
        returns products from the first page
        """
        nonlocal products_list
        if not len(message.text) > 1:
            await message.answer(
                text="В запиті має бути більше ніж 1 буква.. "
                     "Чим детальніший запит, тим краще"
            )
            await cmd_start(message=message)
            return
        await message.answer(text="Завантажую..")
        products_list = parse(message.text)
        if not products_list:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Товарів не знайдено.. Введіть новий запит"
            )
        else:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"Всього по запиту знайдено {len(products_list)} товарів!"
            )
            await send_page_products(
                message=message,
            )
            if len(products_list) > 10:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Відобразити ще? натисни кнопку 'Так'!",
                    reply_markup=inline_keyboard,
                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Шукати інший товар?",
                    reply_markup=inline_keyboard_search,
                )

    executor.start_polling(
        dispatcher=dp,
        skip_updates=True,
        on_startup=on_startup,
    )


if __name__ == "__main__":
    run_bot()
