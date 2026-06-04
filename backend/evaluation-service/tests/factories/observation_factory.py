from datetime import date, datetime
from typing import Union

from src.domain.entities.academic_observation import (
    AcademicObservation,
    Subject,
)


class ObservationFactory:
    @staticmethod
    def build(
        student_id: int = 12,
        teacher_id: int = 7,
        observation_date: date | None = None,
        subject: Union[Subject, str] = Subject.MATH,
        performance_description: str = "El estudiante presenta un desempeño adecuado en clase.",
        behavioral_notes: str = "Actitud cooperativa y respetuosa.",
        pedagogical_adjustments_applied: str | None = "Uso de material visual.",
        recommendations: str | None = "Continuar con apoyo diferenciado.",
        is_active: bool = True,
        id: int | None = None,
    ) -> AcademicObservation:
        observation_date = observation_date or date.today()

        if isinstance(subject, str):
            subject = Subject.from_string(subject)

        return AcademicObservation(
            student_id=student_id,
            teacher_id=teacher_id,
            observation_date=observation_date,
            subject=subject,
            performance_description=performance_description,
            behavioral_notes=behavioral_notes,
            pedagogical_adjustments_applied=pedagogical_adjustments_applied,
            recommendations=recommendations,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=is_active,
            id=id,
        )
