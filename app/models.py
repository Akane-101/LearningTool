from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class StepKind(str, Enum):
    GIVEN = "given"  # ∵ 已知条件
    RELATION = "relation"  # ∴ 几何关系描述
    EQUATION = "equation"  # ∴ 角度计算等式
    KNOWN_VALUE = "known_value"  # ∵ 已知数值
    RESULT = "result"  # ∴ 求出角度


class HintLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"
    FULL = "full"


class ParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="粘贴的题目文本")


class AngleFact(BaseModel):
    name: str
    value: Optional[float] = None
    unit: str = "°"


class ParsedProblem(BaseModel):
    raw_text: str
    summary: str
    known_angles: list[AngleFact] = []
    unknown_angles: list[str] = []
    find_targets: list[str] = []
    keywords: list[str] = []
    clues: list[str] = []
    suggested_reasons: list[str] = []
    confidence: float = 0.0


class StartGuideRequest(BaseModel):
    text: str = Field(..., min_length=1)
    problem_id: Optional[str] = None


class GuideStep(BaseModel):
    index: int
    kind: StepKind
    prompt: str
    placeholder: str
    expected_keywords: list[str] = []
    sample_answer: str = ""
    tip: str = ""


class GuideSession(BaseModel):
    session_id: str
    problem: ParsedProblem
    steps: list[GuideStep]
    current_index: int = 0
    answers: list[str] = []
    completed: bool = False
    final_writeup: str = ""


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str = ""
    hint_level: HintLevel = HintLevel.NONE


class SubmitAnswerResponse(BaseModel):
    ok: bool
    feedback: str
    hint: Optional[str] = None
    next_prompt: Optional[str] = None
    current_index: int
    total_steps: int
    completed: bool
    final_writeup: Optional[str] = None
    session: Optional[GuideSession] = None


class SampleProblem(BaseModel):
    id: str
    title: str
    text: str
    tags: list[str] = []


class ApiMessage(BaseModel):
    message: str
    data: Any = None


class OcrResult(BaseModel):
    ok: bool
    text: str = ""
    message: str = ""
    lines: list[str] = []
    confidence: float = 0.0
    filename: Optional[str] = None
    engine: Optional[str] = None


class AiStartRequest(BaseModel):
    text: str = Field(..., min_length=1, description="题目文字")
    lang: str = Field("zh", description="语言：zh 或 en")
    image_base64: Optional[str] = Field(None, description="图片 base64（不含 data: 前缀）")
    image_mime: Optional[str] = Field(None, description="图片 MIME 类型，如 image/jpeg")


class AiReplyRequest(BaseModel):
    session_id: str
    answer: str = ""
    want_hint: bool = False
