from src import knowledge_base


def test_answer_question_returns_matching_faq_answer(monkeypatch):
    monkeypatch.setattr(knowledge_base, "_call_ollama", lambda prompt: '"Where are the nearest restrooms?"')

    result = knowledge_base.answer_question("Where can I find the bathroom?")

    assert result == knowledge_base.FAQ["Where are the nearest restrooms?"]


def test_answer_question_falls_back_case_insensitive(monkeypatch):
    monkeypatch.setattr(knowledge_base, "_call_ollama", lambda prompt: "  'where can i find food stalls?'  ")

    result = knowledge_base.answer_question("Where can I get something to eat?")

    assert result == knowledge_base.FAQ["Where can I find food stalls?"]
