from typing import Optional, List
from django.utils import timezone

from evaluations.models import PsychologicalEvaluationModel
from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation,
    FollowUpFrequency,
)
from src.domain.ports.psychological_evaluation_repository import (
    PsychologicalEvaluationRepository,
)

class DjangoEvaluationRepository(PsychologicalEvaluationRepository):
    def save(self, evaluation: PsychologicalEvaluation) -> PsychologicalEvaluation:
        psychological_evaluation_data = {
            "instrument_used": evaluation.instrument_used,
            "findings": evaluation.findings,
            "recommendations": evaluation.recommendations,
            "cognitive_assessment": evaluation.cognitive_assessment,
            "emotional_assessment": evaluation.emotional_assessment,
            "behavioral_assessment": evaluation.behavioral_assessment,
            "motor_assessment": evaluation.motor_assessment,
            "social_assessment": evaluation.social_assessment,
            "follow_up_frequency": evaluation.follow_up_frequency.value,
            "next_evaluation_date": evaluation.next_evaluation_date,
            "is_active": evaluation.is_active,
        }

        if evaluation.id: 
            obj = PsychologicalEvaluationModel.objects.get(id=evaluation.id)
            for key, value in psychological_evaluation_data.items():
                setattr(obj, key, value)

            obj.updated_at = timezone.now()
            obj.save()

        else:
            creation_data = {
                **psychological_evaluation_data,
                "student_id": evaluation.student_id,
                "psychologist_id": evaluation.psychologist_id,
                "evaluation_date": evaluation.evaluation_date,
            }

            obj = PsychologicalEvaluationModel.objects.create(**creation_data)
            evaluation.id = obj.pk

        return self._to_entity(obj)
    
    def find_by_id(self, evaluation_id: int) -> Optional[PsychologicalEvaluation]:
        try:
            obj = PsychologicalEvaluationModel.objects.get(id=evaluation_id)
            return self._to_entity(obj)
        
        except PsychologicalEvaluationModel.DoesNotExist:
            return None
        
    def find_by_student(self, student_id: int) -> List[PsychologicalEvaluation]:
        qs = PsychologicalEvaluationModel.objects.filter(
            student_id=student_id
        ).order_by("-evaluation_date")
        return [self._to_entity(obj) for obj in qs]
    
    def find_active_by_student(self, student_id: int) -> List[PsychologicalEvaluation]:
        qs = PsychologicalEvaluationModel.objects.filter(
            student_id=student_id,
            is_active=True
        ).order_by("-evaluation_date")
        return [self._to_entity(obj) for obj in qs]
    
    def find_latest_by_student(self, student_id: int) -> Optional[PsychologicalEvaluation]:
        try:
            obj = PsychologicalEvaluationModel.objects.filter(
                student_id=student_id,
                is_active=True
            ).latest("evaluation_date")
            return self._to_entity(obj)
        except PsychologicalEvaluationModel.DoesNotExist:
            return None
        
    def has_evaluations(self, student_id: int) -> bool:
        return PsychologicalEvaluationModel.objects.filter(
            student_id=student_id
        ).exists()
    
    @staticmethod
    def _to_entity(model: PsychologicalEvaluationModel) -> PsychologicalEvaluation:
        return PsychologicalEvaluation(
            id=model.pk,
            student_id=model.student_id,
            psychologist_id=model.psychologist_id,
            evaluation_date=model.evaluation_date,
            instrument_used=model.instrument_used,
            findings=model.findings,
            recommendations=model.recommendations,
            cognitive_assessment=model.cognitive_assessment,
            emotional_assessment=model.emotional_assessment,
            behavioral_assessment=model.behavioral_assessment,
            motor_assessment=model.motor_assessment,
            social_assessment=model.social_assessment,
            follow_up_frequency=FollowUpFrequency.from_string(model.follow_up_frequency),
            next_evaluation_date=model.next_evaluation_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )