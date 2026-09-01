from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.routers.routers import router as hello_router  # Import the router



app = FastAPI()

app.include_router(hello_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

