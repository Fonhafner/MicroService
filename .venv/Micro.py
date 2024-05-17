import os
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel

from database_manager import PostgreSQLDatabase

# Настройка базовой конфигурации логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра FastAPI
app = FastAPI()

# Используем bcrypt для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Получение URL подключения к базе данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yolo1204@87.242.119.51:5432/microbase")

# Подключение к базе данных PostgreSQL
db = PostgreSQLDatabase(DATABASE_URL)

# Обработчик статических файлов
app.mount("/static", StaticFiles(directory=Path(__file__).parent.resolve() / "static"), name="static")

# Модель для данных о пользователе
class User(BaseModel):
    username: str
    email: str
    password: str

# Регистрация пользователя
@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    logging.info("Trying to register user: %s", username)  # Запись информации о попытке регистрации
    hashed_password = pwd_context.hash(password)
    await db.create_user(username, email, hashed_password)
    return {"message": "User registered successfully"}

# Аутентификация пользователя
@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    logging.info("Trying to log in user: %s", username)  # Запись информации о попытке входа
    user = await db.get_user_by_username(username)
    if not user or not pwd_context.verify(password, user["passwd"]):  # Исправлено на "passwd"
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Если аутентификация успешна, устанавливаем cookie с именем пользователя
    response = RedirectResponse(url="/main", status_code=303)
    response.set_cookie(key="username", value=username)
    return response

# Обработчики для отображения HTML-страниц
@app.get("/register", response_class=HTMLResponse)
async def get_register_page():
    return FileResponse("static/register.html")

@app.get("/login")
async def get_login_page():
    return FileResponse("static/login.html")

@app.post("/login")
async def post_login_page(request: Request, username: str = Form(...), password: str = Form(...)):
    response = await login(request, username, password)
    # Если авторизация прошла успешно, соединение с базой данных закрываться не должно
    return response

@app.get("/main", response_class=HTMLResponse)
async def main_page(request: Request):
    logging.info("Loading main page")  # Запись информации о загрузке главной страницы
    await db.connect()  # Устанавливаем соединение с базой данных
    username = request.cookies.get("username")
    if not username:
        await db.close()  # Закрываем соединение с базой данных
        return RedirectResponse(url="/login", status_code=303)
    return FileResponse("static/main.html")

# Функция для запуска сервера
def start_app():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_app()
