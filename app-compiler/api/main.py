from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import compile, health, runs

app = FastAPI(title="AppCompiler", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(compile.router)
app.include_router(health.router)
app.include_router(runs.router)
