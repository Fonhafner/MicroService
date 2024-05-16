from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from keycloak import KeycloakOpenID
from pydantic import BaseModel


# Настройка базовой конфигурации логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение к Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/auth/",
    client_id="givemetoken",
    realm_name="helpmeplease",
    client_secret_key="lI04AeNwkChC90SXweq60uAGhrmiTmSx"
)

# Обработчик статических файлов
app.mount("/static", StaticFiles(directory=Path(__file__).parent.resolve() / "static"), name="static")

# Модель для данных о пользователе
class User(BaseModel):
    username: str
    email: str
    password: str

# Обработчик для регистрации пользователя
@app.post("/register")
async def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Здесь должна быть логика регистрации пользователя
    logging.info("Попытка регистрации пользователя: %s", username)
    # В этом примере пока просто перенаправим на страницу входа
    return RedirectResponse(url="/login", status_code=303)

# Аутентификация пользователя с помощью Keycloak
async def authenticate_user(username: str, password: str):
    try:
        token = await keycloak_openid.token(username, password)
        return token
    except Exception as e:
        if "invalid_grant" in str(e) and "Account is not fully set up" in str(e):
            logging.warning("Аккаунт не настроен полностью, продолжаем выполнение программы")
            return True  # Возвращаем True, чтобы продолжить выполнение программы
        logging.error("Ошибка при аутентификации: %s", str(e))
        return None

# Обработчик для аутентификации пользователя
@app.post("/login/")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    logging.info("Попытка входа пользователя: %s", username)
    token = await authenticate_user(username, password)
    if token:
        response = RedirectResponse(url="/main", status_code=303)
        response.set_cookie(key="access_token", value=token['access_token'])
        return response
    else:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")

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
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login", status_code=303)
    # Здесь может быть ваша логика проверки токена и обработки запроса
    return FileResponse("static/main.html")

# Функция для запуска сервера
def start_app():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_app()
