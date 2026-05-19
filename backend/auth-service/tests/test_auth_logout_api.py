import pytest
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import UserModel
from typing import cast


@pytest.mark.django_db
class TestAuthLogoutAPI:
    """
    Integration tests for logout endpoint
    POST /api/auth/logout/
    """

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def active_user(self):
        return UserModel.objects.create(
            email="admin@test.com",
            full_name="Administrador Test",
            password=make_password("Admin123*"),
            role="ADMIN",
            status="ACTIVE"
        )

    @pytest.fixture
    def authenticated_client(self, api_client, active_user):
        """
        Client authenticated with access token
        """
        refresh = cast(RefreshToken, RefreshToken.for_user(active_user))
        access_token = str(refresh.access_token)

        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        return api_client, str(refresh)

    def test_logout_success(self, authenticated_client):
        """
        Should logout successfully and blacklist refresh token
        """
        client, refresh_token = authenticated_client

        url = reverse("logout")

        payload = {
            "refresh": refresh_token
        }

        response = client.post(url, payload, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Sesión cerrada exitosamente"

    def test_logout_without_refresh_token(self, authenticated_client):
        """
        Should fail when refresh token is missing
        """
        client, _ = authenticated_client

        url = reverse("logout")

        response = client.post(url, {}, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    def test_logout_invalid_refresh_token(self, authenticated_client):
        """
        Should fail when refresh token is invalid
        """
        client, _ = authenticated_client

        url = reverse("logout")

        payload = {
            "refresh": "token-invalido"
        }

        response = client.post(url, payload, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    def test_logout_without_authentication(self, api_client, active_user):
        """
        Should fail if access token is not provided
        """
        refresh = RefreshToken.for_user(active_user)

        url = reverse("logout")

        payload = {
            "refresh": str(refresh)
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 401

    def test_logout_blacklisted_token_cannot_be_reused(self, authenticated_client):
        """
        Same refresh token should not be usable twice
        """
        client, refresh_token = authenticated_client

        url = reverse("logout")

        payload = {
            "refresh": refresh_token
        }

        first_response = client.post(url, payload, format="json")
        second_response = client.post(url, payload, format="json")

        assert first_response.status_code == 200
        assert second_response.status_code == 400