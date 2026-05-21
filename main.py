from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pedals


app = FastAPI()
app.include_router(pedals.router)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"message": "API is healthy!"}
