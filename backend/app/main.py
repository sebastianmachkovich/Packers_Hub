from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.packers import router as packers_router
from app.services.db_service import *

app = FastAPI(title="PackersHub Backend")

# CORS Configuration
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],  # Vite dev server
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Database lifecycle
@app.on_event("startup")
async def startup_db():
  await connect_db()

@app.on_event("shutdown")
async def shutdown_db():
  await close_db()

# Routes
app.include_router(packers_router, prefix="/packers", tags=["Packers"])

@app.get("/")
def root():
  return {"status": "Backend running"}
