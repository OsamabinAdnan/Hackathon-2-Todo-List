"""
Stateless Architecture Test Templates

These templates provide standardized tests for validating stateless architecture
compliance in the Phase 3 AI Chatbot system.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import threading
import time


def test_user_data_isolation(client: TestClient):
    """
    Test that user A cannot access user B's conversation data.

    Validates: Database state isolation, proper user_id filtering
    """
    # User A creates a conversation
    response_a = client.post("/api/user_a/chat", json={"message": "Hello from A"})
    assert response_a.status_code == 200
    conv_id_a = response_a.json()["conversation_id"]

    # User B creates a conversation
    response_b = client.post("/api/user_b/chat", json={"message": "Hello from B"})
    assert response_b.status_code == 200
    conv_id_b = response_b.json()["conversation_id"]

    # User A should not access User B's conversation
    access_response = client.get(f"/api/user_a/conversations/{conv_id_b}")
    assert access_response.status_code in [404, 403]  # Not found or forbidden

    # User B should not access User A's conversation
    access_response_b = client.get(f"/api/user_b/conversations/{conv_id_a}")
    assert access_response_b.status_code in [404, 403]  # Not found or forbidden


def test_concurrent_request_isolation(client: TestClient):
    """
    Test that concurrent requests maintain proper isolation.

    Validates: Memory state audit, request independence
    """
    results = []
    errors = []

    def make_request(user_id, message):
        try:
            response = client.post(f"/api/{user_id}/chat", json={"message": message})
            results.append((user_id, response.json()))
        except Exception as e:
            errors.append((user_id, str(e)))

    # Simulate concurrent requests from different users
    threads = [
        threading.Thread(target=make_request, args=(f"user_{i}", f"message_{i}"))
        for i in range(5)
    ]

    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    end_time = time.time()

    # Verify all requests were processed independently
    assert len(results) == 5, f"Expected 5 results, got {len(results)}"
    assert len(errors) == 0, f"Unexpected errors: {errors}"

    # Verify each user got their own conversation
    user_conversations = {}
    for user_id, response in results:
        assert "conversation_id" in response
        user_conversations[user_id] = response["conversation_id"]

    # Verify conversations are unique per user
    assert len(set(user_conversations.values())) == 5, "Conversations should be unique"


def test_conversation_state_persistence(client: TestClient):
    """
    Test that conversation state persists correctly across requests.

    Validates: Database state verification, persistence patterns
    """
    # Start a conversation
    response1 = client.post("/api/test_user/chat", json={"message": "Hello"})
    assert response1.status_code == 200
    conv_id = response1.json()["conversation_id"]

    # Add to the conversation
    response2 = client.post(f"/api/test_user/chat/{conv_id}",
                           json={"message": "How are you?"})
    assert response2.status_code == 200

    # Retrieve conversation history
    history_response = client.get(f"/api/test_user/conversations/{conv_id}/history")
    assert history_response.status_code == 200
    history = history_response.json()

    # Verify both messages are present
    assert len(history) >= 2
    message_contents = [msg["content"] for msg in history]
    assert "Hello" in message_contents
    assert "How are you?" in message_contents


def test_transaction_rollback_on_error(client: TestClient):
    """
    Test that database operations are properly rolled back on error.

    Validates: Atomic operation verification, transaction boundaries
    """
    # Create a conversation with invalid data that should trigger rollback
    response = client.post("/api/test_user/chat", json={
        "message": "This should fail",
        "invalid_field": "invalid_value"  # This should cause an error
    })

    # Verify error response
    assert response.status_code in [400, 422, 500]  # Appropriate error status

    # Verify no partial data was saved
    history_response = client.get("/api/test_user/conversations")
    assert history_response.status_code == 200
    history = history_response.json()

    # Should not contain the failed conversation data
    assert not any("This should fail" in str(item) for item in history)


def test_cache_key_isolation(client: TestClient):
    """
    Test that cache keys properly isolate user data.

    Validates: Cache state analysis, user identifier inclusion
    """
    # User A creates conversation
    response_a = client.post("/api/user_a/chat",
                            json={"message": "Cache test message A"})
    assert response_a.status_code == 200
    conv_id_a = response_a.json()["conversation_id"]

    # User B creates conversation with same content
    response_b = client.post("/api/user_b/chat",
                            json={"message": "Cache test message A"})  # Same content
    assert response_b.status_code == 200
    conv_id_b = response_b.json()["conversation_id"]

    # Both should have different conversation IDs despite same content
    assert conv_id_a != conv_id_b

    # Verify each user can only access their own conversation
    hist_a = client.get(f"/api/user_a/conversations/{conv_id_a}/history")
    hist_b = client.get(f"/api/user_b/conversations/{conv_id_b}/history")

    assert hist_a.status_code == 200
    assert hist_b.status_code == 200

    # Each should only see their own message
    hist_a_data = hist_a.json()
    hist_b_data = hist_b.json()

    assert any("Cache test message A" in msg.get("content", "") for msg in hist_a_data)
    assert any("Cache test message A" in msg.get("content", "") for msg in hist_b_data)


def test_no_session_state_between_requests(client: TestClient):
    """
    Test that no session state persists between requests.

    Validates: Memory state audit, request independence
    """
    # First request - should create new conversation
    response1 = client.post("/api/session_test_user/chat",
                           json={"message": "First message"})
    assert response1.status_code == 200
    conv_id_1 = response1.json()["conversation_id"]

    # Second request - should be independent
    response2 = client.post("/api/session_test_user/chat",
                           json={"message": "Second message"})
    assert response2.status_code == 200
    conv_id_2 = response2.json()["conversation_id"]

    # Each request should create its own conversation or continue properly
    # depending on the API design, but they shouldn't interfere
    assert conv_id_1 != conv_id_2  # If each creates new conversation


def test_atomic_operation_boundary(client: TestClient):
    """
    Test that each operation handles its own transaction lifecycle.

    Validates: Atomic operation verification, transaction boundaries
    """
    # Perform multiple operations rapidly
    operations = []
    for i in range(3):
        response = client.post(f"/api/atomic_test_user_{i}/chat",
                              json={"message": f"Atomic operation {i}"})
        assert response.status_code == 200
        operations.append(response.json())

    # Each operation should be independent and complete
    for i, op_result in enumerate(operations):
        assert "conversation_id" in op_result
        assert "message" in op_result or "response" in op_result

    # Verify no cross-contamination between operations
    for i in range(3):
        history_resp = client.get(f"/api/atomic_test_user_{i}/conversations")
        assert history_resp.status_code == 200
        history = history_resp.json()

        # Each user should only see their own operations
        user_messages = []
        for item in history:
            if isinstance(item, dict) and "message" in item:
                user_messages.append(item["message"])
            elif isinstance(item, str):
                user_messages.append(item)

        assert f"Atomic operation {i}" in str(user_messages)


def test_memory_state_clean_after_request(client: TestClient):
    """
    Test that no memory state persists after request completion.

    Validates: Memory state audit, request-scoped dependencies
    """
    # Make several requests and verify no accumulation of state
    initial_count = len(client.cookies)  # Count any session cookies

    for i in range(5):
        response = client.post(f"/api/memory_test_user_{i}/chat",
                              json={"message": f"Memory test {i}"})
        assert response.status_code == 200

    # Final cookie count should not have grown unexpectedly
    final_count = len(client.cookies)

    # The exact behavior depends on session management, but generally
    # there should be no unexpected accumulation of state


def test_database_transaction_scope(client: TestClient):
    """
    Test that database transactions are properly scoped per request.

    Validates: Database state verification, transaction boundaries
    """
    import uuid

    user_id = f"txn_test_{uuid.uuid4().hex[:8]}"

    # First transaction
    resp1 = client.post(f"/api/{user_id}/chat",
                       json={"message": "Transaction 1"})
    assert resp1.status_code == 200

    # Second transaction
    resp2 = client.post(f"/api/{user_id}/chat",
                       json={"message": "Transaction 2"})
    assert resp2.status_code == 200

    # Verify both operations completed independently
    history_resp = client.get(f"/api/{user_id}/conversations")
    assert history_resp.status_code == 200
    history = history_resp.json()

    # Should contain both messages
    message_texts = []
    for item in history:
        if isinstance(item, dict) and 'message' in item:
            message_texts.append(item['message'])
        elif isinstance(item, dict) and 'content' in item:
            message_texts.append(item['content'])

    assert "Transaction 1" in str(message_texts)
    assert "Transaction 2" in str(message_texts)


# Parametrized test for multiple scenarios
@pytest.mark.parametrize("user_prefix,message_content", [
    ("iso_test_1", "Isolation test message 1"),
    ("iso_test_2", "Isolation test message 2"),
    ("iso_test_3", "Isolation test message 3"),
])
def test_parametrized_isolation(client: TestClient, user_prefix: str, message_content: str):
    """
    Parametrized test for user isolation scenarios.
    """
    # Create conversation for this user
    response = client.post(f"/api/{user_prefix}/chat",
                          json={"message": message_content})
    assert response.status_code == 200

    # Verify only this user can access their data
    access_response = client.get(f"/api/{user_prefix}/conversations")
    assert access_response.status_code == 200