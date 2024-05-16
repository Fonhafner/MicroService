import unittest
from unittest.mock import AsyncMock, patch
from database_manager import PostgreSQLDatabase

class TestPostgreSQLDatabase(unittest.IsolatedAsyncioTestCase):

    async def test_connect(self):
        # Создаем мок объекта asyncpg.connect
        asyncpg_connect_mock = AsyncMock()

        # Подменяем asyncpg.connect на наш мок
        with patch("database_manager.asyncpg") as asyncpg:
            asyncpg.connect = asyncpg_connect_mock

            # Создаем экземпляр PostgreSQLDatabase
            db = PostgreSQLDatabase("test_dsn")

            # Вызываем метод connect
            await db.connect()

            # Проверяем, что метод asyncpg.connect был вызван
            asyncpg_connect_mock.assert_called_once_with("test_dsn")

if __name__ == '__main__':
    unittest.main()
