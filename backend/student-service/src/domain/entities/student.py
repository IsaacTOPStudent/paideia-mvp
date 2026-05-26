from dataclasses import dataclass
from datetime import date, datetime 
from typing import Optional
from enum import Enum

class Gender(Enum):
    """
        Student gender
    """
    MALE = "MALE"
    FEMALE = "FEMALE"

    @classmethod
    def from_string(cls, value: str):
        if not value:
            raise ValueError("Genero requerido")

        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Genero inválido: {value}")

@dataclass
class Student:
    """
        NEE Student
    """

    # Personal data
    document_type: str #cc, ti, ce
    document_number: str #Unique
    first_name: str 
    last_name: str 
    date_of_birth: date 
    gender: Gender

    # Academic data
    grade: str
    section: Optional[str] 

    # Guardian's information
    guardian_name: str 
    guardian_phone: str 
    guardian_email: Optional[str]
    guardian_relationship: Optional[str]

    # Consent
    consent_date: Optional[datetime]
    consent_given: bool 

    #Optional data
    address: Optional[str]
    neighborhood: Optional[str]
    city: Optional[str]
    socioeconomic_stratum: Optional[int]

    # Metadata
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    id: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.gender, str):
            self.gender = Gender.from_string(self.gender)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def is_minor(self) -> bool:
        return self.age < 18
    
    def has_valid_consent(self) -> bool:
        return self.consent_given and self.consent_date is not None
    
    def validate_for_registration(self) -> tuple[bool, list[str]]:
        """
            RN-03: Validate that the profile is complete
        """
        missing = []

        if not self.document_number or not self.document_number.strip():
            missing.append('document_number')
        if not self.first_name or not self.first_name.strip():
            missing.append('first_name')
        if not self.last_name or not self.last_name.strip():
            missing.append('last_name')
        if not self.date_of_birth:
            missing.append('date_of_birth')
        if not self.gender:
            missing.append('gender')
        if not self.grade:
            missing.append('grade')
        if not self.guardian_name or not self.guardian_name.strip():
            missing.append('guardian_name')
        if not self.guardian_phone or not self.guardian_phone.strip():
            missing.append('guardian_phone')
        if not self.consent_given:
            missing.append('consent_given')

        return (len(missing) == 0, missing)
    
    def validate_for_characterization(self) -> bool:
        is_valid, _ = self.validate_for_registration()
        return is_valid and self.is_active

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()

    def update_data(
        self,
        first_name: str,
        last_name: str,
        grade: str,
        section: Optional[str],
        guardian_name: str,
        guardian_phone: str,
        guardian_email: Optional[str],
        guardian_relationship: Optional[str],
        address: Optional[str],
        neighborhood: Optional[str],
        city: Optional[str],
        socioeconomic_stratum: Optional[int]
    ) -> None:

        self.first_name = first_name.strip()
        self.last_name = last_name.strip()

        self.grade = grade
        self.section = section

        self.guardian_name = guardian_name.strip()
        self.guardian_phone = guardian_phone.strip()

        self.guardian_email = guardian_email
        self.guardian_relationship = guardian_relationship

        self.address = address
        self.neighborhood = neighborhood
        self.city = city
        self.socioeconomic_stratum = socioeconomic_stratum

        self.updated_at = datetime.now()

    def __str__(self):
        return f"Student({self.document_number}, {self.full_name}, Grado {self.grade})"