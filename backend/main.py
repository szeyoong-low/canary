import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # load variables from .env into the process environment

app = FastAPI()

# Comma-separated list of origins allowed to call this API.
# Set ALLOWED_ORIGINS in the environment for each deployment target.
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5030").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"Hello": "World"}
