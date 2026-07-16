from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .models import AiReplyRequest, AiStartRequest, SampleProblem
from .guide import SAMPLE_PROBLEMS
from .ocr import ocr_image_bytes
from .config import (
    api_key_configured,
    vision_configured,
    vision_provider,
    DEEPSEEK_MODEL,
    DASHSCOPE_VL_MODEL,
)
from .vision import analyze_geometry_image
from .ai_guide import get_session, reply_session, start_session as ai_start_session

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="解三角形 AI 引导",
    description="DeepSeek 逐步引导初中生解三角形角度题",
    version="0.3.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html = templates.get_template("index.html").render(
        request=request,
        samples=SAMPLE_PROBLEMS,
    )
    return HTMLResponse(content=html)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "ai_configured": api_key_configured(),
        "model": DEEPSEEK_MODEL,
        "vision_configured": vision_configured(),
        "vision_provider": vision_provider(),
        "vision_model": DASHSCOPE_VL_MODEL,
    }


@app.get("/api/samples", response_model=list[SampleProblem])
async def list_samples():
    return [SampleProblem(**p) for p in SAMPLE_PROBLEMS]


@app.post("/api/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    """上传题目图片：OCR 文字 + 百炼看图（几何结构）。"""
    data = await file.read()
    if len(data) > 12 * 1024 * 1024:
        return {
            "ok": False,
            "text": "",
            "message": "图片太大了（超过 12MB），请压缩后再试。",
        }

    try:
        ocr_raw = ocr_image_bytes(data, filename=file.filename)
        ocr = ocr_raw.model_dump() if hasattr(ocr_raw, "model_dump") else dict(ocr_raw)
    except Exception as exc:
        ocr = {
            "ok": False,
            "text": "",
            "message": f"文字识别失败：{exc}",
            "lines": [],
            "confidence": 0.0,
            "engine": None,
        }

    try:
        vision = analyze_geometry_image(data, mime=file.content_type)
    except Exception as exc:
        vision = {
            "ok": False,
            "message": f"看图失败：{exc}",
            "problem_text": "",
            "geometry_description": "",
            "figure": None,
        }

    text = (ocr.get("text") or "").strip()
    geom = (vision.get("geometry_description") or "").strip()
    v_text = (vision.get("problem_text") or "").strip()

    if vision.get("ok") and v_text:
        if not text or len(v_text) >= max(20, int(len(text) * 0.7)):
            text = v_text
        elif v_text not in text:
            text = f"{text}\n\n{v_text}"
    if vision.get("ok") and geom and geom not in text:
        text = f"{text}\n\n【图形】{geom}".strip()

    ok = bool(ocr.get("ok") or vision.get("ok"))
    if vision.get("ok"):
        message = "已识别文字，并看懂图中的几何图形"
    elif ocr.get("ok"):
        # 文字已出；看图失败用简短说明，不重复粘贴 API 原文
        vision_msg = (vision.get("message") or "").strip()
        if vision_msg:
            message = f"文字已识别。看图未成功：{vision_msg}"
        else:
            message = ocr.get("message") or "文字已识别"
    else:
        message = vision.get("message") or ocr.get("message") or "识别失败"

    return {
        "ok": ok,
        "text": text,
        "message": message,
        "lines": ocr.get("lines") or [],
        "confidence": ocr.get("confidence") or 0.0,
        "filename": file.filename,
        "engine": ocr.get("engine"),
        "geometry_description": geom,
        "figure": vision.get("figure"),
        "vision_ok": bool(vision.get("ok")),
        "vision_message": vision.get("message") or "",
    }


@app.post("/api/ai/start")
async def ai_start(body: AiStartRequest):
    """开始 AI 逐步引导。"""
    if not api_key_configured():
        return {
            "ok": False,
            "message": "未配置 DeepSeek API Key，请检查 .env 文件中的 DEEPSEEK_API_KEY。",
        }
    try:
        return ai_start_session(
            body.text,
            body.lang,
            body.image_base64,
            body.image_mime,
            body.geometry_description,
            body.figure_data,
        )
    except RuntimeError as exc:
        return {"ok": False, "message": str(exc)}
    except Exception as exc:
        return {"ok": False, "message": f"AI 调用失败：{exc}"}


@app.post("/api/ai/reply")
async def ai_reply(body: AiReplyRequest):
    """提交学生回答，或请求提示。"""
    if not api_key_configured():
        return {"ok": False, "message": "未配置 DeepSeek API Key。"}
    try:
        return reply_session(body.session_id, body.answer, body.want_hint)
    except RuntimeError as exc:
        return {"ok": False, "message": str(exc)}
    except Exception as exc:
        return {"ok": False, "message": f"AI 调用失败：{exc}"}


@app.get("/api/ai/{session_id}")
async def ai_status(session_id: str):
    session = get_session(session_id)
    if session is None:
        return {"ok": False, "message": "会话不存在"}
    return {
        "ok": True,
        "session_id": session_id,
        "problem_text": session.get("problem_text", ""),
        "completed": session.get("completed", False),
        "final_solution": session.get("final_solution", ""),
        "turns": session.get("turns", 0),
    }
