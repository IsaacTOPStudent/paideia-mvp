from src.domain.dto.student_info import StudentInfoDTO


class StudentFactory:
    @staticmethod
    def build(
        id: int = 1,
        first_name: str = "Juan",
        last_name: str = "Perez",
        document_number: str = "12345678",
        is_active: bool = True,
    ) -> StudentInfoDTO:
        return StudentInfoDTO(
            id=id,
            first_name=first_name,
            last_name=last_name,
            document_number=document_number,
            is_active=is_active,
        )
