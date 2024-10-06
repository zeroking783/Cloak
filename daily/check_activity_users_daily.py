import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from connect_database import *
import os
from delete_client import *

# load_dotenv()
BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
SERVERS_URL = os.getenv("SERVERS_URL")

print(f"Вот переменная BOT_API_TOKEN: {BOT_API_TOKEN}")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_API_TOKEN)

dp = Dispatcher()
db_data = Database(dsn=DATABASE_URL)
db_serv = Database(dsn=SERVERS_URL)

async def main():
    await db_data.init(1, 3)

    await db_serv.init(1, 3)

    # Здесь должен находиться код
    rows = await db_data.fetch("SELECT * FROM connections")

    for row in rows:

        query_web_base_path = """
        SELECT web_base_path FROM servers WHERE ip = $1
        """
        web_base_path = await db_serv.fetchval(query_web_base_path, row[4])

        print("Вот здесь я вывожу row")

        print(row)

        print("Вот здесь я вызываю check_connections и возвращаю result")
        
        result = await check_connections(row, db_serv, web_base_path)

        print(f"Вот сам результ: {result}")

        if result[0] == 1:
            query_delete_connection = "DELETE FROM connections WHERE user_id = $1"
            await bot.send_message(
                row[0],
                text="Уууупс, кажется твоя подписка закончилась"
            )
            await db_data.execute(query_delete_connection, row[0])
        elif result[0] == 2:
            query_delete_connection = "DELETE FROM connections WHERE user_id = $1"
            await bot.send_message(
                row[0],
                text="Уууупс, кажется ты исчерпал все свои биты("
            )
            await db_data.execute(query_delete_connection, row[0])
        elif result[0] == 0:
            query_update_spent_gb = """
            UPDATE connections SET spent_gb = $1 WHERE user_id = $2
            """
            await db_data.execute(query_update_spent_gb, result[1], row[0])


    await db_data.close()
    await db_serv.close()

if __name__ == "__main__":
    asyncio.run(main())
