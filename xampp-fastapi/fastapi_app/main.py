from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def frontend():
    return """
    <html>
        <head><title>FastAPI Frontend</title></head>
        <body>
            <h1>Hello from FastAPI Frontend</h1>
        </body>
    </html>
    """

@app.get("/api/hello")
async def api_hello():
    return {"message": "Hello from FastAPI API"}