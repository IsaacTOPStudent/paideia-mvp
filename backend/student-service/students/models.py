from django.db import models

# Create your models here.
class StudentModel(models.Model):

    DOCUMENT_TYPES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Masculino'),
        ('FEMALE', 'Femenino')
    ]

    GRADES = [
        ('Preescolar', 'Preescolar'),
        ('1°', 'Primero'),
        ('2°', 'Segundo'),
        ('3°', 'Tercero'),
        ('4°', 'Cuarto'),
        ('5°', 'Quinto'),
        ('6°', 'Sexto'),
        ('7°', 'Séptimo'),
        ('8°', 'Octavo'),
        ('9°', 'Noveno'),
        ('10°', 'Décimo'),
        ('11°', 'Undécimo'),
    ]

    # Datos personales
    document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    
    # Datos académicos
    grade = models.CharField(max_length=20, choices=GRADES)
    section = models.CharField(max_length=5, null=True, blank=True)
    
    # Datos del acudiente
    guardian_name = models.CharField(max_length=150)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_relationship = models.CharField(max_length=50, null=True, blank=True)
    
    # Consentimiento (RN-08)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    
    # Datos opcionales
    address = models.CharField(max_length=255, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    socioeconomic_stratum = models.IntegerField(null=True, blank=True)
    
    # Metadatos
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['first_name', 'last_name'])
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.document_number})"
