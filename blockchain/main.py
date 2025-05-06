from fastapi import FastAPI
from api import router

app = FastAPI(title="Blockchain App")
app.include_router(router)