import logging
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, Response, FileResponse, RedirectResponse  # Added RedirectResponse import
from fastapi.staticfiles import StaticFiles
from keycloak import KeycloakOpenID
from pathlib import Path
from keycloak.exceptions import KeycloakAuthenticationError
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, Histogram
from jose import jwt
from jaeger_client import Config

# Конфигурация Jaeger
config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'logging': True,
    },
    service_name='micro',
    validate=True,
)
jaeger_tracer = config.initialize_tracer()

# Настройка базовой конфигурации логирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение к Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080",
    client_id="givemetoken",
    realm_name="helpmeplease",
    client_secret_key="lI04AeNwkChC90SXweq60uAGhrmiTmSx"
)

# Обработчик статических файлов
app.mount("/static", StaticFiles(directory=Path(__file__).parent.resolve() / "static"), name="static")

# Метрики Prometheus
request_counter = Counter("http_requests_total", "Total number of HTTP requests", ["method", "endpoint"])
authentication_counter = Counter("authentication_attempts", "Total number of authentication attempts", ["outcome"])
error_counter = Counter("authentication_errors_total", "Total number of authentication errors")
request_duration_histogram = Histogram("http_request_duration_seconds", "Duration of HTTP requests",
                                       ["method", "endpoint"])


# Обработчик для страницы входа
@app.get("/keycloak_login", response_class=HTMLResponse)
async def get_login():
    return FileResponse("static/keycloakauth.html", media_type="text/html")


@app.post("/keycloak_login")
async def post_login(username: str = Form(...), password: str = Form(...)):
    try:
        token = keycloak_openid.token(username=username, password=password)
        print(token)
        if "access_token" not in token:
            raise HTTPException(status_code=401, detail="Токен не был получен после аутентификации")

        authentication_counter.labels(outcome="success").inc()  # Успешная аутентификация

        response = RedirectResponse(url="/main", status_code=302)
        response.set_cookie(key="access_token", value=token['access_token'], httponly=True)
        return response
    except KeycloakAuthenticationError as e:
        logging.error("Ошибка при аутентификации: %s", str(e))
        authentication_counter.labels(outcome="failure").inc()  # Неуспешная аутентификация
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")


@app.get("/main", response_class=HTMLResponse)
async def get_main(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Пользователь не авторизован")

    # Создание нового спана для трассировки
    span = jaeger_tracer.start_span("get_main")

    # Создание гистограммы для измерения времени выполнения запроса
    with request_duration_histogram.labels(method="GET", endpoint="/main").time():
        try:
            public_key = keycloak_openid.public_key()
            key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            decoded_token = jwt.decode(token, key, algorithms=["RS256"], audience="account")
            roles = decoded_token.get("realm_access", {}).get("roles", [])
        except Exception as e:
            logging.error("Ошибка при декодировании токена: %s", str(e))
            # Устанавливаем тег ошибки для спана
            span.set_tag("error", True)
            raise HTTPException(status_code=401, detail="Неверный токен")
        finally:
            # Завершаем спан
            span.finish()

    roles_html = "".join(f"<li>{role}</li>" for role in roles)
    admin_role_notice = "Системой замечено, что у вас есть роль 'admin'." if "admin" in roles else ""

    return HTMLResponse(f"""
        <html>
        <body>
            <h1>Роли пользователя</h1>
            <ul>{roles_html}</ul>
            <p>{admin_role_notice}</p>
        </body>
        </html>
    """)


# Обработчик для метрик Prometheus
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)