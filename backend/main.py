"""AI StudyMate backend entry point.  Run: uvicorn main:app --reload"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.study import router as study_router
from utils import config
from utils.errors import LLMError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)  # keep request URLs out of logs
logger = logging.getLogger("studymate")

app = FastAPI(title="AI StudyMate API")
app.add_middleware(CORSMiddleware, allow_origins=config.get_allowed_origins(),
                   allow_methods=["POST", "GET"], allow_headers=["Content-Type"])
app.include_router(study_router)


def _error(status: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"success": False, "error": message})


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """422 with one friendly message instead of Pydantic's raw error list."""
    err = exc.errors()[0]
    if err["type"] == "missing":
        message = "Please fill in the required fields."
    elif err["type"] == "value_error":
        message = str(err["msg"]).removeprefix("Value error, ")
    else:
        message = "One of the selected options is invalid."
    return _error(422, message)


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    logger.error("LLM error (%s): %s", exc.status_code, exc.log_detail)  # technical detail stays in the log
    return _error(exc.status_code, exc.user_message)


@app.exception_handler(Exception)
async def unexpected_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error")
    return _error(500, "Something went wrong on our side. Please try again.")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
