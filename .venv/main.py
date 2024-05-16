import asyncpg
import asyncio

#akjsndkajnskdnaslkdas
async def main():
    # Параметры подключения к базе данных PostgreSQL
    dsn = "postgresql://fonhafner:YoLo1204@localhost:5432/SecretWhisper_DB"

    try:
        # Устанавливаем соединение с базой данных
        connection = await asyncpg.connect(dsn)
        print("Connected to the database")

        # Выполняем запрос к базе данных
        result = await connection.fetch("SELECT 1")
        print("Query executed successfully:", result)

        # Закрываем соединение с базой данных
        await connection.close()
        print("Connection closed")
    except Exception as e:
        print("An error occurred:", e)


# Запускаем асинхронную функцию
asyncio.run(main())
