import pytest
from rest_framework.test import APIClient

from authentication.models import UserModel, AuditLogModel


USERS_URL = '/api/auth/users/'
TOKEN_URL = '/api/auth/login/'
LOGOUT_URL = '/api/auth/logout/'


@pytest.mark.django_db
class TestAuditAPI:
    def setup_method(self):
        self.client = APIClient()

        self.admin = UserModel.objects.create_user(
            email="admin@test.com",
            password="Admin123*",
            full_name="Administrador",
            role="ADMIN",
        )

        self.teacher = UserModel.objects.create_user(
            email="teacher@test.com",
            password="Teacher123*",
            full_name="Docente",
            role="TEACHER",
        )

    def authenticate_admin(self):
        response = self.client.post(
            TOKEN_URL,
            {
                "email": "admin@test.com",
                "password": "Admin123*"
            },
            format="json"
        )

        access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def authenticate_teacher(self):
        response = self.client.post(
            TOKEN_URL,
            {
                "email": "teacher@test.com",
                "password": "Teacher123*"
            },
            format="json"
        )

        access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    # LOGIN

    def test_login_creates_audit_log(self):
        response = self.client.post(
            TOKEN_URL,
            {
                "email": "teacher@test.com",
                "password": "Teacher123*"
            },
            format="json"
        )

        assert response.status_code == 200

        assert AuditLogModel.objects.filter(
            user=self.teacher,
            action="LOGIN"
        ).exists()

    # CREATE USER

    def test_create_user_creates_audit_log(self):
        self.authenticate_admin()

        payload = {
            "email": "newuser@test.com",
            "full_name": "Nuevo Usuario",
            "password": "Password123*",
            "role": "PSYCHOLOGIST"
        }

        response = self.client.post(f"{USERS_URL}create/", payload, format="json")

        assert response.status_code == 201

        assert AuditLogModel.objects.filter(
            user=self.admin,
            action="CREATE_USER"
        ).exists()

    # UPDATE USER

    def test_update_user_creates_audit_log(self):
        self.authenticate_admin()

        payload = {
            "full_name": "Docente Actualizado",
            "role": "SECRETARY"
        }

        response = self.client.patch(
            f"{USERS_URL}{self.teacher.id}/update/",
            payload,
            format="json"
        )

        assert response.status_code == 200

        assert AuditLogModel.objects.filter(
            user=self.admin,
            action="UPDATE_USER"
        ).exists()

    # DEACTIVATE USER

    def test_deactivate_user_creates_audit_log(self):
        self.authenticate_admin()

        response = self.client.patch(f"{USERS_URL}{self.teacher.id}/deactivate/")

        assert response.status_code == 200

        assert AuditLogModel.objects.filter(
            user=self.admin,
            action="DEACTIVATE_USER"
        ).exists()

    # REACTIVATE USER

    def test_reactivate_user_creates_audit_log(self):
        self.authenticate_admin()

        # desactivar primero
        self.client.patch(f"{USERS_URL}{self.teacher.id}/deactivate/")

        response = self.client.patch(
            f"{USERS_URL}{self.teacher.id}/activate/"
        )

        assert response.status_code == 200

        assert AuditLogModel.objects.filter(
            user=self.admin,
            action="REACTIVATE_USER"
        ).exists()