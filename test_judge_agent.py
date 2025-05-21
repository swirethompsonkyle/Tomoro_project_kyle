from tests.conftest import judge_stub

def test_judge_returns_correct(judge_stub):
    verdict, prompt = judge_stub.judge(
        context="",
        question="?",
        expected="42",
        ai_answer="42",
        qa_data=None,
    )
    assert verdict.startswith("Correct")
    assert "# Question:" in prompt

