from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, songs, subscription
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:8080",
		"http://127.0.0.1:8080",
		"http://localhost:5500",
		"http://127.0.0.1:5500",
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(subscription.router)