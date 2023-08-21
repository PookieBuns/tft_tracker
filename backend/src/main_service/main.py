from fastapi import APIRouter, FastAPI

from .routers import augments

app = FastAPI()

stats_router = APIRouter(prefix="/stats", tags=["stats"])
stats_router.include_router(augments.router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
