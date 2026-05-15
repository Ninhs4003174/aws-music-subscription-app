from fastapi import FastAPI, Request, Response
from app.routes import auth, songs, subscription
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

@app.middleware("http")
async def cors_middleware(request: Request, call_next):
	if request.method == "OPTIONS":
		return Response(status_code=200, headers={
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
			"Access-Control-Allow-Headers": "Content-Type,Authorization",
		})

	response = await call_next(request)
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
	return response

app.include_router(auth.router)
app.include_router(songs.router)
app.include_router(subscription.router)