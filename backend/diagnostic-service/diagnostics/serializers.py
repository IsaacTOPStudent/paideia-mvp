from rest_framework import serializers
from typing import Any, Optional, Union

from src.domain.entities.characterization import Characterization, SeverityLevel
from src.domain.entities.diagnostic_catalog import Diagnostic, NEECategory

class BaseDomainSerializer(serializers.Serializer):
    def get_field_value(self, obj: Union[object, dict ], field: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(field, default)
        
        return getattr(obj, field, default)

class DiagnosticSerializer(BaseDomainSerializer):

    id = serializers.IntegerField(read_only=True)

    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=50)

    description = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    normative_reference = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    is_active = serializers.BooleanField()
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    category_display = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)

        category = self.get_field_value(instance, "category")

        if hasattr(category, "value"):
            data["category"] = category.value

        return data
    

    def get_category_display(self, obj: Union[Diagnostic, dict]) -> str:
        category = self.get_field_value(obj, "category")

        if isinstance(category, NEECategory):
            return category.to_spanish()
        
        if isinstance(category, str):
            try:
                return NEECategory.from_string(category).to_spanish()
            
            except ValueError:
                return category
            
        return str(category)

class DiagnosticUpdateSerializer(BaseDomainSerializer):

    code = serializers.CharField(max_length=50, required=False)

    name = serializers.CharField(max_length=255, required=False)

    category = serializers.CharField(max_length=50, required=False)

    description = serializers.CharField(required=False)

    normative_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    updated_at = serializers.DateTimeField(read_only=True)

class CharacterizationSerializer(BaseDomainSerializer):
    id = serializers.IntegerField(read_only=True)
    student_id = serializers.IntegerField()
    diagnostic_id = serializers.IntegerField()
    
    severity_level = serializers.CharField()
    identification_date = serializers.DateField(allow_null=True)
    
    observations = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    cognitive_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    communicative_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    socioemotional_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    motor_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    sensory_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    academic_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    behavioral_area_notes = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.IntegerField(read_only=True, allow_null=True)
    
    severity_level_display = serializers.SerializerMethodField()
    diagnostic_name = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)

        severity_level = self.get_field_value(instance, "severity_level")

        if hasattr(severity_level, "value"):
            data["severity_level"] = severity_level.value

        return data

    def get_severity_level_display(self, obj: Union[Characterization, dict]) -> str:
        if isinstance(obj, Characterization):
            return obj.severity_in_spanish
        
        severity_level = self.get_field_value(obj, "severity_level")

        if isinstance(severity_level, SeverityLevel):
            return severity_level.to_spanish()
        
        if isinstance(severity_level, str):
            try:
                return SeverityLevel.from_string(
                    severity_level
                ).to_spanish()
            
            except ValueError:
                return severity_level
            
        return str(severity_level)
    
    def get_diagnostic_name(self, obj: Union[Characterization, dict]) -> Optional[str]:

        diagnostic_name = self.get_field_value(
            obj, "diagnostic_name"
        )

        if diagnostic_name:
            return diagnostic_name
        
        diagnostic = self.get_field_value(obj, "diagnostic")

        if not diagnostic:
            return None 
        
        if isinstance(diagnostic, dict):
            return diagnostic.get("name")
        
        return getattr(diagnostic, "name", None)
    
            