import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from connect_database import *
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
import os

from find_empty_server import find_server
from new_client import *

load_dotenv()

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
TIME_GET_CLIENT = os.getenv("TIME_GET_CLIENT")
GB_GET_CLIENT = os.getenv("GB_GET_CLIENT")

bot = Bot(token=BOT_API_TOKEN)

dp = Dispatcher()
db = Database(dsn=DATABASE_URL)



# Пока делаю с учетом того, что ее нажмут только в самом начале
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    
    await bot.delete_message(message.chat.id, message.message_id)

    await send_main_menu(message.from_user.id, message.from_user.username)

    query = "INSERT INTO users (user_id, username, state) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING"
    await db.execute(query, message.from_user.id, message.from_user.username, "main")

    await update_state(message.from_user.id, "main")



@dp.message(Command("main"))
async def cmd_start(message: types.Message):

    await bot.delete_message(message.chat.id, message.message_id)
    if get_user_state(message.from_user.id) != "main":
        await send_main_menu(message.from_user.id, message.from_user.username)
        await update_state(message.from_user.id, "main")



# Вызов главного меню командой (Пока просто нет такой кнопки)
# @dp.message(Command("main"))
# async def main_menu_command(message: types.Message):
#     await update_state(message.from_user.id, "main")
#     await bot.delete_message(message.chat.id, message.message_id)
#     if not await get_user_state(message.from_user.id) == "main":
#         await send_main_menu(message.from_user.id, message.from_user.username)



# Главное меню
async def send_main_menu(user_id, username):

    query = "SELECT name_client FROM users WHERE user_id = $1"
    name_client = await db.fetchval(query, user_id)

    builder_full = InlineKeyboardBuilder()
    builder_full.add(
        types.InlineKeyboardButton(
            text="Создать подключение",
            callback_data="create_connections"),
        types.InlineKeyboardButton(
            text="Инструкция по установке",
            callback_data="instruction_menu"),
        types.InlineKeyboardButton(
            text="Бонус",
            callback_data="referal_menu"),
        types.InlineKeyboardButton(
            text="Мои рефералы",
            callback_data="users_referals"),
        types.InlineKeyboardButton(
            text="Регистрация",
            callback_data="registration")
    )
    builder_full.adjust(1)

    builder_user = InlineKeyboardBuilder()
    builder_user.add(
        types.InlineKeyboardButton(
            text="Инструкция по установке",
            callback_data="instruction_menu"),
        types.InlineKeyboardButton(
            text="Бонус",
            callback_data="referal_menu"),
        types.InlineKeyboardButton(
            text="Мои рефералы",
            callback_data="users_referals")
    )
    builder_user.adjust(1)

    # Проверяем, имеет ли пользователь активное подключение
    if await check_cell_connection(user_id):
        # Пользователь имеет активное подключение
        query_info_connection = """
        SELECT url_client, paid_up_to_time, spent_gb
        FROM connections
        WHERE user_id = $1
        """
        info_connection = await db.fetchrow(query_info_connection, user_id)

        await bot.send_message(
            user_id,
            f"tg_username: <b>{username}</b>\n"
            f"tg_id: <b>{user_id}</b>\n"
            f"У тебя есть активное подключение\n"
            f"Активно до:\n"
            f"<b>{info_connection['paid_up_to_time']}</b>\n"
            f"Гб осталось\n"
            f"<b>{int(GB_GET_CLIENT) - info_connection['spent_gb']}</b>\n"
            "Твоя ссылка для подключения:\n"
            f"<code>{info_connection['url_client']}</code>\n"
            f"Регистрационное имя:\n"
            f"<b>{name_client}</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=builder_user.as_markup()
        )
    else:
        # Пользователь не имеет активного подключения
        if name_client:
            await bot.send_message(
                user_id,
                f"tg_username: <b>{username}</b>\n"
                f"tg_id: <b>{user_id}</b>\n"
                f"Регистрационное имя:\n"
                f"<b>{name_client}</b>",
                parse_mode=ParseMode.HTML,
                reply_markup=builder_full.as_markup()
            )
        else:
            await bot.send_message(
                user_id,
                f"@tg_username: <b>{username}</b>\n"
                f"@tg_id: <b>{user_id}</b>\n",
                parse_mode=ParseMode.HTML,
                reply_markup=builder_full.as_markup()
            )


# Кнопка, которая создает новое подключение
@dp.callback_query(F.data == "create_connections")
async def create_connections(callback: types.CallbackQuery):

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Отправил",
            callback_data="send_money_is_done"
        )
    )

    if not await check_cell_input_name(callback.from_user.id):
        await callback.answer(
            text="Сначала тебе нужно пройти регистрацию",
            show_alert=True
        )
    else:
        await update_state(callback.from_user.id, "wait_send_money")

        if await user_present_in_the_table(callback.from_user.id) or await user_is_always_true(callback.from_user.id):
            query_1 = """
            INSERT INTO payments_record (user_id, username, payment_method, data_payment, name_client_now, payment_processed, payment_approval)
            VALUES ($1, $2, $3, NOW(), $4, $5, $6)
            """
            query_2 = ("SELECT name_client FROM users WHERE user_id = $1")
            name_client = await db.fetchval(query_2, callback.from_user.id)

            await db.execute(query_1, callback.from_user.id, callback.from_user.username, "SBP", name_client, False, False )

        await bot.send_message(
            callback.from_user.id,
            text="<b>Читай внимательно</b>\nТебе нужно "
                 "отправить 70 рублей на Сбербанк по номеру телефона 89874410512. "
                 "После платежа обязательно нажми кнопку 'Отправил' под этим сообщением. "
                 "Если ты не нажмешь кнопку",
            parse_mode=ParseMode.HTML,
            reply_markup=builder.as_markup()
        )

# Кнопка, которая создает новое подключение
@dp.callback_query(F.data == "send_money_is_done")
async def create_connections(callback: types.CallbackQuery):
    query_1 = """
    UPDATE payments_record 
    SET payment_processed = True, data_payment = NOW() 
    WHERE user_id = $1 AND payment_processed = False
    """
    await db.execute(query_1, callback.from_user.id)

    query_2 = """
    SELECT id_payment FROM payments_record WHERE user_id = $1 AND payment_processed = True AND payment_approval = False
    """
    id_payment = await db.fetchval(query_2, callback.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="Принять",
            callback_data=f"approve_payment:{id_payment}"
        ),
        types.InlineKeyboardButton(
            text="Отклонить",
            callback_data=f"reject_payment:{id_payment}"
        )
    )

    message_to_me = ("<b>user_id</b>: " + str(callback.from_user.id) + "\n" 
                    "<b>username</b>: " + str(callback.from_user.username) + "\n"
                    "<b>name_payment</b>: " + str(await db.fetchval("SELECT name_client_now "
                                                                    "FROM payments_record "
                                                                    "WHERE user_id = $1 "
                                                                    "AND payment_processed = True "
                                                                    "AND payment_approval = False",
                                                                    callback.from_user.id)) + "\n" 
                    "<b>data_payment</b>: " + str(await db.fetchval("SELECT data_payment "
                                                                    "FROM payments_record "
                                                                    "WHERE user_id = $1 "
                                                                    "AND payment_processed = True "
                                                                    "AND payment_approval = False",
                                                                    callback.from_user.id)) + "\n" 
                    "<b>payment_method</b>: " + str(await db.fetchval("SELECT payment_method "
                                                                    "FROM payments_record "
                                                                    "WHERE user_id = $1 "
                                                                    "AND payment_processed = True "
                                                                    "AND payment_approval = False",
                                                                    callback.from_user.id))
                     )

    await bot.send_message(
        566646763,
        text = message_to_me,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup()
    )

# Функция для обработки принятия платежа
@dp.callback_query(F.data.startswith("approve_payment:"))
async def approve_payment(callback: types.CallbackQuery):
    id_payment = int(callback.data.split(":")[1])

    query_1 = """
    UPDATE payments_record
    SET payment_approval = True
    WHERE id_payment = $1
    """

    await db.execute(query_1, id_payment)

    query_2 = """
    SELECT user_id, username
    FROM payments_record
    WHERE id_payment = $1;
    """

    user_id_username = await db.fetchrow(query_2, id_payment)
    user_id = user_id_username['user_id']
    username = user_id_username['username']
    best_server = await find_server()
    best_server.append(username)
    best_server.append(user_id)
    info_connections = await new_client(best_server)

    query_add_client = """
            INSERT INTO connections (user_id, username, url_client, uuid, ip_server, paid_up_to_time, spent_gb)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id) DO NOTHING;
            """

    await db.execute(query_add_client, user_id, username, info_connections[0],
                     info_connections[1], info_connections[2], info_connections[3], 0)

    print(f"!!!!! USER_ID : {user_id}")
    print(f"!!!! INFO_CONNECTIONS: {info_connections}")
    await bot.send_message(
        user_id,
        text=info_connections[0]
    )


@dp.callback_query(F.data.startswith("reject_payment:"))
async def approve_payment(callback: types.CallbackQuery):
    id_payment = int(callback.data.split(":")[1])

    query_1 = """
            SELECT user_id, username
            FROM payments_record
            WHERE id_payment = $1;
            """

    user_id_username = await db.fetchrow(query_1, id_payment)

    await bot.send_message(
        user_id_username[0],
        text="Я не нашел твоей платежки, если ты все таки оплачивал, то напиши админу"
    )

    query_2 = """
           DELETE FROM payments_record
           WHERE id_payment = $1
           """

    await db.execute(query_2, id_payment)

@dp.callback_query(F.data == "registration")
async def registration_procedure(callback: types.CallbackQuery):

    await update_state(callback.from_user.id, "input_name")

    await bot.edit_message_text(
        text = f"Для регистрации отправь свое имя, отчество и первую букву фамилии (информация, которая выводится при переводе на карту).\n\n"
        f"<i>Это нужно исключительно для того, чтобы админ мог проверить оплату VPN.\n</i>"
        f"<i>Если будут отправленны не те данные, то админ не сможет удостовериться в вашем переводе</i>",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        parse_mode=ParseMode.HTML
    )

# Функция обрабатывает все обычные сообщения от пользователя, пока только ввод имени отчества
@dp.message(F.text)
async def save_name_user(message: types.Message):

    if await get_user_state(message.from_user.id) == "input_name":
        query = "UPDATE users SET name_client  = $1 WHERE user_id = $2"
        await db.execute(query, message.text, message.from_user.id)
        await send_main_menu(message.from_user.id, message.from_user.username)
    else:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

# Функция, которая обновляет состояние пользователя
async def update_state(user_id, state):
    query = "UPDATE users SET state = $1 WHERE user_id = $2"
    await db.execute(query, state, user_id)

# Функция возвращает state пользователя
async def get_user_state(user_id):
    query = "SELECT state FROM users WHERE user_id = $1"
    state = await db.fetchval(query, user_id)
    return state

# Функция возвращает true, если в таблице payments_record нет такого user_id
async def user_present_in_the_table(user_id):
    query = """
    SELECT NOT EXISTS (
        SELECT 1 
        FROM payments_record
        WHERE user_id = $1
    ) AS is_not_exists; 
    """
    return await db.fetchval(query, user_id)

# Функция возвращает true, если в payment_record у всех прошлых записях в payment_processed везде стоит true у этого user_id
async def user_is_always_true(user_id):
    query = """
    SELECT NOT EXISTS (
        SELECT 1
        FROM payments_record
        WHERE user_id = $1
        AND payment_approval = false
    ) AS all_processed
    """
    return await db.fetchval(query, user_id)

# Получает информацию есть ли у пользователя активное подключение
async def check_cell_connection(user_id):
    query = "SELECT url_client FROM connections WHERE user_id = $1"
    url_client = await db.fetchval(query, user_id)
    return url_client is not None

# Получает информацию зарегестрирован ли пользователь
async def check_cell_input_name(user_id):
    query = "SELECT name_client FROM users WHERE user_id = $1"
    name_client = await db.fetchval(query, user_id)
    return name_client is not None

async def it_is_new_create_connection(user_id):
    query = ("SELECT "
             "CASE "
             "WHEN EXISTS ("
             "SELECT 1 "
             "FROM payments_record "
             "WHERE user_id = $1 "
             "AND payment_processed = false "
             ") THEN TRUE "
             "ELSE FALSE "
             "END as result;")
    otvet = await db.fetchval(query, user_id)
    return otvet


async def main():
    await db.init(5, 20)
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())















