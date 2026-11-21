"""Main FastAPI application entry point for Gold Trust AI."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routers import exchanges, verify
from app.domain.exceptions import DomainError

app = FastAPI(
    title="Gold Trust AI API",
    description="Trust architecture for gold jewellery exchanges",
    version="0.1.0",
)

# Cross-Origin Resource Sharing (PWA counter & customer devices)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RFC 9457 Problem Details Exception Handler for Domain Errors
@app.exception_handler(DomainError)
def domain_exception_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        media_type="application/problem+json",
        content={
            "type": f"https://goldtrust.ai/errors/{exc.code.lower()}",
            "title": "Domain Rule Violation",
            "status": 422,
            "detail": exc.message,
            "code": exc.code,
        },
    )

# Standard Health and Readiness Probes
@app.get("/healthz", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "gold-trust-ai"}

@app.get("/readyz", tags=["health"])
def readiness_check() -> dict[str, str]:
    return {"status": "ready"}

# Include Routers
app.include_router(exchanges.router)
app.include_router(verify.router)
