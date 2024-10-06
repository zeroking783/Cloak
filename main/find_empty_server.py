from dotenv import load_dotenv
import os
import asyncpg

# Загрузка переменных окружения
load_dotenv()

# Получение URL базы данных из переменной окружения
SERVERS_URL = os.getenv("SERVERS_URL")

# Асинхронная функция для поиска и добавления сервера
async def find_server():
    try:
        # Устанавливаем соединение с базой данных
        conn = await asyncpg.connect(SERVERS_URL)

        # SQL-запрос для вставки данных
        query_1 = """
        SELECT ip, port, login, pass, web_base_path
        FROM servers
        ORDER BY count_connect ASC
        LIMIT 1;
        """

        # Выполняем запрос с передачей данных
        best_server = await conn.fetchrow(query_1)

        if best_server:
            print(f"!!!! BEST SERVERS: {best_server}")
            query_2 = """
            UPDATE servers
            SET count_connect = count_connect + 1
            WHERE ip = $1;
            """
            await conn.execute(query_2, best_server[0])

            await conn.close()

            return [best_server['ip'], best_server['port'], best_server['login'], best_server['pass'], best_server['web_base_path']]
        else:
            await conn.close()
            print("Не удалось достать ip и port из servers")

    except Exception as e:
        # Обрабатываем ошибку
        print(f"Ошибка: {e}")
