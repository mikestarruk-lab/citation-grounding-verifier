import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .baseline import LexicalVerifier
from .domain import VerificationReport, VerifyError, VerifyRequest
from .llm import AnthropicProvider, LLMVerifier, execute

load_dotenv()
app = FastAPI(title="Citation Grounding & Faithfulness Verifier", version="0.1.0")


@app.exception_handler(VerifyError)
async def verifier_error(request: Request, error: VerifyError):
    return JSONResponse(
        status_code=error.status, content={"error": {"code": error.code, "message": str(error)}}
    )


@app.get("/healthz")
def health():
    return {"status": "ok", "default_method": os.getenv("VERIFIER_METHOD", "minimal")}


@app.post("/verify", response_model=VerificationReport)
async def verify(request: VerifyRequest):
    if not request.generated_answer.strip():
        return VerificationReport(claims=[])
    method = os.getenv("VERIFIER_METHOD", "minimal")
    if method == "lexical":
        return await execute(LexicalVerifier(), request, {})
    if method not in {"minimal", "optimized"}:
        raise VerifyError("configuration", "Unknown VERIFIER_METHOD", 503)
    provider = AnthropicProvider()
    try:
        return await execute(LLMVerifier(provider, optimized=method == "optimized"), request, {})
    finally:
        await provider.close()
