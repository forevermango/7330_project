from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routes  # Import routes from routes.py

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(routes.router)  # Include the router from routes.py

