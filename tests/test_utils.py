from convfinqa.utils import stringify


def test_stringify_list() -> None:
    assert stringify(["a", "b"]) == "a\nb"


def test_stringify_str() -> None:
    assert stringify("hello") == "hello"
