import os

os.environ["GROQ_API_KEY"] = "fake-key-for-testing"

from unittest.mock import patch
from llm_service import validate_notes, llm_client, chunk_transcript

VALID_RESPONSE = '{"summary": "Test meeting", "action_items": [{"text": "Do something", "owner": "Ivan", "due_date": null}], "decisions": ["Decision 1"], "key_takeaways": ["Takeaway 1"], "topics": ["Topic 1"], "next_steps": [{"text": "Next step", "owner": "Ivan"}]}'


# Test 1 - valid JSON from LLM
def test_valid_notes():
    with patch("llm_service._call_llm", return_value=VALID_RESPONSE):
        result = llm_client("Some transcript text")
        notes = validate_notes(result)
        assert notes["summary"] == "Test meeting"
        assert len(notes["action_items"]) == 1
        assert notes["action_items"][0]["owner"] == "Ivan"


# Test 2 - LLM returns invalid JSON
def test_invalid_json_with_markdown():
    fake_response = '```json\n{"summary": "Test", "action_items": [], "decisions": [], "key_takeaways": [], "topics": [], "next_steps": []}\n```'
    notes = validate_notes(fake_response)
    assert notes["summary"] == "Test"


# Test 3 - missing fields are filled with defaults
def test_missing_fields():
    fake_response = '{"summary": "Test meeting"}'
    notes = validate_notes(fake_response)
    assert notes["action_items"] == []
    assert notes["decisions"] == []
    assert notes["key_takeaways"] == []
    assert notes["topics"] == []
    assert notes["next_steps"] == []


# Test 4 - transcript too long is split into chunks
def test_chunk_transcript():
    long_transcript = "a" * 50000
    chunks = chunk_transcript(long_transcript)
    assert len(chunks) == 3
    assert len(chunks[0]) == 20000
    assert len(chunks[1]) == 20000
    assert len(chunks[2]) == 10000


# Test 5 - missing owner and due_date are set to null
def test_missing_owner_and_due_date():
    fake_response = '{"summary": "Test", "action_items": [{"text": "Do something"}], "decisions": [], "key_takeaways": [], "topics": [], "next_steps": []}'
    notes = validate_notes(fake_response)
    assert notes["action_items"][0].get("owner") is None
    assert notes["action_items"][0].get("due_date") is None


# Test 6 - empty action items
def test_empty_action_items():
    fake_response = '{"summary": "Test", "action_items": [], "decisions": [], "key_takeaways": [], "topics": [], "next_steps": []}'
    notes = validate_notes(fake_response)
    assert notes["action_items"] == []


# Test 7 - short transcript
def test_short_transcript():
    with patch("llm_service._call_llm", return_value=VALID_RESPONSE):
        result = llm_client("Hi.")
        assert result is not None
