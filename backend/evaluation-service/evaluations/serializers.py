from rest_framework import serializers
from typing import Any, Optional, Union, cast
from datetime import date

from src.domain.entities.psychological_evaluation import (
    PsychologicalEvaluation,
    FollowUpFrequency,
    FollowUpStatus,
)
from src.domain.entities.academic_observation import (
    AcademicObservation,
    Subject,
)

class BaseDomainSerializer(serializers.Serializer):
    def get_field_value(
        self,
        obj: Union[object, dict],
        field: str,
        default: Any = None
    ) -> Any:
        if isinstance(obj, dict):
            return obj.get(field, default)
        return getattr(obj, field, default)
    
# Psychologic evaluations
    
class PsychologicalEvaluationRegisterSerializer(BaseDomainSerializer):
    student_id = serializers.IntegerField()
    evaluation_date = serializers.DateField()
    instrument_used = serializers.CharField(max_length=255, min_length=3)
    findings = serializers.CharField(min_length=10)
    recommendations = serializers.CharField(min_length=10)

    cognitive_assessment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    emotional_assessment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    behavioral_assessment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    motor_assessment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    social_assessment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    follow_up_frequency = serializers.ChoiceField(
        choices=["MONTHLY", "QUARTERLY", "BIANNUAL", "ANNUAL"]
    )
    next_evaluation_date = serializers.DateField()

    def validate(self, attrs):
        evaluation_date = attrs.get("evaluation_date")
        next_date = attrs.get("next_evaluation_date")

        if evaluation_date and next_date and next_date <= evaluation_date:
            raise serializers.ValidationError({
                "next_evaluation_date": (
                    "La fecha de próxima evaluación debe ser posterior a la fecha de evaluación"
                )
            })
        
        if next_date and next_date < date.today():
            raise serializers.ValidationError({ 
                "next_evaluation_date": (
                    "La proxima fecha de evaluación no puede ser anterior a hoy"
                )
            })
        
        assessment_areas = [
            attrs.get("cognitive_assessment"),
            attrs.get("emotional_assessment"),
            attrs.get("behavioral_assessment"),
            attrs.get("motor_assessment"),
            attrs.get("social_assessment"),
        ]

        if not any(
            area and str(area).strip()
            for area in assessment_areas
        ):
            raise serializers.ValidationError({
                "assessment": (
                    "Debe registrar al menos un área evaluada."
                )
            })
            
        return attrs
    
class PsychologicalEvaluationResponseSerializer(BaseDomainSerializer):

    id = serializers.IntegerField(read_only=True)
    student_id = serializers.IntegerField()
    psychologist_id = serializers.IntegerField()

    evaluation_date = serializers.DateField()
    instrument_used = serializers.CharField()
    findings = serializers.CharField()
    recommendations = serializers.CharField()

    cognitive_assessment = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    emotional_assessment = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    behavioral_assessment = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    motor_assessment = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    social_assessment = serializers.CharField(
        allow_blank=True, allow_null=True
    )

    follow_up_frequency = serializers.CharField()
    next_evaluation_date = serializers.DateField()

    follow_up_frequency_display = serializers.SerializerMethodField()
    follow_up_status = serializers.SerializerMethodField()
    follow_up_status_display = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_next_evaluation = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        frequency = self.get_field_value(instance, "follow_up_frequency")
        if hasattr(frequency, "value"):
            data["follow_up_frequency"] = frequency.value
        return data
    
    def get_follow_up_frequency_display(
        self,
        obj: Union[PsychologicalEvaluation, dict]
    ) -> str:
        frequency = self.get_field_value(obj, "follow_up_frequency")

        if isinstance(frequency, FollowUpFrequency):
            return frequency.to_spanish()

        if isinstance(frequency, str):
            try:
                return FollowUpFrequency.from_string(frequency).to_spanish()
            except ValueError:
                return frequency

        return str(frequency)
    
    def get_follow_up_status(
        self,
        obj: Union[PsychologicalEvaluation, dict]
    ) -> str:
        if isinstance(obj, PsychologicalEvaluation):
            return obj.follow_up_status.value

        next_date = self.get_field_value(obj, "next_evaluation_date")
        if next_date and date.today() > next_date:
            return FollowUpStatus.PENDING.value
        return FollowUpStatus.UP_TO_DATE.value
    
    def get_follow_up_status_display(
        self,
        obj: Union[PsychologicalEvaluation, dict]
    ) -> str:
        if isinstance(obj, PsychologicalEvaluation):
            return obj.follow_up_status.to_spanish()

        next_date = self.get_field_value(obj, "next_evaluation_date")
        if next_date and date.today() > next_date:
            return FollowUpStatus.PENDING.to_spanish()
        return FollowUpStatus.UP_TO_DATE.to_spanish()
    
    def get_is_overdue(
        self,
        obj: Union[PsychologicalEvaluation, dict]
    ) -> bool:
        if isinstance(obj, PsychologicalEvaluation):
            return obj.is_overdue

        next_date = self.get_field_value(obj, "next_evaluation_date")
        if next_date:
            return date.today() > next_date
        return False
    
    def get_days_until_next_evaluation(
        self,
        obj: Union[PsychologicalEvaluation, dict]
    ) -> Optional[int]:
        if isinstance(obj, PsychologicalEvaluation):
            return obj.days_until_next_evaluation

        next_date = self.get_field_value(obj, "next_evaluation_date")
        if next_date:
            return (next_date - date.today()).days
        return None

# Academic observations

class AcademicObservationRegisterSerializer(BaseDomainSerializer):

    student_id = serializers.IntegerField()
    observation_date = serializers.DateField()
    subject = serializers.ChoiceField(
        choices=[
            "MATH", "SPANISH", "SCIENCE", "SOCIAL_STUDIES",
            "ARTS", "PHYSICAL_EDUCATION", "ENGLISH", "OTHER"
        ]
    )
    performance_description = serializers.CharField(min_length=10)


    behavioral_notes = serializers.CharField(min_length=10)
    pedagogical_adjustments_applied = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, min_length=5
    )
    recommendations = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, min_length=5
    )

    def validate(self, attrs):
        observation_date = attrs.get("observation_date")

        if observation_date and observation_date > date.today():
            raise serializers.ValidationError({
                "observation_date": (
                    "La fecha de observación no puede ser futura"
                )
            })
        
        return attrs

class AcademicObservationResponseSerializer(BaseDomainSerializer):
    id = serializers.IntegerField(read_only=True)
    student_id = serializers.IntegerField()
    teacher_id = serializers.IntegerField()

    observation_date = serializers.DateField()
    subject = serializers.CharField()
    performance_description = serializers.CharField()

    behavioral_notes = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    pedagogical_adjustments_applied = serializers.CharField(
        allow_blank=True, allow_null=True
    )
    recommendations = serializers.CharField(
        allow_blank=True, allow_null=True
    )

    subject_display = serializers.SerializerMethodField()

    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        subject = self.get_field_value(instance, "subject")
        if hasattr(subject, "value"):
            data["subject"] = subject.value
        return data

    def get_subject_display(
        self,
        obj: Union[AcademicObservation, dict]
    ) -> str:
        subject = self.get_field_value(obj, "subject")

        if isinstance(subject, Subject):
            return subject.to_spanish()

        if isinstance(subject, str):
            try:
                return Subject.from_string(subject).to_spanish()
            except ValueError:
                return subject

        return str(subject)
    
    
# Longitudinal History

class LongitudinalHistorySerializer(BaseDomainSerializer):

    student_id = serializers.IntegerField()

    student_info = serializers.DictField()
    characterizations = serializers.ListField()
    has_records = serializers.BooleanField()

    follow_up_status = serializers.CharField()
    days_until_next_evaluation = serializers.IntegerField(allow_null=True)

    evaluations = serializers.SerializerMethodField()
    observations = serializers.SerializerMethodField()

    total_evaluations = serializers.IntegerField()
    total_observations = serializers.IntegerField()

    def get_evaluations(self, obj) -> list:

        evaluations = self.get_field_value(obj, "evaluations", [])
        serializer = PsychologicalEvaluationResponseSerializer(
            evaluations, many=True
        )
        return cast(list[Any], serializer.data)

    def get_observations(self, obj) -> list:
        observations = self.get_field_value(obj, "observations", [])
        serializer = AcademicObservationResponseSerializer(
            observations, many=True
        )
        return cast(list[Any], serializer.data)
    
    