from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database_manager import PostgreSQLDatabase
import logging
import os

# Настройка базовой конфигурации логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра FastAPI и Jinja2Templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Получение URL подключения к базе данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yolo1204@87.242.119.51:5432/microbase")

# Подключение к базе данных PostgreSQL
db = PostgreSQLDatabase(DATABASE_URL)

# Модель для данных о пользователе
class User:
    def __init__(self, username: str):
        self.username = username

# Эндпоинт для отображения списка пользователей на HTML-странице
@app.get("/users", response_class=HTMLResponse)
async def get_users(request: Request):
    logging.info("Getting all users")  # Запись информации о получении всех пользователей
    users = await db.get_all_usernames()
    users_data = [User(username=user) for user in users]
    return templates.TemplateResponse("users.html", {"request": request, "users": users_data})

# Функция для запуска сервера
def start_app():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    start_app()
