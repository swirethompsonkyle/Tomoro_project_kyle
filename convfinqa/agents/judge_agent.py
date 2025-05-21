from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from convfinqa.agents.prompts import JUDGE_SYSTEM_PROMPT


class JudgeAgent:
    """Grades an answer and, when wrong, explains why (prefixed with 'Incorrect')."""

    _SYS_PROMPT = JUDGE_SYSTEM_PROMPT

    def __init__(self, model: str = "meta-llama/llama-3-70b-instruct", *, temperature: float = 0.1) -> None:
        self._llm = ChatOpenAI(model=model, temperature=temperature)


    def judge(
        self,
        *,
        context: str,
        question: str,
        expected: str,
        ai_answer: str,
        qa_data: Dict[str, Any] | None = None,
    ) -> Tuple[str, str]:
        """Return (verdict, prompt_sent_to_llm).  The verdict string is kept raw."""
        prompt = self._craft_prompt(context, question, expected, ai_answer, qa_data)
        messages = [("system", self._SYS_PROMPT), ("human", prompt)]
        raw: AIMessage = self._llm.invoke(messages)  # type: ignore[arg-type]
        return raw.content.strip(), prompt

    @staticmethod
    def _craft_prompt(
            context: str,
            question: str,
            expected: str,
            ai_answer: str,
            qa_data: Dict[str, Any] | None,
    ) -> str:
        qa_block = (
            "# QA metadata from dev row:\n"
            f"{json.dumps(qa_data, ensure_ascii=False, indent=2)}\n\n"
            if qa_data
            else ""
        )
        return (
            f"{qa_block}"
            f"# Text context:\n{context}\n\n"
            f"# Question:\n{question}\n\n"
            f"# Expected answer:\n{expected}\n\n"
            f"# AI answer:\n{ai_answer}\n\n"
            "Is the AI answer correct? Follow the instructions exactly."
        )
