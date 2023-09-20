from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import augments

app = FastAPI()

stats_router = APIRouter(prefix="/stats", tags=["stats"])
stats_router.include_router(augments.router)
app.include_router(stats_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}
