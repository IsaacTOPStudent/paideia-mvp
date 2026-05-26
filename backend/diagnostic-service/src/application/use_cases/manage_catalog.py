from django.utils import timezone
from typing import List
from ...domain.entities.diagnostic_catalog import Diagnostic, NEECategory
from ...domain.entities.characterization import Characterization, SeverityLevel
from ...domain.ports.diagnostic_repository import DiagnosticCatalogRepository
from ...domain.ports.characterization_repository import CharacterizationRepository
from ...domain.exceptions import InvalidDiagnosticDataError, DiagnosticAlreadyExistsError, InvalidCharacterizationDataError, DiagnosticInactiveError, DiagnosticNotFoundError

class CreateDiagnosticUseCase:
    def __init__(self, repository: DiagnosticCatalogRepository):
        self.repository = repository

    def execute(self, data: dict) -> Diagnostic:
        # Create a new diagnostic (only admin)

        code = str(data.get('code', '')).strip().upper()
        name = str(data.get('name', '')).strip()

        if not code or not name:
            raise InvalidDiagnosticDataError('El código y el nombre del diagnóstico son obligatorios.')

        if self.repository.exists_by_code(code):
            raise DiagnosticAlreadyExistsError(f"Ya existe un diagnóstico con el código: {code}")
        
        try:
            category = NEECategory.from_string(data['category'])
        except ValueError:
            raise InvalidDiagnosticDataError(f"Categoría no válida: {data['category']}")
        
        diagnostic = Diagnostic(
            id=None,
            code=code,
            name=name,
            category=category,
            description=data.get('description', ''),
            normative_reference=data.get('normative_reference', ''),
            is_active=True,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        return self.repository.save(diagnostic)
    
class ListDiagnosticUseCase:
    """
        List diagnoses from the catalog
    """

    def __init__(self, repository: DiagnosticCatalogRepository):
        self.repository = repository

    def execute(self, active_only: bool = True) -> List[Diagnostic]:
        if active_only:
            return self.repository.find_all_active()
        return self.repository.find_all()
    
class CharacterizeStudentUseCase:
    """
        Characterize Student
    """

    def __init__(self, diagnostic_repo: DiagnosticCatalogRepository, char_repo: CharacterizationRepository):
        self.diagnostic_repo = diagnostic_repo
        self.char_repo = char_repo

    def execute(self, data:dict, psychologist_id: int) -> Characterization:

        if not self.diagnostic_repo.is_any_active():
            raise InvalidDiagnosticDataError("El catálogo de diagnósticos no está configurado. Contacte al Administrador")

        diagnostic_id = data.get('diagnostic_id', '')

        diagnostic = self.diagnostic_repo.find_by_id(diagnostic_id)

        if not diagnostic:
            raise DiagnosticNotFoundError(str(diagnostic_id))
        
        if not diagnostic.can_be_used():
            raise DiagnosticInactiveError(diagnostic_id)
        
        #validate severity
        try:
            severity = SeverityLevel.from_string(data['severity_level'])
        except ValueError:
            raise InvalidCharacterizationDataError(f"Nivel de severidad inválido: {data['severity_level']}")
        
        characterization = Characterization(
            id=None,
            student_id=data.get('student_id', ''),
            diagnostic_id=data.get('diagnostic_id', ''),
            severity_level=severity,
            identification_date=data.get('identification_date', ''),
            observations=data.get('observations', ''),
            cognitive_area_notes=data.get('cognitive_area_notes'),
            communicative_area_notes=data.get('communicative_area_notes'),
            socioemotional_area_notes=data.get('socioemotional_area_notes'),
            motor_area_notes=data.get('motor_area_notes'),
            sensory_area_notes=data.get('sensory_area_notes'),
            academic_area_notes=data.get('academic_area_notes'),
            behavioral_area_notes=data.get('behavioral_area_notes'),
            is_active=True,
            created_at=timezone.now(),
            created_by=psychologist_id
        )

        is_valid, missing = characterization.validate()
        if not is_valid:
            raise InvalidCharacterizationDataError(
                f"Campos obligatorios faltantes: {', '.join(missing)}"
            )

        return self.char_repo.save(characterization)
        