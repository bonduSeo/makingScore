from __future__ import annotations

import secrets
from pathlib import Path

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.llm import LLMAdvisor
from app.services.pipeline import PipelineRunner

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

runner = PipelineRunner(output_root=Path(settings.output_dir))
advisor = LLMAdvisor(api_key=settings.openai_api_key)

oauth = OAuth()
if settings.oauth_enabled and settings.oauth_client_id and settings.oauth_client_secret:
    oauth.register(
        name="openai",
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        authorize_url=settings.oauth_authorize_url,
        access_token_url=settings.oauth_token_url,
        client_kwargs={"scope": "openid profile email"},
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "advice": None})


@app.post("/transcribe", response_class=HTMLResponse)
async def transcribe(
    request: Request,
    audio_file: UploadFile = File(...),
    approach: str = Form("B"),
    include_score: bool = Form(False),
):
    suffix = Path(audio_file.filename).suffix or ".mp3"
    temp_name = f"upload_{secrets.token_hex(4)}{suffix}"
    upload_path = Path(settings.output_dir) / temp_name
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(await audio_file.read())

    result = runner.run(upload_path, approach=approach, include_score=include_score)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "advice": None,
        },
    )


@app.post("/advice", response_class=HTMLResponse)
async def advice(request: Request, question: str = Form(...)):
    suggested = advisor.suggest(question)
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "advice": suggested})


@app.get("/auth/login")
async def login(request: Request):
    if "openai" not in oauth._clients:
        return RedirectResponse(url="/?oauth=disabled")
    return await oauth.openai.authorize_redirect(request, settings.oauth_redirect_uri)


@app.get("/auth/callback")
async def callback(request: Request):
    if "openai" not in oauth._clients:
        return RedirectResponse(url="/?oauth=disabled")
    token = await oauth.openai.authorize_access_token(request)
    return {"status": "ok", "token": token}
