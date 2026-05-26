from typing import Optional, List
from diagnostics.models import DiagnosticModel, CharacterizationModel
from ...domain.entities.diagnostic_catalog import Diagnostic, NEECategory
from ...domain.entities.characterization import Characterization, SeverityLevel
from ...domain.ports.diagnostic_repository import DiagnosticCatalogRepository
from ...domain.ports.characterization_repository import CharacterizationRepository

class DjangoDiagnosticRepository(DiagnosticCatalogRepository):

    def save(self, diagnostic: Diagnostic) -> Diagnostic:
        diagnostic_data = {
            "code": diagnostic.code,
            "name": diagnostic.name,
            "category": diagnostic.category.value,
            "description": diagnostic.description,
            "normative_reference": diagnostic.normative_reference,
            "is_active": diagnostic.is_active
        }

        if diagnostic.id:
            obj = DiagnosticModel.objects.get(id=diagnostic.id)
            for key, value in diagnostic_data.items():
                setattr(obj, key, value)

            obj.save()
        else:
            obj = DiagnosticModel.objects.create(**diagnostic_data)
            diagnostic.id = obj.pk

        return diagnostic
    
    def find_by_id(self, diagnostic_id: int) -> Optional[Diagnostic]:
        try:
            obj = DiagnosticModel.objects.get(id=diagnostic_id)
            return self._to_entity(obj)
        except DiagnosticModel.DoesNotExist:
            return None
        
    def find_by_code(self, code: str) -> Optional[Diagnostic]:
        try:
            obj = DiagnosticModel.objects.get(code=code)
            return self._to_entity(obj)
        except DiagnosticModel.DoesNotExist:
            return None
        
    def find_all_active(self) -> List[Diagnostic]:
        return [self._to_entity(obj) for obj in DiagnosticModel.objects.filter(is_active=True)]
    
    def find_all(self) -> List[Diagnostic]:
        return [self._to_entity(obj) for obj in DiagnosticModel.objects.all()]
    
    def exists_by_code(self, code: str) -> bool:
        return DiagnosticModel.objects.filter(code=code).exists()
    
    def is_any_active(self) -> bool:
        return DiagnosticModel.objects.filter(is_active=True).exists()
    
    @staticmethod
    def _to_entity(model: DiagnosticModel) -> Diagnostic:
        return Diagnostic(
            id=model.pk,
            code=model.code,
            name=model.name,
            category=NEECategory.from_string(model.category),
            description=model.description,
            normative_reference=model.normative_reference,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

class DjangoCharacterizationRepository(CharacterizationRepository):

    def save(self, characterization: Characterization) -> Characterization:

        characterization_data = {
            "severity_level": characterization.severity_level.value,
            "observations": characterization.observations,
            "cognitive_area_notes": characterization.cognitive_area_notes,
            "communicative_area_notes": characterization.communicative_area_notes,
            "socioemotional_area_notes": characterization.socioemotional_area_notes,
            "motor_area_notes": characterization.motor_area_notes,
            "sensory_area_notes": characterization.sensory_area_notes,
            "academic_area_notes": characterization.academic_area_notes,
            "behavioral_area_notes": characterization.behavioral_area_notes,
            "is_active": characterization.is_active,
        }

        if characterization.id:
            obj = CharacterizationModel.objects.get(id=characterization.id)
            for key, value in characterization_data.items():
                setattr(obj, key, value)

            obj.updated_by = characterization.updated_by
            obj.save()

        else:
            creation_data = {
                **characterization_data,
                "student_id": characterization.student_id,
                "diagnostic_id": characterization.diagnostic_id,
                "identification_date": characterization.identification_date,
                "created_by": characterization.created_by
            }

            obj = CharacterizationModel.objects.create(**creation_data)
            characterization.id = obj.pk
        
        return characterization

    def find_by_id(self, characterization_id: int) -> Optional[Characterization]:
        try:
            obj = CharacterizationModel.objects.get(id=characterization_id)
            return self._to_entity(obj)
        except CharacterizationModel.DoesNotExist:
            return None

    def find_by_student(self, student_id: int) -> List[Characterization]:

        return [self._to_entity(obj) for obj in CharacterizationModel.objects.filter(student_id=student_id)]
    
    def find_active_by_student(self, student_id: int) -> List[Characterization]:

        return [self._to_entity(obj) for obj in CharacterizationModel.objects.filter(
            student_id=student_id,
            is_active=True
        )]

    def find_by_student_and_diagnostic(self, student_id: int, diagnostic_id: int) -> Optional[Characterization]:
        try:
            obj = CharacterizationModel.objects.get(
                student_id=student_id,
                diagnostic_id=diagnostic_id
            )
            return self._to_entity(obj)
        except CharacterizationModel.DoesNotExist:
            return None
        
    @staticmethod
    def _to_entity(model: CharacterizationModel) -> Characterization:
        return Characterization(
            id=model.pk,
            student_id=model.student_id,
            diagnostic_id=model.diagnostic_id,
            severity_level=SeverityLevel.from_string(model.severity_level),
            identification_date=model.identification_date,
            observations=model.observations,
            cognitive_area_notes=model.cognitive_area_notes,
            communicative_area_notes=model.communicative_area_notes,
            socioemotional_area_notes=model.socioemotional_area_notes,
            motor_area_notes=model.motor_area_notes,
            sensory_area_notes=model.sensory_area_notes,
            academic_area_notes=model.academic_area_notes,
            behavioral_area_notes=model.behavioral_area_notes,
            is_active=model.is_active,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by
        )