"""图片 OCR：把题目照片/截图转成文字。"""

from __future__ import annotations

import io
from functools import lru_cache
from typing import Optional

from PIL import Image

from .models import OcrResult


@lru_cache(maxsize=1)
def _rapid_engine():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


@lru_cache(maxsize=1)
def _dddd_pair():
    import ddddocr

    det = ddddocr.DdddOcr(det=True, ocr=False, show_ad=False)
    ocr = ddddocr.DdddOcr(det=False, ocr=True, show_ad=False)
    return det, ocr


def _prepare_image(data: bytes) -> tuple[Image.Image, bytes]:
    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    max_side = 1600
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return img, buf.getvalue()


def _join_lines(lines: list[str]) -> str:
    cleaned = []
    for line in lines:
        t = line.strip()
        if not t:
            continue
        if len(t) == 1 and t not in "△∠°αβγABCabc":
            continue
        cleaned.append(t)
    return "\n".join(cleaned)


def _ocr_rapid(png_bytes: bytes, img: Image.Image) -> Optional[OcrResult]:
    try:
        import numpy as np

        engine = _rapid_engine()
        result, _ = engine(np.array(img))
    except ImportError:
        return None
    except Exception as exc:
        return OcrResult(ok=False, text="", message=f"RapidOCR 识别失败：{exc}")

    lines: list[str] = []
    scores: list[float] = []
    if result:
        for item in result:
            if len(item) >= 3:
                lines.append(str(item[1]))
                try:
                    scores.append(float(item[2]))
                except (TypeError, ValueError):
                    pass

    text = _join_lines(lines)
    conf = sum(scores) / len(scores) if scores else 0.0
    if not text:
        return OcrResult(ok=False, text="", message="没有识别到文字", lines=[], confidence=0.0)
    return OcrResult(
        ok=True,
        text=text,
        message="识别完成，请检查并改正错字后再开始引导。",
        lines=lines,
        confidence=round(conf, 3),
        engine="rapidocr",
    )


def _ocr_dddd(png_bytes: bytes, img: Image.Image) -> Optional[OcrResult]:
    try:
        det, ocr = _dddd_pair()
    except ImportError:
        return None

    try:
        boxes = det.detection(png_bytes) or []
        lines: list[str] = []
        # 按从上到下、从左到右排序
        boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
        for box in boxes:
            x1, y1, x2, y2 = box
            crop = img.crop((x1, y1, x2, y2))
            buf = io.BytesIO()
            crop.save(buf, format="PNG")
            part = ocr.classification(buf.getvalue())
            if part and str(part).strip():
                lines.append(str(part).strip())

        # 检测不到框时，整图再试一次
        if not lines:
            whole = ocr.classification(png_bytes)
            if whole and str(whole).strip():
                lines = [str(whole).strip()]
    except Exception as exc:
        return OcrResult(ok=False, text="", message=f"OCR 识别失败：{exc}")

    text = _join_lines(lines)
    if not text:
        return OcrResult(
            ok=False,
            text="",
            message="没有识别到文字。请拍清楚题目，或手动输入。",
            lines=[],
            confidence=0.0,
            engine="ddddocr",
        )
    return OcrResult(
        ok=True,
        text=text,
        message="识别完成，请检查并改正错字后再开始引导。",
        lines=lines,
        confidence=0.7,
        engine="ddddocr",
    )


def ocr_image_bytes(data: bytes, filename: Optional[str] = None) -> OcrResult:
    if not data:
        return OcrResult(ok=False, text="", message="没有收到图片数据")

    try:
        img, png_bytes = _prepare_image(data)
    except Exception:
        return OcrResult(ok=False, text="", message="无法读取图片，请换一张清晰的 jpg/png")

    # 优先 RapidOCR（更适合整段题目），否则用 ddddocr
    result = _ocr_rapid(png_bytes, img)
    if result is None:
        result = _ocr_dddd(png_bytes, img)
    if result is None:
        return OcrResult(
            ok=False,
            text="",
            message="未安装 OCR 库。请执行：pip install pillow ddddocr",
        )

    result.filename = filename
    return result
