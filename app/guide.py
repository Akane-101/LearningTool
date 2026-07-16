"""按学生书写习惯生成逐步引导：∵ → ∴关系 → ∴等式 → ∵数值 → ∴结果。"""

from __future__ import annotations

import re
import uuid
from typing import Optional

from .models import (
    GuideSession,
    GuideStep,
    HintLevel,
    ParsedProblem,
    StepKind,
    SubmitAnswerResponse,
)
from .parser import parse_problem_text

# 内存会话（原型足够；后续可换 Redis / 数据库）
SESSIONS: dict[str, GuideSession] = {}


def _known_text(problem: ParsedProblem) -> str:
    if not problem.known_angles:
        return "（请写出题目给出的已知条件）"
    return "，".join(f"∠{a.name}={a.value:g}°" for a in problem.known_angles)


def _target_name(problem: ParsedProblem) -> str:
    if problem.find_targets:
        return problem.find_targets[0]
    if problem.unknown_angles:
        return problem.unknown_angles[0]
    return "x"


def _reason_text(problem: ParsedProblem) -> str:
    if problem.suggested_reasons:
        return problem.suggested_reasons[0]
    return "三角形内角和等于 180°"


def _relation_sample(problem: ParsedProblem) -> str:
    reason = _reason_text(problem)
    keywords = "、".join(problem.keywords) if problem.keywords else "三角形内角和"
    return f"由{keywords}可知：{reason}"


def _equation_sample(problem: ParsedProblem) -> str:
    target = _target_name(problem)
    known = problem.known_angles
    # 默认按内角和模板
    if len(known) >= 2:
        a, b = known[0], known[1]
        return f"∠{a.name}+∠{b.name}+∠{target}=180°"
    if len(known) == 1:
        a = known[0]
        return f"∠{a.name}+∠{target}=180°（若还有一角，请一并写出）"
    return f"……+∠{target}=180°"


def _known_value_sample(problem: ParsedProblem) -> str:
    return _known_text(problem)


def _result_sample(problem: ParsedProblem) -> str:
    target = _target_name(problem)
    known = problem.known_angles
    if len(known) >= 2 and "内角和" in "".join(problem.keywords):
        total = sum(a.value or 0 for a in known[:2])
        ans = 180 - total
        return f"∠{target}=180°-∠{known[0].name}-∠{known[1].name}=180°-{known[0].value:g}°-{known[1].value:g}°={ans:g}°"
    if len(known) >= 2:
        total = sum(a.value or 0 for a in known[:2])
        ans = 180 - total
        return f"∠{target}={ans:g}°"
    return f"∠{target}=……°"


def build_steps(problem: ParsedProblem) -> list[GuideStep]:
    target = _target_name(problem)
    reason = _reason_text(problem)

    return [
        GuideStep(
            index=0,
            kind=StepKind.GIVEN,
            prompt="第 1 步（∵ 已知条件）：先把题目里已经给出的条件写清楚。",
            placeholder="例：∠A=50°，∠B=60°",
            expected_keywords=[a.name for a in problem.known_angles]
            + [str(int(a.value)) for a in problem.known_angles if a.value is not None],
            sample_answer=_known_text(problem),
            tip="把带数字的角都写出来，这是后面每一步的出发点。",
        ),
        GuideStep(
            index=1,
            kind=StepKind.RELATION,
            prompt="第 2 步（∴ 几何关系）：根据图形，说明用到了什么性质，并写出依据。",
            placeholder=f"例：∴ ∠A=∠C（依据：{reason}）",
            expected_keywords=problem.keywords[:3] or ["内角和", "180"],
            sample_answer=_relation_sample(problem),
            tip="常见依据：三角形内角和、平行线同位角/内错角、角平分线、等腰底角相等、对顶角相等。",
        ),
        GuideStep(
            index=2,
            kind=StepKind.EQUATION,
            prompt="第 3 步（∴ 角度计算等式）：把关系写成含未知角的等式。",
            placeholder=f"例：∴ ∠A+∠B+∠{target}=180°",
            expected_keywords=["=", "180"] if "内角和" in "".join(problem.keywords) else ["="],
            sample_answer=_equation_sample(problem),
            tip="先列式，不要急着代入数字。",
        ),
        GuideStep(
            index=3,
            kind=StepKind.KNOWN_VALUE,
            prompt="第 4 步（∵ 已知数值）：把已知角度的具体数值写出来，准备代入。",
            placeholder="例：∵ ∠A=50°，∠B=60°",
            expected_keywords=[str(int(a.value)) for a in problem.known_angles if a.value is not None],
            sample_answer=f"∵ {_known_value_sample(problem)}",
            tip="这一步对应你笔记里的「∵ 已知的数值」。",
        ),
        GuideStep(
            index=4,
            kind=StepKind.RESULT,
            prompt=f"第 5 步（∴ 求出角度）：代入计算，写出中间过程并得到 ∠{target}。",
            placeholder=f"例：∴ ∠{target}=180°-50°-60°=70°",
            expected_keywords=[target],
            sample_answer=_result_sample(problem),
            tip="最终答案要带单位「°」，并写清计算过程。",
        ),
    ]


def start_session(text: str) -> GuideSession:
    problem = parse_problem_text(text)
    steps = build_steps(problem)
    session = GuideSession(
        session_id=str(uuid.uuid4()),
        problem=problem,
        steps=steps,
        current_index=0,
        answers=[],
        completed=False,
    )
    SESSIONS[session.session_id] = session
    return session


def get_session(session_id: str) -> Optional[GuideSession]:
    return SESSIONS.get(session_id)


def _normalize_answer(s: str) -> str:
    return re.sub(r"\s+", "", s.lower().replace("∠", "").replace("角", ""))


def _check_answer(step: GuideStep, answer: str) -> tuple[bool, str]:
    text = answer.strip()
    if not text:
        return False, "还没有填写内容哦，先试着写一小句。"

    norm = _normalize_answer(text)
    if not step.expected_keywords:
        return True, "写得不错，可以进入下一步。"

    hits = 0
    for kw in step.expected_keywords:
        if _normalize_answer(str(kw)) in norm:
            hits += 1

    # 至少命中一半关键词，或答案较长且含关键符号
    need = max(1, (len(step.expected_keywords) + 1) // 2)
    if hits >= need:
        return True, "很好！这一步的关键信息已经写出来了。"
    if len(text) >= 6 and any(ch in text for ch in "∵∴=＋+-°度"):
        return True, "思路方向对，继续保持这种书写格式。"
    return False, "再看看：是否写出了关键角名、依据或等式？可以点「提示」看看。"


def _hint_for(step: GuideStep, level: HintLevel) -> Optional[str]:
    if level == HintLevel.NONE:
        return None
    if level == HintLevel.LIGHT:
        return step.tip or "想想这一步是「已知」还是「推出」。"
    return f"参考写法：{step.sample_answer}"


def _compose_writeup(session: GuideSession) -> str:
    lines: list[str] = []
    labels = {
        StepKind.GIVEN: "∵",
        StepKind.RELATION: "∴",
        StepKind.EQUATION: "∴",
        StepKind.KNOWN_VALUE: "∵",
        StepKind.RESULT: "∴",
    }
    for step, ans in zip(session.steps, session.answers):
        body = ans.strip()
        # 若学生没写符号，自动补上
        prefix = labels[step.kind]
        if not body.startswith("∵") and not body.startswith("∴"):
            body = f"{prefix} {body}"
        lines.append(body)
    return "\n".join(lines)


def submit_answer(
    session_id: str,
    answer: str,
    hint_level: HintLevel = HintLevel.NONE,
) -> SubmitAnswerResponse:
    session = get_session(session_id)
    if session is None:
        return SubmitAnswerResponse(
            ok=False,
            feedback="会话不存在或已过期，请重新粘贴题目开始。",
            current_index=0,
            total_steps=0,
            completed=False,
        )

    if session.completed:
        return SubmitAnswerResponse(
            ok=True,
            feedback="本题已经完成啦。可以复制下方完整书写，或换一题继续练。",
            current_index=session.current_index,
            total_steps=len(session.steps),
            completed=True,
            final_writeup=session.final_writeup,
            session=session,
        )

    step = session.steps[session.current_index]
    hint = _hint_for(step, hint_level)

    # 仅要提示、不提交空答案时：返回提示
    if hint_level != HintLevel.NONE and not answer.strip():
        return SubmitAnswerResponse(
            ok=False,
            feedback="先看提示，再自己写一版。",
            hint=hint,
            current_index=session.current_index,
            total_steps=len(session.steps),
            completed=False,
            session=session,
        )

    ok, feedback = _check_answer(step, answer)
    if not ok:
        return SubmitAnswerResponse(
            ok=False,
            feedback=feedback,
            hint=hint,
            current_index=session.current_index,
            total_steps=len(session.steps),
            completed=False,
            session=session,
        )

    # 通过本步
    if len(session.answers) == session.current_index:
        session.answers.append(answer.strip())
    else:
        session.answers[session.current_index] = answer.strip()

    session.current_index += 1
    if session.current_index >= len(session.steps):
        session.completed = True
        session.final_writeup = _compose_writeup(session)
        return SubmitAnswerResponse(
            ok=True,
            feedback="全部步骤完成！下面是按你习惯整理的完整书写。",
            current_index=session.current_index,
            total_steps=len(session.steps),
            completed=True,
            final_writeup=session.final_writeup,
            session=session,
        )

    next_step = session.steps[session.current_index]
    return SubmitAnswerResponse(
        ok=True,
        feedback=feedback,
        next_prompt=next_step.prompt,
        current_index=session.current_index,
        total_steps=len(session.steps),
        completed=False,
        session=session,
    )


SAMPLE_PROBLEMS = [
    {
        "id": "p1",
        "title": "2023·三角形内角和",
        "text": "在△ABC中，∠A=50°，∠B=60°，求∠C的度数。",
        "tags": ["内角和"],
    },
    {
        "id": "p2",
        "title": "2022·平行线求角度",
        "text": "如图，在△ABC中，D、E分别是AB、AC上的点，DE∥BC，∠ADE=70°，∠A=40°，求∠C的度数。",
        "tags": ["平行线", "内角和"],
    },
    {
        "id": "p3",
        "title": "2021·角平分线",
        "text": "在△ABC中，∠A=80°，∠B=60°，AD是∠BAC的角平分线，交BC于点D，求∠ADC的度数。",
        "tags": ["角平分线", "外角"],
    },
    {
        "id": "p4",
        "title": "2022·等腰三角形求角",
        "text": "在等腰△ABC中，AB=AC，∠A=40°，D是BC边上的中点，连接AD，求∠BAD的度数。",
        "tags": ["等腰", "三线合一"],
    },
    {
        "id": "p5",
        "title": "2023·平行线+角平分线综合",
        "text": "如图，AB∥CD，EF平分∠AEC，∠A=50°，∠C=30°，求∠AEF的度数。",
        "tags": ["平行线", "角平分线"],
    },
    {
        "id": "p6",
        "title": "2024·直角三角形+互余",
        "text": "在Rt△ABC中，∠C=90°，∠A=2∠B，求∠A和∠B的度数。",
        "tags": ["直角三角形", "互余"],
    },
    {
        "id": "p7",
        "title": "2023·三角形外角性质",
        "text": "如图，在△ABC中，∠A=30°，∠B=50°，延长BC至点D，求∠ACD的度数。",
        "tags": ["外角"],
    },
    {
        "id": "p8",
        "title": "2024·等边三角形+平行线",
        "text": "在等边△ABC中，D是AC边上一点，过D作DE∥AB交BC于E，若∠EDC=20°，求∠BDE的度数。",
        "tags": ["等边三角形", "平行线"],
    },
]
