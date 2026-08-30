import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    """Întoarce o funcție: fiecare test își autentifică propriul user."""

    def _login(user, password="pw12345"):
        response = api_client.post(
            "/api/v1/auth/token/",
            {"username": user.username, "password": password},
            format="json",
        )
        token = response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return api_client

    return _login


@pytest.fixture(autouse=True)
def clear_cache():
    """Contoarele de throttling trăiesc în cache — fără asta, se scurg între teste."""
    cache.clear()
    yield
    cache.clear()
