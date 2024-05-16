import unittest
from showusers import get_all_users

class TestShowUsers(unittest.TestCase):

    def test_get_all_users(self):
        # Предположим, что у вас есть мок базы данных, который возвращает список пользователей
        mock_db = Mock()
        mock_db.get_all_usernames.return_value = ["user1", "user2", "user3"]

        # Вызов функции get_all_users с моком базы данных
        users = get_all_users(mock_db)

        # Проверка, что функция возвращает список объектов User
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)

        # Проверка, что каждый элемент списка является объектом User
        for user in users:
            self.assertIsInstance(user, User)
