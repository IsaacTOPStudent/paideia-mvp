from dataclasses import dataclass

@dataclass
class StudentInfoDTO:
    id: int
    first_name: str
    last_name: str
    document_number: str
    is_active: bool