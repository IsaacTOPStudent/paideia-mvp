import pytest
from typing import cast
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import UserModel

USERS_URL = '/api/auth/users/'
TOKEN_URL = '/api/auth/login/'

@pytest.mark.django_db
class TestUserManagementAPI:
    def setup_method(self):
        self.client = APIClient()

        # Admin user
        self.admin = UserModel.objects.create_user(
            email="admin@test.com",
            password="Admin123*",
            full_name="Administrador",
            role="ADMIN",
        )

        # Non-admin user
        self.teacher = UserModel.objects.create_user(
            email="teacher@test.com",
            password="Teacher123*",
            full_name="Docente",
            role="TEACHER",
        )

    # HELPERS

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

    # ==========================================
    # POST /users/
    # ==========================================

    def test_admin_can_create_user(self):
        self.authenticate_admin()

        payload = {
            "email": "newuser@test.com",
            "full_name": "Nuevo Usuario",
            "password": "Password123*",
            "role": "PSYCHOLOGIST"
        }

        response = self.client.post(f"{USERS_URL}create/", payload, format="json")

        assert response.status_code == 201
        assert response.data["message"] == "Usuario creado exitosamente"
        assert UserModel.objects.filter(email="newuser@test.com").exists()

    def test_non_admin_cannot_create_user(self):
        self.authenticate_teacher()

        payload = {
            "email": "forbidden@test.com",
            "full_name": "Forbidden User",
            "password": "Password123*",
            "role": "SECRETARY"
        }

        response = self.client.post(f"{USERS_URL}create/", payload, format="json")

        assert response.status_code == 403

    def test_create_user_duplicate_email(self):
        self.authenticate_admin()

        payload = {
            "email": "teacher@test.com",
            "full_name": "Duplicado",
            "password": "Password123*",
            "role": "TEACHER"
        }

        response = self.client.post(f"{USERS_URL}create/", payload, format="json")

        assert response.status_code == 409

    def test_create_user_invalid_data(self):
        self.authenticate_admin()

        payload = {
            "email": "bad-email",
            "full_name": "",
            "password": "123",
            "role": "INVALID_ROLE"
        }

        response = self.client.post(f"{USERS_URL}create/", payload, format="json")

        assert response.status_code == 400

    # ==========================================
    # GET /users/
    # ==========================================

    def test_admin_can_list_users(self):
        self.authenticate_admin()

        response = self.client.get(USERS_URL)

        assert response.status_code == 200
        assert "data" in response.data
        assert response.data["count"] >= 2

    def test_non_admin_cannot_list_users(self):
        self.authenticate_teacher()

        response = self.client.get(USERS_URL)

        assert response.status_code == 403

    def test_admin_can_list_users_with_inactive(self):
        self.authenticate_admin()

        inactive_user = UserModel.objects.create_user(
            email="inactive@test.com",
            password="Inactive123*",
            full_name="Inactive User",
            role="SECRETARY",
            status="INACTIVE"
        )

        response = self.client.get(f"{USERS_URL}?include_inactive=true")

        assert response.status_code == 200
        assert response.data["count"] >= 3

    # ==========================================
    # GET /users/<id>/
    # ==========================================

    def test_admin_can_get_user_detail(self):
        self.authenticate_admin()

        response = self.client.get(f"{USERS_URL}{self.teacher.pk}/")

        assert response.status_code == 200
        assert response.data["email"] == self.teacher.email

    def test_non_admin_cannot_get_user_detail(self):
        self.authenticate_teacher()

        response = self.client.get(f"{USERS_URL}{self.admin.pk}/")

        assert response.status_code == 403

    def test_get_nonexistent_user(self):
        self.authenticate_admin()

        response = self.client.get(f"{USERS_URL}9999/")

        assert response.status_code == 404

    # ==========================================
    # PUT /users/<id>/
    # ==========================================

    def test_admin_can_update_user(self):
        self.authenticate_admin()

        payload = {
            "full_name": "Docente Actualizado",
            "role": "SECRETARY"
        }

        response = self.client.patch(
            f"{USERS_URL}{self.teacher.pk}/update/",
            payload,
            format="json"
        )

        assert response.status_code == 200

        updated = UserModel.objects.get(id=self.teacher.pk)
        assert updated.full_name == "Docente Actualizado"
        assert updated.role == "SECRETARY"

    def test_non_admin_cannot_update_user(self):
        self.authenticate_teacher()

        payload = {
            "full_name": "No autorizado"
        }

        response = self.client.put(
            f"{USERS_URL}{self.admin.pk}/",
            payload,
            format="json"
        )

        assert response.status_code == 403

    def test_update_nonexistent_user(self):
        self.authenticate_admin()

        payload = {
            "full_name": "Ghost"
        }

        response = self.client.patch(
            f"{USERS_URL}9999/update/",
            payload,
            format="json"
        )

        assert response.status_code == 404

    def test_update_invalid_role(self):
        self.authenticate_admin()

        payload = {
            "role": "INVALID_ROLE"
        }

        response = self.client.patch(
            f"{USERS_URL}{self.teacher.pk}/update/",
            payload,
            format="json"
        )

        assert response.status_code == 400

    # ==========================================
    # DELETE /users/<id>/
    # ==========================================

    def test_admin_can_deactivate_user(self):
        self.authenticate_admin()

        response = self.client.patch(f"{USERS_URL}{self.teacher.pk}/deactivate/")

        assert response.status_code == 200
        assert response.data['data']['status'] == 'INACTIVE'
        assert response.data['data']['status_display'] == 'Inactivo'

        deactivated = UserModel.objects.get(id=self.teacher.pk)
        assert deactivated.status == "INACTIVE"

    def test_non_admin_cannot_deactivate_user(self):
        self.authenticate_teacher()

        response = self.client.patch(f"{USERS_URL}{self.admin.pk}/deactivate/")

        assert response.status_code == 403

    def test_deactivate_nonexistent_user(self):
        self.authenticate_admin()

        response = self.client.patch(f"{USERS_URL}9999/deactivate/")

        assert response.status_code == 404

    def test_admin_cannot_deactivate_self(self):
        self.authenticate_admin()

        response = self.client.patch(f"{USERS_URL}{self.admin.pk}/deactivate/")

        assert response.status_code == 400


    def test_admin_can_reactivate_user(self):
        self.authenticate_admin()
        self.teacher.status = "INACTIVE"
        self.teacher.save()

        response = self.client.patch(f"{USERS_URL}{self.teacher.pk}/activate/")
        assert response.status_code == 200
        assert response.data['data']['status'] == 'ACTIVE'
        assert response.data['data']['status_display'] == 'Activo'

        reactivated = UserModel.objects.get(id=self.teacher.pk)
        assert reactivated.status == "ACTIVE"