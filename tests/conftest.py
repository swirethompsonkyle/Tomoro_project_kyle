from typing import Dict, Any

import pytest
from convfinqa.agents.judge_agent import JudgeAgent
from convfinqa.agents.solver_agent import SolverAgent


class DummyLLM:
    """A minimal drop-in replacement for ChatOpenAI used in tests."""
    def __init__(self, reply: str) -> None:
        self._reply = reply

    def invoke(self, _messages):            # type: ignore[override]
        from langchain_core.messages import AIMessage
        return AIMessage(content=self._reply)



@pytest.fixture()
def solver_stub(monkeypatch):
    monkeypatch.setattr(SolverAgent, "__init__", lambda self, *a, **k: None)
    agent = SolverAgent.__new__(SolverAgent)
    agent._llm = DummyLLM("42")                   # type: ignore[attr-defined]
    return agent


@pytest.fixture()
def judge_stub(monkeypatch):
    monkeypatch.setattr(JudgeAgent, "__init__", lambda self, *a, **k: None)
    agent = JudgeAgent.__new__(JudgeAgent)
    agent._llm = DummyLLM("Correct")              # type: ignore[attr-defined]
    return agent


@pytest.fixture()
def dummy_entry() -> Dict[str, Any]:
    return {
        "id": "abc123",
        "pre_text": "Company revenue rose sharply.",
        "post_text": "",
        "table": {"Year": ["2023"], "Revenue": ["100"]},
        "qa": {"question": "What was the revenue in 2023?", "exe_ans": "100"},
    }
