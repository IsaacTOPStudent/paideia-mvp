from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum

class FollowUpFrequency(Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    BIANNUAL = "BIANNUAL"
    ANNUAL = "ANNUAL"

    @classmethod
    def from_string(cls, value: str):
        if not value:
            raise ValueError("Frecuencia de seguimiento requerida")
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Frecuencia inválida: {value}")
        
    def to_spanish(self) -> str:
        translations = {
            "MONTHLY": "Mensual",
            "QUARTERLY": "Trimestral",
            "BIANNUAL": "Semestral",
            "ANNUAL": "Anual",
        }
        return translations[self.name]

class FollowUpStatus(Enum):
    """
    Student tracking status.
    Determines whether tracking is up to date or pending.
    """
    UP_TO_DATE = "UP_TO_DATE"
    PENDING = "PENDING"

    def to_spanish(self) -> str:
        """RNF-07: Mensajes en español"""
        translations = {
            "UP_TO_DATE": "Al día",
            "PENDING": "Pendiente de actualización",
        }
        return translations[self.name]
    
@dataclass
class PsychologicalEvaluation:
    student_id: int
    psychologist_id: int 

    evaluation_date: date
    instrument_used: str # Ej: "Wisc-V", "Vineland", "Conners"
    findings: str 
    recommendations: str

    cognitive_assessment: Optional[str]
    emotional_assessment: Optional[str]
    behavioral_assessment: Optional[str]
    motor_assessment: Optional[str]
    social_assessment: Optional[str]

    follow_up_frequency: FollowUpFrequency
    next_evaluation_date: date 

    created_at: datetime
    updated_at: datetime 

    is_active: bool = True
    id: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.follow_up_frequency, str):
            self.follow_up_frequency = FollowUpFrequency.from_string(
                self.follow_up_frequency
            )

        self.instrument_used = (
            self.instrument_used.strip()
            if self.instrument_used
            else ""
        )

        self.findings = (
            self.findings.strip()
            if self.findings
            else ""
        )

        self.recommendations = (
            self.recommendations.strip()
            if self.recommendations
            else ""
        )

    # Domain properties
    @property
    def follow_up_status(self) -> FollowUpStatus:
        """
        Calculate follow-up status.
        If the next evaluation date has already passed → PENDING.
        """
        if date.today() > self.next_evaluation_date:
            return FollowUpStatus.PENDING
        return FollowUpStatus.UP_TO_DATE
    
    @property
    def is_overdue(self) -> bool:
        return self.follow_up_status == FollowUpStatus.PENDING
    
    @property
    def days_until_next_evaluation(self) -> int:
        delta = self.next_evaluation_date - date.today()
        return delta.days
    
    #Domain Methods
    def validate(self) -> tuple[bool, list[str]]:

        errors = []

        if not self.instrument_used or not self.instrument_used.strip():
            errors.append("instrument_used")
        if not self.findings or not self.findings.strip():
            errors.append("findings")
        if not self.recommendations or not self.recommendations.strip():
            errors.append("recommendations")
        if not self.evaluation_date:
            errors.append("evaluation_date")
        if not self.follow_up_frequency:
            errors.append("follow_up_frequency")
        if not self.next_evaluation_date:
            errors.append("next_evaluation_date")

        if self.next_evaluation_date and self.next_evaluation_date < date.today():
            errors.append("La proxima fecha de evaluación no debe ser anterior a hoy")

        if self.evaluation_date and self.next_evaluation_date:
            if self.next_evaluation_date <= self.evaluation_date:
                errors.append(
                    "La próxima fecha de evaluación debe ser posterior."
                )

        if self.instrument_used and len(self.instrument_used.strip()) < 3:
            errors.append("El instrumento usado debe tener al menos 3 caracteres.")

        if self.findings and len(self.findings.strip()) < 10:
            errors.append(
                "Los hallazgos deben tener al menos 10 caracteres"
            )

        if self.recommendations and len(self.recommendations.strip()) < 10:
            errors.append("Las recomendaciones deben tener al menos 10 caracteres.")

        assessment_areas = [
            self.cognitive_assessment,
            self.emotional_assessment,
            self.behavioral_assessment,
            self.motor_assessment,
            self.social_assessment,
        ]

        if not any(
            area and area.strip()
            for area in assessment_areas
        ):
            errors.append(
                "Debe registrar al menos un área evaluada."
            )

        return (len(errors) == 0, errors)
    
    def can_be_deleted(self) -> bool:
        return False 
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        return (
            f"PsychologicalEvaluation("
            f"student={self.student_id}, "
            f"date={self.evaluation_date}, "
            f"status={self.follow_up_status.to_spanish()})"
        )
