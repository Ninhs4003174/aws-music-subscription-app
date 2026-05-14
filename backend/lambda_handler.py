from app.main import app
from mangum import Mangum

# Lambda handler - this converts the FastAPI ASGI app to work with API Gateway
handler = Mangum(app, lifespan="off")
