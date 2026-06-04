from typing import Optional, List
from django.utils import timezone

from evaluations.models import AcademicObservationModel

from src.domain.entities.academic_observation import AcademicObservation, Subject
from src.domain.ports.academic_observation_repository import AcademicObservationRepository

class DjangoObservationRepository(AcademicObservationRepository):

    def save(self, observation: AcademicObservation) -> AcademicObservation:
        academic_observation_data = {
            "performance_description": observation.performance_description,
            "behavioral_notes": observation.behavioral_notes,
            "pedagogical_adjustments_applied": observation.pedagogical_adjustments_applied,
            "recommendations": observation.recommendations,
            "is_active": observation.is_active
        }

        if observation.id:
            obj = AcademicObservationModel.objects.get(id=observation.id)
            for key, value in academic_observation_data.items():
                setattr(obj, key, value)

            obj.updated_at = timezone.now()
            obj.save()

        else:
            creation_data = {
                **academic_observation_data,
                "student_id": observation.student_id,
                "teacher_id": observation.teacher_id,
                "observation_date": observation.observation_date,
                "subject": observation.subject.value
            }
            obj = AcademicObservationModel.objects.create(**creation_data)
            observation.id = obj.pk

        return self._to_entity(obj)
    
    def find_by_id(self, observation_id: int) -> Optional[AcademicObservation]:
        try:
            obj = AcademicObservationModel.objects.get(id=observation_id)
            return self._to_entity(obj)
        except AcademicObservationModel.DoesNotExist:
            return None
        
    def find_by_student(self, student_id: int) -> List[AcademicObservation]:
        qs = AcademicObservationModel.objects.filter(
            student_id=student_id
        ).order_by("-observation_date")
        return [self._to_entity(obj) for obj in qs]
    
    def find_active_by_student(self, student_id: int) -> List[AcademicObservation]:
        qs = AcademicObservationModel.objects.filter(
            student_id=student_id,
            is_active=True
        ).order_by("-observation_date")
        return [self._to_entity(obj) for obj in qs]
    
    def find_by_student_and_teacher(
        self,
        student_id: int,
        teacher_id: int
    ) -> List[AcademicObservation]:
        qs = AcademicObservationModel.objects.filter(
            student_id=student_id,
            teacher_id=teacher_id,
            is_active=True
        ).order_by("-observation_date")
        return [self._to_entity(obj) for obj in qs]
    
    @staticmethod
    def _to_entity(model: AcademicObservationModel) -> AcademicObservation:
        return AcademicObservation(
            id=model.pk,
            student_id=model.student_id,
            teacher_id=model.teacher_id,
            observation_date=model.observation_date,
            subject=Subject.from_string(model.subject),
            performance_description=model.performance_description,
            behavioral_notes=model.behavioral_notes,
            pedagogical_adjustments_applied=model.pedagogical_adjustments_applied,
            recommendations=model.recommendations,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )