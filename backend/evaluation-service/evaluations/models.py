from django.db import models

# Create your models here.

class PsychologicalEvaluationModel(models.Model):

    FOLLOW_UP_FREQUENCY_CHOICES = [
        ("MONTHLY", "Mensual"),
        ("QUARTERLY", "Trimestral"),
        ("BIANNUAL", "Semestral"),
        ("ANNUAL", "Anual"),
    ]

    student_id = models.IntegerField(db_index=True)
    psychologist_id = models.IntegerField(db_index=True)

    evaluation_date = models.DateField()
    instrument_used = models.CharField(max_length=255)
    findings = models.TextField()
    recommendations = models.TextField()

    cognitive_assessment = models.TextField(null=True, blank=True)
    emotional_assessment = models.TextField(null=True, blank=True)
    behavioral_assessment = models.TextField(null=True, blank=True)
    motor_assessment = models.TextField(null=True, blank=True)
    social_assessment = models.TextField(null=True, blank=True)

    follow_up_frequency = models.CharField(
        max_length=20,
        choices=FOLLOW_UP_FREQUENCY_CHOICES
    )
    next_evaluation_date = models.DateField()

    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'psychological_evaluations'
        verbose_name = "Evaluación Psicológica"
        verbose_name_plural = "Evaluaciones Psicológicas"
        indexes = [
            models.Index(fields=["student_id", "is_active"]),
            models.Index(fields=["student_id", "evaluation_date"]),
            models.Index(fields=["next_evaluation_date"]),
        ]
        ordering = ["-evaluation_date"]

    def __str__(self):
        return (
            f"Evaluación Psicológica "
            f"(Estudiante: {self.student_id}, "
            f"Fecha: {self.evaluation_date})"
        )
    
class AcademicObservationModel(models.Model):
    SUBJECT_CHOICES = [
        ("MATH", "Matemáticas"),
        ("SPANISH", "Español"),
        ("SCIENCE", "Ciencias Naturales"),
        ("SOCIAL_STUDIES", "Ciencias Sociales"),
        ("ARTS", "Artes"),
        ("PHYSICAL_EDUCATION", "Educación Física"),
        ("ENGLISH", "Inglés"),
        ("OTHER", "Otra"),
    ]

    student_id = models.IntegerField(db_index=True)
    teacher_id = models.IntegerField(db_index=True)

    observation_date = models.DateField()
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES)
    performance_description = models.TextField()

    behavioral_notes = models.TextField()
    pedagogical_adjustments_applied = models.TextField(null=True, blank=True)
    recommendations = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_observations'
        verbose_name = "Observación Académica"
        verbose_name_plural = "Observaciones Académicas"
        indexes = [
            models.Index(fields=["student_id", "is_active"]),
            models.Index(fields=["student_id", "teacher_id"]),
            models.Index(fields=["observation_date"]),
        ]
        ordering = ["-observation_date"]

    def __str__(self):
        return (
            f"Observación Académica "
            f"(Estudiante: {self.student_id}, "
            f"Materia: {self.subject}, "
            f"Fecha: {self.observation_date})"
        )