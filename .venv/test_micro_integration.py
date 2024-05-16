import unittest
import requests

class TestMicroIntegration(unittest.TestCase):

    def test_register_user(self):
        # Отправляем POST-запрос на регистрацию нового пользователя
        response = requests.post("http://localhost:8000/register", data={"username": "testuser", "email": "test@example.com", "password": "testpassword"})

        # Проверяем, что статус код ответа равен 200 (успешно)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в ответе содержится ожидаемое сообщение
        self.assertIn("User registered successfully", response.text)

    def test_login_user(self):
        # Отправляем POST-запрос на вход пользователя
        response = requests.post("http://localhost:8000/login", data={"username": "hello", "password": "YoLo1204"}, allow_redirects=False)

        # Проверяем, что произошел редирект
        self.assertEqual(response.status_code, 303)

        # Получаем cookie из заголовков ответа
        cookie = response.headers.get("Set-Cookie")

        # Проверяем, что cookie установлен
        self.assertIsNotNone(cookie)

        # Проверяем, что cookie содержит ожидаемое значение
        self.assertIn("username=hello", cookie)

if __name__ == '__main__':
    unittest.main()
