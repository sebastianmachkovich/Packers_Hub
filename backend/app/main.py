from fastapi import FastAPI
from app.routes.packers import router as packers_router

app = FastAPI(title="PackersHub Backend")

# Routes
app.include_router(packers_router, prefix="/packers", tags=["Packers"])

@app.get("/")
def root():
  return {"status": "Backend running"}
