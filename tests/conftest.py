import pytest
import gazu.client


@pytest.fixture(autouse=True)
def reset_client_state():
    """Save and restore the default client state around every test."""
    client = gazu.client.default_client
    original_host = client.host
    original_event_host = client.event_host
    original_tokens = client.tokens.copy()
    yield
    client.host = original_host
    client.event_host = original_event_host
    client.tokens = original_tokens
