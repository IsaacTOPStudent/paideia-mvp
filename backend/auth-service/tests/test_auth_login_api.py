import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from authentication.models import UserModel, AuditLogModel

@pytest.mark.django_db
class TestAuthLoginAPI:
    """
    Integration tests for login endpoint (CU-01)
    Endpoint: POST /api/auth/token/
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
    def inactive_user(self):
        return UserModel.objects.create(
            email="inactive@test.com",
            full_name="Usuario Inactivo",
            password=make_password("Admin123*"),
            role="TEACHER",
            status="INACTIVE"
        )

    def test_login_success(self, api_client, active_user):
        """
        Should authenticate correctly and return tokens + user data
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "admin@test.com",
            "password": "Admin123*"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

        assert response.data["user"]["email"] == active_user.email
        assert response.data["user"]["role"] == "ADMIN"

    def test_login_invalid_password(self, api_client, active_user):
        """
        Should reject invalid password
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "admin@test.com",
            "password": "WrongPassword"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 401
        assert "detail" in response.data

    def test_login_nonexistent_user(self, api_client):
        """
        Should reject non-existing user
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "fake@test.com",
            "password": "Admin123*"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 401
        assert "detail" in response.data

    def test_login_inactive_user(self, api_client, inactive_user):
        """
        Should reject inactive user
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "inactive@test.com",
            "password": "Admin123*"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 401
        assert "detail" in response.data
        assert "inactivo" in str(response.data["detail"]).lower()

    def test_login_creates_audit_log(self, api_client, active_user):
        """
        Successful login should create audit log
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "admin@test.com",
            "password": "Admin123*"
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == 200

        audit = AuditLogModel.objects.filter(
            user=active_user,
            action="LOGIN"
        ).first()

        assert audit is not None
        assert audit.module == "AUTH"

    def test_login_response_contains_custom_claims(self, api_client, active_user):
        """
        Response should contain user payload
        """
        url = reverse("token_obtain_pair")

        payload = {
            "email": "admin@test.com",
            "password": "Admin123*"
        }

        response = api_client.post(url, payload, format="json")

        user_data = response.data["user"]

        assert user_data["id"] == active_user.id
        assert user_data["email"] == active_user.email
        assert user_data["full_name"] == active_user.full_name
        assert user_data["role"] == active_user.role