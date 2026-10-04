from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.conversations import router as conversations_router
from routers.documents import router as documents_router
from routers.health import router as health_router
from routers.query import router as query_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(conversations_router)
