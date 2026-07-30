from fastapi import FastAPI

from src.routers.routers import router as hello_router  # Import the router

app = FastAPI()

app.include_router(hello_router)
