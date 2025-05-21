from __future__ import annotations

from typing import List, Tuple

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from convfinqa.agents.prompts import AGENT_SYSTEM_PROMPT


class SolverAgent:
    """The primary reasoning agent that answers each question."""

    _SYS_PROMPT = AGENT_SYSTEM_PROMPT

    def __init__(self, model: str = "gpt-4o-mini", *, temperature: float = 0.1) -> None:
        self._llm = ChatOpenAI(model=model, temperature=temperature)


    def solve(self, context: str, question: str, history: str) -> str:
        messages: List[Tuple[str, str]] = [
            ("system", self._SYS_PROMPT),
            ("human", self._build_prompt(context, question, history)),
        ]
        ai_msg: AIMessage = self._llm.invoke(messages)  # type: ignore[arg-type]
        return ai_msg.content.strip()

    @staticmethod
    def _build_prompt(context: str, question: str, history: str) -> str:
        return (
            f"Based on the context and previous conversation answer "
            f"the following Question:\n{question}\n\n"
            f"# Previous Conversation so far:\n{history}\n\n"
            f"# Context:\n{context}"
        )
