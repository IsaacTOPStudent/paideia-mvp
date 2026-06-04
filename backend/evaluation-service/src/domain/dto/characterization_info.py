from dataclasses import dataclass

@dataclass
class CharacterizationInfoDTO:
    id: int
    student_id: int
    diagnostic_id: int
    diagnostic_name: str
    nee_category: str  # PHYSICAL_DISABILITY, SENSORY_VISUAL, etc.
    severity_level: str  # MILD, MODERATE, SEVERE
    identification_date: str
    is_active: bool
