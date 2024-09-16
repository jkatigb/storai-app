import os
from fastapi import FastAPI
from dotenv import load_dotenv
from .routers import story, image
from .celery_app import celery_app

load_dotenv()  # This loads the environment variables from a .env file

app = FastAPI()

app.include_router(story.router)
app.include_router(image.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Children's Storybook API"}

# Add Celery app to FastAPI app
app.celery_app = celery_app