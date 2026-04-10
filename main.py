from fastapi import FastAPI, Request

from api.v1.payments import router as payments_router


app = FastAPI(
    title="Async Payments Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(payments_router, prefix="/api/v1")


@app.get("/health", tags=["service"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/test-webhook", tags=["test"])
async def test_webhook(request: Request) -> dict:
    payload = await request.json()
    print("TEST WEBHOOK RECEIVED:", payload)
    return {"received": True}