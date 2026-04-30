from fastapi import FastAPI
from app.routes import auth, songs, subscription
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(subscription.router)