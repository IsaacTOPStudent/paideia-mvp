from datetime import date, datetime, timedelta
from typing import Union

from src.domain.entities.psychological_evaluation import (
    FollowUpFrequency,
    PsychologicalEvaluation,
)


class EvaluationFactory:
    @staticmethod
    def build(
        student_id: int = 10,
        psychologist_id: int = 5,
        evaluation_date: date | None = None,
        instrument_used: str = "WISC-V",
        findings: str = "Resultados de evaluación válidos.",
        recommendations: str = "Realizar seguimiento mensual.",
        cognitive_assessment: str = "Cognitivo dentro de lo esperado.",
        emotional_assessment: str | None = None,
        behavioral_assessment: str | None = None,
        motor_assessment: str | None = None,
        social_assessment: str | None = None,
        follow_up_frequency: Union[FollowUpFrequency, str] = FollowUpFrequency.MONTHLY,
        next_evaluation_date: date | None = None,
        is_active: bool = True,
        id: int | None = None,
    ) -> PsychologicalEvaluation:
        evaluation_date = evaluation_date or date.today()
        next_evaluation_date = next_evaluation_date or (evaluation_date + timedelta(days=30))

        if isinstance(follow_up_frequency, str):
            follow_up_frequency = FollowUpFrequency.from_string(follow_up_frequency)

        return PsychologicalEvaluation(
            student_id=student_id,
            psychologist_id=psychologist_id,
            evaluation_date=evaluation_date,
            instrument_used=instrument_used,
            findings=findings,
            recommendations=recommendations,
            cognitive_assessment=cognitive_assessment,
            emotional_assessment=emotional_assessment,
            behavioral_assessment=behavioral_assessment,
            motor_assessment=motor_assessment,
            social_assessment=social_assessment,
            follow_up_frequency=follow_up_frequency,
            next_evaluation_date=next_evaluation_date,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=is_active,
            id=id,
        )
