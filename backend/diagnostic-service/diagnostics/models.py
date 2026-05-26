from django.db import models

# Create your models here.
class DiagnosticModel(models.Model):
    """Modelo del Catálogo de Diagnósticos"""
    
    CATEGORIES = [
        ('PHYSICAL_DISABILITY', 'Discapacidad Física'),
        ('SENSORY_VISUAL', 'Discapacidad Sensorial Visual'),
        ('SENSORY_AUDITORY', 'Discapacidad Sensorial Auditiva'),
        ('COGNITIVE_DISABILITY', 'Discapacidad Cognitiva'),
        ('PSYCHOSOCIAL_DISABILITY', 'Discapacidad Psicosocial'),
        ('MULTIPLE_DISABILITY', 'Discapacidad Múltiple'),
        ('SPECIFIC_LEARNING_DISORDER', 'Trastorno Específico del Aprendizaje'),
        ('ADHD', 'TDAH'),
        ('AUTISM_SPECTRUM', 'Trastorno del Espectro Autista (TEA)'),
        ('GIFTEDNESS', 'Superdotación'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    description = models.TextField()
    normative_reference = models.CharField(max_length=200, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'diagnostic_catalog'
        verbose_name = 'Diagnóstico del Catálogo'
        verbose_name_plural = 'Diagnósticos del Catálogo'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['category']),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class CharacterizationModel(models.Model):
    SEVERITY_LEVELS = [
        ('MILD', 'Leve'),
        ('MODERATE', 'Moderado'),
        ('SEVERE', 'Severo'),
    ]
    
    student_id = models.IntegerField()  # FK a student-service
    diagnostic = models.ForeignKey(
        DiagnosticModel,
        on_delete=models.PROTECT,  # No se puede eliminar el diagnóstico
        related_name='characterizations'
    )
    
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    identification_date = models.DateField()
    observations = models.TextField(null=True, blank=True)
    
    # Áreas evaluadas
    cognitive_area_notes = models.TextField(null=True, blank=True)
    communicative_area_notes = models.TextField(null=True, blank=True)
    socioemotional_area_notes = models.TextField(null=True, blank=True)
    motor_area_notes = models.TextField(null=True, blank=True)
    sensory_area_notes = models.TextField(null=True, blank=True)
    academic_area_notes = models.TextField(null=True, blank=True)
    behavioral_area_notes = models.TextField(null=True, blank=True)
    
    # Control (RN-06: no se elimina)
    is_active = models.BooleanField(default=True)
    created_by = models.IntegerField()  # ID del psicólogo
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'characterizations'
        verbose_name = 'Caracterización'
        verbose_name_plural = 'Caracterizaciones'
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['student_id', 'is_active'])
        ]

    def __str__(self):
        return f"Characterization(Student:{self.student_id}, Diagnostic:{self.diagnostic.code})"
