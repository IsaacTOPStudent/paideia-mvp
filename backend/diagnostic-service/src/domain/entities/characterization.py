from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum
from django.utils import timezone

class SeverityLevel(Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"

    @classmethod
    def from_string(cls, value: str):
        try: 
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Nivel de severidad inválido: {value}")


    def to_spanish(self) -> str:
        traslations = {
            'MILD': 'Leve',
            'MODERATE': 'Moderado',
            'SEVERE': 'Severo'
        }

        return traslations[self.name]
    

@dataclass
class Characterization:


    student_id: int  # FK a Student
    diagnostic_id: int  # FK a DiagnosticCatalog

    #Characterization core
    severity_level: SeverityLevel
    identification_date: date

    #General observations
    id: Optional[int]
    observations: Optional[str] = None

    
    # Evaluated areas
    cognitive_area_notes: Optional[str] = None 
    communicative_area_notes: Optional[str] = None
    socioemotional_area_notes: Optional[str] = None
    motor_area_notes: Optional[str] = None 
    sensory_area_notes: Optional[str] = None
    academic_area_notes: Optional[str] = None
    behavioral_area_notes: Optional[str] = None
    
    # Control (RN-06)
    is_active: bool = True

    #Metadata
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.severity_level, str):
            self.severity_level = SeverityLevel.from_string(self.severity_level)

        if self.created_at is None:
            self.created_at = timezone.now()

        if self.updated_at is None:
            self.updated_at = timezone.now()

        if self.observations:
            self.observations = self.observations.strip()

    def validate(self) -> tuple[bool, list[str]]:
        errors = []


        if not self.student_id:
            errors.append("student_id")

        if not self.diagnostic_id:
            errors.append("diagnostic_id")

        if not self.identification_date:
            errors.append("identification_date")

        if not isinstance(
            self.severity_level,
            SeverityLevel
        ):
            errors.append("severity_level")

        return (len(errors) == 0, errors)

    def can_be_used(self) -> bool:
        return self.is_active

    def can_be_deleted(self) -> bool:
        """RN-06: Las caracterizaciones no se eliminan"""
        return False
    
    def mark_as_inactive(self, admin_id: int) -> None:
        """RN-06: Solo Admin puede marcar como inactiva"""
        self.is_active = False
        self.updated_at = timezone.now()
        self.updated_by = admin_id

    def reactivate(self, admin_id: int) -> None:
        self.is_active = True 
        self.updated_at = timezone.now()
        self.updated_by = admin_id

    @property
    def severity_in_spanish(self) -> str:
        return self.severity_level.to_spanish()
    
    def __str__(self):
        return (
            f"Characterization("
            f"student_id={self.student_id}, "
            f"diagnostic_id={self.diagnostic_id}, "
            f"severity={self.severity_level.value}, "
            f"active={self.is_active}"
            f")"
        )
        
