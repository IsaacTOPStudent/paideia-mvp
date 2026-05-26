from django.utils import timezone
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum 

class NEECategory(Enum):
    """
       Special Educational Needs (SEN) categories according to Decree 1421/2017 and Law 2216/2022 (RN-16) 
    """
    PHYSICAL_DISABILITY = "PHYSICAL_DISABILITY"
    SENSORY_VISUAL = "SENSORY_VISUAL"
    SENSORY_AUDITORY = "SENSORY_AUDITORY"
    COGNITIVE_DISABILITY = "COGNITIVE_DISABILITY"
    PSYCHOSOCIAL_DISABILITY = "PSYCHOSOCIAL_DISABILITY"
    MULTIPLE_DISABILITY = "MULTIPLE_DISABILITY"
    SPECIFIC_LEARNING_DISORDER = "SPECIFIC_LEARNING_DISORDER"
    ADHD = "ADHD"
    AUTISM_SPECTRUM = "AUTISM_SPECTRUM"
    GIFTEDNESS = "GIFTEDNESS"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Categoría inválida: {value}")
        

    def to_spanish(self) -> str:
        """Convertir a español (RNF-07)"""
        translations = {
            'PHYSICAL_DISABILITY': 'Discapacidad Física',
            'SENSORY_VISUAL': 'Discapacidad Sensorial Visual',
            'SENSORY_AUDITORY': 'Discapacidad Sensorial Auditiva',
            'COGNITIVE_DISABILITY': 'Discapacidad Cognitiva',
            'PSYCHOSOCIAL_DISABILITY': 'Discapacidad Psicosocial',
            'MULTIPLE_DISABILITY': 'Discapacidad Múltiple',
            'SPECIFIC_LEARNING_DISORDER': 'Trastorno Específico del Aprendizaje',
            'ADHD': 'TDAH',
            'AUTISM_SPECTRUM': 'Trastorno del Espectro Autista (TEA)',
            'GIFTEDNESS': 'Superdotación',
        }
        return translations.get(self.name, self.name)
    

@dataclass
class Diagnostic:
    """
        - Management of the Special Educational Needs (SEN) catalog (RF-05, CU-09)
        - Alignment with Colombian regulations (RN-16)
        - Control of active diagnoses (RN-05)
    """

    id: Optional[int]
    code: str  # Código único institucional
    name: str
    category: NEECategory
    description: str
    normative_reference: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):

        self.code = self.code.upper().strip()

        self.name = self.name.strip()

        if isinstance(self.category, str):
            self.category = NEECategory.from_string(self.category)

        if self.created_at is None:
            self.created_at = timezone.now()

        if self.updated_at is None:
            self.updated_at = timezone.now()

    def validate(self) -> tuple[bool, list[str]]:
        """
            Validate entity integrity before persistence
        """
        errors = []

        if not self.code:
            errors.append("code")
        
        if not self.name:
            errors.append("name")

        if not self.description or not self.description.strip():
            errors.append("description")

        if not isinstance(self.category, NEECategory):
            errors.append("category")

        return (len(errors) == 0, errors)

    def can_be_used(self) -> bool:
        """
        Only active diagnostics can be used
        in characterization forms.
        """
        return self.is_active
        
    def deactivate(self) -> None:
        """Deactivate without deleting historical records"""
        self.is_active = False
        self.updated_at = timezone.now()
        
    def reactivate(self) -> None:
        """Reactivate diagnostic"""
        self.is_active = True
        self.updated_at = timezone.now()
        
    def __str__(self):
        return (
            f"DiagnosticCatalog("
            f"code={self.code}, "
            f"name={self.name}, "
            f"category={self.category.value}, "
            f"active={self.is_active}"
            f")"
        )