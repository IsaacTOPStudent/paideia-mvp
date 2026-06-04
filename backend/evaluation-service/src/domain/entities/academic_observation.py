from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum

class Subject(Enum):
    MATH = "MATH"
    SPANISH = "SPANISH"
    SCIENCE = "SCIENCE"
    SOCIAL_STUDIES = "SOCIAL_STUDIES"
    ARTS = "ARTS"
    PHYSICAL_EDUCATION = "PHYSICAL_EDUCATION"
    ENGLISH = "ENGLISH"
    OTHER = "OTHER"

    @classmethod
    def from_string(cls, value: str):
        if not value:
            raise ValueError("Materia requerida")
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Materia inválida: {value}")
        
    def to_spanish(self) -> str:
        translations = {
            "MATH": "Matemáticas",
            "SPANISH": "Español",
            "SCIENCE": "Ciencias Naturales",
            "SOCIAL_STUDIES": "Ciencias Sociales",
            "ARTS": "Artes",
            "PHYSICAL_EDUCATION": "Educación Física",
            "ENGLISH": "Inglés",
            "OTHER": "Otra",
        }
        return translations[self.name]
    
@dataclass
class AcademicObservation:
    student_id: int
    teacher_id: int

    observation_date: date
    subject: Subject
    performance_description: str 

    behavioral_notes: str
    pedagogical_adjustments_applied: Optional[str]
    recommendations: Optional[str]

    created_at: datetime 
    updated_at: datetime 

    is_active: bool = True
    id: Optional[int] = None 

    def __post_init__(self):
        if isinstance(self.subject, str):
            self.subject = Subject.from_string(self.subject)

        self.performance_description = (
            self.performance_description.strip()
            if self.performance_description
            else ""
        )

        self.behavioral_notes = (
            self.behavioral_notes.strip()
            if self.behavioral_notes
            else ""
        )

        self.pedagogical_adjustments_applied = (
            self.pedagogical_adjustments_applied.strip()
            if self.pedagogical_adjustments_applied
            else None
        )

        self.recommendations = (
            self.recommendations.strip()
            if self.recommendations
            else None
        )

    def validate(self) -> tuple[bool, list[str]]:

        errors = []

        if not self.observation_date:
            errors.append("observation_date")

        if not self.subject:
            errors.append("subject")
            
        if not self.performance_description or not self.performance_description.strip():
            errors.append("performance_description")

        if (
            not self.behavioral_notes
            or not self.behavioral_notes.strip()
        ):
            errors.append(
                "Las observaciones conductuales son obligatorias."
            )

        if self.observation_date:
            if self.observation_date > date.today():
                errors.append(
                    "La fecha de observación no puede ser futura."
                )

        if (
            self.performance_description
            and len(self.performance_description.strip()) < 10
        ):
            errors.append(
                "La descripción del desempeño debe tener al menos "
                "10 caracteres."
            )

        if (
        self.behavioral_notes
        and len(self.behavioral_notes.strip()) < 10
        ):
            errors.append(
                "Las observaciones conductuales deben tener al menos "
                "10 caracteres."
            )

        if (
        self.pedagogical_adjustments_applied
        and len(
            self.pedagogical_adjustments_applied.strip()
        ) < 5
        ):
            errors.append(
                "Los ajustes pedagógicos deben tener al menos "
                "5 caracteres."
            )

        if (
        self.recommendations
        and len(self.recommendations.strip()) < 5
        ):
            errors.append(
                "Las recomendaciones deben tener al menos "
                "5 caracteres."
            )

        return (len(errors) == 0, errors)
    
    def can_be_deleted(self) -> bool:
        return False
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        return (
            f"AcademicObservation("
            f"student={self.student_id}, "
            f"subject={self.subject.to_spanish()}, "
            f"date={self.observation_date})"
        )