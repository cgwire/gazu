import requests
import json
import sseclient

from cachetools import LRUCache

cache = LRUCache(maxsize=100)


def with_requests(url):
    """Get a streaming response for the given event feed using requests."""
    return requests.get(url, stream=True)


def listen_to_events():
    url = "http://localhost:5001"
    client = sseclient.SSEClient(with_requests(url))
    for event in client.events():
        print(json.loads(event.data))
