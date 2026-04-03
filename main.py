from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import models
from database import engine
from routers import auth, records, dashboard, users

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Data Processing and Access Control Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Only block 500 unhandled exceptions, do not intercept HTTPException!
    from fastapi import HTTPException
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

import os
from fastapi.staticfiles import StaticFiles

if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"message": "Welcome to Finance Dashboard API"}
