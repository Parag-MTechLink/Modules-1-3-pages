from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routes import router
import os

app = FastAPI(title="Internal EUT Management System")

# Resolve base directory safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount frontend as static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "frontend")),
    name="static",
)

# Register routes
app.include_router(router)
