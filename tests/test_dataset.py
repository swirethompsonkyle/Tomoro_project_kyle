from convfinqa.dataset import FinQADataset


def test_build_context(dummy_entry):  # type: ignore[override]
    ctx = FinQADataset.build_context(dummy_entry)
    assert "# Start of Context #" in ctx
    assert "Company revenue rose sharply." in ctx
    assert '"Revenue": ["100"]' in ctx
