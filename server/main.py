import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from server.routes import router

app = FastAPI(title="Library Desk Agent")

app.include_router(router)

app.mount("/static", StaticFiles(directory="app"), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse("app/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)