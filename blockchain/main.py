from fastapi import FastAPI
from api import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Blockchain App")
# Настроим CORS для разрешения OPTIONS и других методов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем только фронтенд с этого домена
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Разрешаем методы GET, POST, OPTIONS
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(router)