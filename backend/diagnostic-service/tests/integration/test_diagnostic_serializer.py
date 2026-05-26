import pytest

from diagnostics.serializers import DiagnosticSerializer, DiagnosticUpdateSerializer
from src.domain.entities.diagnostic_catalog import (
    Diagnostic,
    NEECategory
)


@pytest.mark.unit
class TestDiagnosticSerializer:

    def test_serializer_returns_category_as_string_value(self):
        diagnostic = Diagnostic(
            id=1,
            code="DSL001",
            name="Dislexia",
            category=NEECategory.SPECIFIC_LEARNING_DISORDER,
            description="Dificultad específica en lectoescritura",
            normative_reference="DSM-5",
            is_active=True,
            created_at=None,
            updated_at=None
        )

        serializer = DiagnosticSerializer(diagnostic)

        assert serializer.data["category"] == "SPECIFIC_LEARNING_DISORDER"

    def test_serializer_returns_category_display_in_spanish(self):
        diagnostic = Diagnostic(
            id=1,
            code="ADH001",
            name="TDAH",
            category=NEECategory.ADHD,
            description="Trastorno por déficit de atención",
            normative_reference="DSM-5",
            is_active=True,
            created_at=None,
            updated_at=None
        )

        serializer = DiagnosticSerializer(diagnostic)

        assert serializer.data["category_display"] == "TDAH"

    def test_serializer_accepts_valid_input_data(self):
        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "TEA",
            "normative_reference": "DSM-5",
            "is_active": True
        }

        serializer = DiagnosticSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["category"] == "AUTISM_SPECTRUM"

    def test_serializer_rejects_missing_required_fields(self):
        data = {
            "description": "Sin campos requeridos"
        }

        serializer = DiagnosticSerializer(data=data)

        assert not serializer.is_valid()

        assert "code" in serializer.errors
        assert "name" in serializer.errors
        assert "category" in serializer.errors
        assert "is_active" in serializer.errors

    def test_serializer_returns_category_string_when_invalid_enum_instance(self):
        class FakeCategory:
            value = "CUSTOM_CATEGORY"

        diagnostic = {
            "id": 1,
            "code": "TEST001",
            "name": "Test",
            "category": FakeCategory(),
            "description": "Test",
            "is_active": True
        }

        serializer = DiagnosticSerializer(diagnostic)

        assert serializer.data["category"] == "CUSTOM_CATEGORY"

    def test_category_display_returns_original_string_when_invalid(self):
        diagnostic = {
            "id": 1,
            "code": "TEST001",
            "name": "Test",
            "category": "INVALID_CATEGORY",
            "description": "Test",
            "is_active": True
        }

        serializer = DiagnosticSerializer(diagnostic)

        assert serializer.data["category_display"] == "INVALID_CATEGORY"

    def test_serializer_serializes_all_basic_fields(self):
        diagnostic = Diagnostic(
            id=10,
            code="VIS001",
            name="Discapacidad Visual",
            category=NEECategory.SENSORY_VISUAL,
            description="Limitación visual",
            normative_reference="Norma X",
            is_active=False,
            created_at=None,
            updated_at=None
        )

        serializer = DiagnosticSerializer(diagnostic)

        data = serializer.data

        assert data["id"] == 10
        assert data["code"] == "VIS001"
        assert data["name"] == "Discapacidad Visual"
        assert data["category"] == "SENSORY_VISUAL"
        assert data["description"] == "Limitación visual"
        assert data["normative_reference"] == "Norma X"
        assert data["is_active"] is False

class TestDiagnosticUpdateSerializer:

    def test_serializer_valid_data(self):

        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "Diagnóstico actualizado",
            "normative_reference": "Ley 2216"
        }

        serializer = DiagnosticUpdateSerializer(
            data=data
        )

        assert serializer.is_valid()
        assert serializer.validated_data["code"] == "AUT001"

    def test_serializer_optional_normative_reference(self):

        data = {
            "code": "AUT001",
            "name": "Autismo",
            "category": "AUTISM_SPECTRUM",
            "description": "Diagnóstico actualizado"
        }

        serializer = DiagnosticUpdateSerializer(
            data=data
        )

        assert serializer.is_valid()

    def test_serializer_missing_fields(self):

        serializer = DiagnosticUpdateSerializer(
            data={}
        )

        assert serializer.is_valid()
