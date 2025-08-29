"""Main FastAPI application."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.infrastructure.database import database
from src.presentation import router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await database.create_tables()
    yield
    # Shutdown
    await database.close()


app = FastAPI(
    title="NeuroVet - Veterinary Neurological Diagnostic Assistant",
    description="AI-powered diagnostic assistant for canine neurological disorders",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "NeuroVet - Veterinary Neurological Diagnostic Assistant",
        "version": "1.0.0",
        "status": "running"
    }


